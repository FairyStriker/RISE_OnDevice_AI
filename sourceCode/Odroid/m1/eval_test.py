import os
import time
import numpy as np
import cv2
import glob
import json
from rknnlite.api import RKNNLite

# ================= 설정 (Configuration) =================
RKNN_MODEL = './rknn_file/yolov8n_fp16.rknn'   # 사용하시는 모델 파일명
IMG_PATH = './test/images'
LABEL_PATH = './test/labels'
IMG_SIZE = (640, 640)        # 모델 입력 크기
CONF_THRES = 0.25            # 필요하다면 0.001로 낮춰서 테스트 해보세요
IOU_THRES = 0.45             # NMS IoU Threshold
MAX_IMAGES = None            # None으로 설정하면 전체 이미지 검사
OUTPUT_JSON_FILE = 'yolov8n_fp16_rknn_result.json' # 결과 저장 파일명
# =======================================================

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114)):
    """
    이미지 비율을 유지하며 리사이징하고, 남는 공간을 회색(114)으로 채우는 함수
    Returns:
        im: 레터박스 적용된 이미지
        ratio: 축소/확대 비율
        (dw, dh): 양쪽에 들어간 패딩 크기
    """
    shape = im.shape[:2]  # [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # 1. 비율 계산 (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

    # 2. 패딩 계산
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    dw /= 2  # 양쪽으로 나누기 (좌우 또는 상하 균등 분배)
    dh /= 2

    # 3. 리사이징 (비율 유지)
    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)

    # 4. 테두리(패딩) 추가
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)

    return im, r, (dw, dh)

def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    """
    예측된 박스 좌표(640x640 기준)를 원본 이미지(img0) 좌표로 복원하는 함수 (Un-Letterbox)
    """
    if ratio_pad is None:  # 비율 정보가 없으면 계산
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2
    else:
        gain = ratio_pad[0]    # ratio
        pad = ratio_pad[1]     # (dw, dh)

    # 1. 패딩 제거 (좌표 이동)
    coords[:, [0, 2]] -= pad[0]  # x 좌표에서 좌측 패딩(dw) 빼기
    coords[:, [1, 3]] -= pad[1]  # y 좌표에서 상단 패딩(dh) 빼기

    # 2. 스케일 복원 (비율로 나누기)
    coords[:, :4] /= gain

    # 3. 이미지 범위 벗어나는 좌표 클립(Clip)
    coords[:, 0].clip(0, img0_shape[1])  # x1
    coords[:, 1].clip(0, img0_shape[0])  # y1
    coords[:, 2].clip(0, img0_shape[1])  # x2
    coords[:, 3].clip(0, img0_shape[0])  # y2
    return coords

def xywh2xyxy(x):
    # Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2]
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y

def compute_iou(box1, box2):
    # Intersection over Union 계산
    area1 = (box1[:, 2] - box1[:, 0]) * (box1[:, 3] - box1[:, 1])
    area2 = (box2[:, 2] - box2[:, 0]) * (box2[:, 3] - box2[:, 1])

    lt = np.maximum(box1[:, None, :2], box2[:, :2])
    rb = np.minimum(box1[:, None, 2:], box2[:, 2:])
    wh = np.clip(rb - lt, 0, None)
    inter = wh[:, :, 0] * wh[:, :, 1]
    return inter / (area1[:, None] + area2 - inter + 1e-7)

if __name__ == '__main__':
    # 1. RKNN 초기화
    rknn = RKNNLite()
    print("--> Loading RKNN model")
    ret = rknn.load_rknn(RKNN_MODEL)
    if ret != 0:
        print('Load RKNN model failed')
        exit(ret)

    print("--> Init runtime environment")
    ret = rknn.init_runtime()
    if ret != 0:
        print('Init runtime environment failed')
        exit(ret)

    img_files = glob.glob(os.path.join(IMG_PATH, '*.jpg'))
    if MAX_IMAGES: img_files = img_files[:MAX_IMAGES]

    print(f"--> 총 {len(img_files)}장의 이미지로 평가를 시작합니다 (Letterbox Mode)...")

    tp_count = 0
    gt_count = 0
    pred_count = 0

    inference_times = [] # 순수 NPU 시간
    total_times = []     # 전처리+NPU+후처리 시간

    for idx, img_file in enumerate(img_files):
        # 원본 이미지 로드 (이 크기를 기준으로 최종 좌표를 복원해야 함)
        img0 = cv2.imread(img_file)
        if img0 is None: continue

        start_total = time.time()

        # [핵심] 1. 전처리 (Letterbox 적용)
        # img: 640x640 (패딩 포함됨)
        # ratio: 축소 비율
        # pad: (dw, dh) 패딩 크기
        img, ratio, pad = letterbox(img0, new_shape=IMG_SIZE)

        img_input = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_input = np.expand_dims(img_input, 0)

        # 2. NPU 추론
        start_inf = time.time()
        outputs = rknn.inference(inputs=[img_input])
        end_inf = time.time()
        inference_times.append(end_inf - start_inf)

        # 3. 후처리 (Post-processing)
        output = outputs[0][0]
        if output.shape[0] < output.shape[1]: output = output.T # (8400, 84)

        boxes = output[:, :4]
        scores = output[:, 4:]
        max_scores = np.max(scores, axis=1)

        # Threshold Filtering
        mask = max_scores > CONF_THRES
        boxes = boxes[mask]
        max_scores = max_scores[mask]

        preds = []
        if len(boxes) > 0:
            boxes = xywh2xyxy(boxes) # xyxy로 변환 (아직 640좌표계)

            # NMS 수행
            indices = cv2.dnn.NMSBoxes(boxes.tolist(), max_scores.tolist(), CONF_THRES, IOU_THRES)

            if len(indices) > 0:
                # NMS 통과한 박스만 선택
                det_boxes = boxes[indices.flatten()]

                # [핵심] 4. 좌표 복원 (Un-Letterbox)
                # 640x640 좌표 -> 원본 이미지 좌표로 변환
                # 패딩을 빼고, 비율만큼 늘려줌
                det_boxes = scale_coords(IMG_SIZE, det_boxes, img0.shape, ratio_pad=(ratio, pad))

                for box in det_boxes:
                    preds.append(box.tolist()) # [x1, y1, x2, y2]

        end_total = time.time()
        total_times.append(end_total - start_total)

        # --- 평가(Evaluation) 로직 ---
        pred_count += len(preds)

        # 정답(GT) 파일 로드
        txt_path = img_file.replace('images', 'labels').replace('.jpg', '.txt')
        gts = []
        if os.path.exists(txt_path):
            h_org, w_org = img0.shape[:2]
            with open(txt_path) as f:
                for line in f:
                    p = list(map(float, line.strip().split()))
                    # 정규화된 좌표 -> 원본 픽셀 좌표
                    x, y, w, h = p[1], p[2], p[3], p[4]
                    x1 = (x - w/2) * w_org
                    y1 = (y - h/2) * h_org
                    x2 = (x + w/2) * w_org
                    y2 = (y + h/2) * h_org
                    gts.append([x1, y1, x2, y2])
        gt_count += len(gts)

        # IoU 매칭 (채점)
        matched = 0
        if len(preds) > 0 and len(gts) > 0:
            iou_mat = compute_iou(np.array(preds), np.array(gts))
            # 각 예측박스마다 가장 높은 IoU를 가진 GT가 0.5 이상인지 확인
            matched = np.sum(np.max(iou_mat, axis=1) > 0.5)
            tp_count += matched

        if idx % 10 == 0 or matched > 0:
            print(f"[{idx+1}/{len(img_files)}] {os.path.basename(img_file)}: 매칭 {matched}개 (FPS: {1.0/(end_total-start_total):.1f})")

    # ================= 결과 계산 및 출력 =================
    precision = tp_count / (pred_count + 1e-7)
    recall = tp_count / (gt_count + 1e-7)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-7)

    avg_inf_time = np.mean(inference_times)
    avg_total_time = np.mean(total_times)

    inf_fps = 1.0 / avg_inf_time
    total_fps = 1.0 / avg_total_time

    print("\n" + "="*40)
    print(f" [최종 결과 리포트 - Letterbox 적용됨] ")
    print(f" 검사 이미지 수: {len(img_files)}")
    print("-" * 40)
    print(f" 정밀도(Precision): {precision:.4f}")
    print(f" 재현율(Recall):    {recall:.4f}")
    print(f" F1 Score:         {f1:.4f}")
    print("-" * 40)
    print(f" 순수 추론 시간 (NPU): {avg_inf_time*1000:.2f} ms")
    print(f" 순수 추론 FPS (NPU):  {inf_fps:.2f} FPS")
    print("-" * 40)
    print(f" 전체 처리 시간 (Total): {avg_total_time*1000:.2f} ms")
    print(f" 전체 처리 FPS (Total):  {total_fps:.2f} FPS")
    print("="*40)

    # JSON 저장
    results = {
        "model": RKNN_MODEL,
        "images": len(img_files),
        "metrics": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4)
        },
        "performance": {
            "inference_fps": round(inf_fps, 2),
            "total_fps": round(total_fps, 2),
            "inference_ms": round(avg_inf_time * 1000, 2)
        }
    }

    try:
        with open(OUTPUT_JSON_FILE, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"--> 결과 파일 저장 완료: {OUTPUT_JSON_FILE}")
    except Exception as e:
        print(f"--> JSON 저장 실패: {e}")

    rknn.release()

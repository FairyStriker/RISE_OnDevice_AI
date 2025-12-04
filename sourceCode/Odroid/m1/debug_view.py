import cv2
import numpy as np
from rknnlite.api import RKNNLite

# ================= 설정 =================
RKNN_MODEL = './rknn_file/yolov8l_fp16.rknn'   # 사용중인 모델 파일명
TEST_IMG = '/home/odroid/ssj/test/images/human_2862.jpg' # 테스트할 이미지 경로 (아무거나 1장 지정해주세요)
IMG_SIZE = (640, 640)
CONF_THRES = 0.2
# =======================================

def xywh2xyxy(x):
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2
    y[..., 1] = x[..., 1] - x[..., 3] / 2
    y[..., 2] = x[..., 0] + x[..., 2] / 2
    y[..., 3] = x[..., 1] + x[..., 3] / 2
    return y

# RKNN 로드
rknn = RKNNLite()
rknn.load_rknn(RKNN_MODEL)
rknn.init_runtime()

# 이미지 준비
img = cv2.imread(TEST_IMG)
if img is None:
    print("이미지를 찾을 수 없습니다 경로를 확인하세요.")
    exit()

img_input = cv2.resize(img, IMG_SIZE)
img_input = cv2.cvtColor(img_input, cv2.COLOR_BGR2RGB) # RGB 변환
img_input = np.expand_dims(img_input, 0)

# 추론
print("--> Inference Start")
outputs = rknn.inference(inputs=[img_input])

# ================= [디버깅 구간] =================
output = outputs[0]
output = np.squeeze(output)

print(f"1. Raw Output Shape: {output.shape}")

# Transpose 체크
if output.shape[0] < output.shape[1]:
    output = output.T
    print(f"2. Transposed Shape: {output.shape}")

# 점수 확인
scores = output[:, 4:] # 4번째 이후가 클래스 점수
max_scores = np.max(scores, axis=1)
print(f"3. Max Confidence Score: {np.max(max_scores):.4f}")
print(f"   (이 값이 {CONF_THRES}보다 작으면 박스가 안 그려집니다)")

# 박스 그리기
boxes = output[:, :4]
boxes = xywh2xyxy(boxes)
indices = cv2.dnn.NMSBoxes(boxes.tolist(), max_scores.tolist(), CONF_THRES, 0.45)

print(f"4. Detected Boxes: {len(indices)}")

if len(indices) > 0:
    scale_x = img.shape[1] / IMG_SIZE[0]
    scale_y = img.shape[0] / IMG_SIZE[1]

    for i in indices.flatten():
        box = boxes[i]
        x1 = int(box[0] * scale_x)
        y1 = int(box[1] * scale_y)
        x2 = int(box[2] * scale_x)
        y2 = int(box[3] * scale_y)

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        score = max_scores[i]
        cv2.putText(img, f"{score:.2f}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    cv2.imwrite("result_debug.jpg", img)
    print("--> 'result_debug.jpg' 저장 완료! 확인해보세요.")
else:
    print("--> 검출된 박스가 없습니다.")

rknn.release()

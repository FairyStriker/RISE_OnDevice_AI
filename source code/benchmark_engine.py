import os
import time
import json
import cv2
import platform
from ultralytics import YOLO
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# --- ⚙️ 1. Jetson 사용자 설정 ---

# [모델 경로]
MODEL_PATH = '/home/laheckaf/ssj/models/yolo_n.engine'  # Jetson에서 사용할 TensorRT 모델

# [검증 설정] (mAP, F1 등 측정용)
DATA_YAML_PATH = '/home/laheckaf/dataset/data.yaml'  # 검증(validation) 데이터셋의 .yaml 파일 경로
IMG_SIZE = 640                   # 추론 및 검증 시 사용할 이미지 크기
IOU_THRESHOLD = 0.50             # mAP50 계산을 위한 IOU 값
CONF_THRESHOLD = 0.25            # 검증 시 사용할 Confidence 임계값

# [FPS 측정 설정]
FPS_IMAGE_PATH = 'test_fps.jpg'       # FPS 테스트에 사용할 샘플 이미지
WARMUP_RUNS = 10                 # GPU 워밍업을 위한 반복 횟수
FPS_ITERATIONS = 100             # FPS 평균 계산을 위한 반복 횟수

# [결과 저장]
RESULTS_FILE_PATH = 'benchmark_results_jetson.json'

# --- (설정 끝) ---


def check_files():
    """필수 파일들이 존재하는지 확인합니다."""
    if not os.path.exists(MODEL_PATH):
        print(f"오류: Jetson 모델 파일 없음 - {MODEL_PATH}")
        return False

    if not os.path.exists(DATA_YAML_PATH):
        print(f"오류: 데이터셋 YAML 파일 없음 - {DATA_YAML_PATH}")
        return False

    if not os.path.exists(FPS_IMAGE_PATH):
        print(f"경고: FPS 테스트 이미지 없음 - {FPS_IMAGE_PATH}")
        print("Ultralytics 기본 'bus.jpg' 이미지를 다운로드합니다...")
        try:
            from ultralytics.utils.downloads import GITHUB_ASSETS_DIR
            img_path_obj = GITHUB_ASSETS_DIR / 'bus.jpg'
            if not img_path_obj.exists():
                import torch
                torch.hub.download_url_to_file('https://ultralytics.com/images/bus.jpg', 'bus.jpg')
            globals()["FPS_IMAGE_PATH"] = 'bus.jpg' # 전역 변수 업데이트
        except Exception as e:
            print(f"'bus.jpg' 다운로드 실패: {e}")
            return False

    return True

def run_jetson_benchmark():
    """Jetson 플랫폼에서 모든 성능 지표를 측정합니다."""

    if not check_files():
        return

    platform_name = f"Jetson ({platform.machine()})"
    device_target = 0  # Jetson GPU

    print(f"--- 🚀 Jetson 벤치마크 시작 ---")
    print(f"플랫폼: {platform_name}")
    print(f"모델 파일: {MODEL_PATH}")
    print(f"데이터셋: {DATA_YAML_PATH}")
    print(f"타겟 디바이스: {device_target} (GPU)")

    results = {
        'platform': platform_name,
        'model': MODEL_PATH,
        'img_size': IMG_SIZE,
        'iou_threshold': IOU_THRESHOLD,
    }

    try:
        # 1. 모델 로드
        print(f"\n[1/3] 모델 로드 중: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        print("모델 로드 완료.")

        # 2. 정확도 측정 (mAP, Precision, Recall, F1)
        print(f"\n[2/3] 정확도 측정 시작 (데이터: {DATA_YAML_PATH})...")

        metrics = model.val(
            data=DATA_YAML_PATH,
            imgsz=IMG_SIZE,
            split='val',
            iou=IOU_THRESHOLD,
            conf=CONF_THRESHOLD,
            device=device_target,
            verbose=False
        )

        print("정확도 측정 완료.")

        results['mAP50-95'] = metrics.box.map
        results['mAP50'] = metrics.box.map50

        p = metrics.box.p[0] if isinstance(metrics.box.p, list) else metrics.box.p
        r = metrics.box.r[0] if isinstance(metrics.box.r, list) else metrics.box.r

        results['Precision'] = p
        results['Recall'] = r

        if (p + r) > 0:
            results['F1_Score'] = 2 * (p * r) / (p + r)
        else:
            results['F1_Score'] = 0.0

    except Exception as e:
        print(f"‼️ 정확도 측정 중 오류 발생: {e}")
        results['accuracy_error'] = str(e)

    try:
        # 3. 속도(FPS) 측정
        print(f"\n[3/3] FPS 측정 시작 (이미지: {FPS_IMAGE_PATH})...")

        img = cv2.imread(FPS_IMAGE_PATH)
        if img is None:
            print(f"오류: FPS 테스트 이미지 로드 실패 - {FPS_IMAGE_PATH}")
            raise Exception("FPS 이미지 로드 실패")

        # 워밍업
        print(f"워밍업 실행 ({WARMUP_RUNS}회)...")
        for _ in range(WARMUP_RUNS):
            model.predict(img, imgsz=IMG_SIZE, device=device_target, verbose=False)

        # 실제 측정
        print(f"성능 측정 실행 ({FPS_ITERATIONS}회)...")
        start_time = time.perf_counter()

        for _ in range(FPS_ITERATIONS):
            model.predict(img, imgsz=IMG_SIZE, device=device_target, verbose=False)

        end_time = time.perf_counter()

        total_time = end_time - start_time
        avg_time_ms = (total_time / FPS_ITERATIONS) * 1000
        fps = 1.0 / (total_time / FPS_ITERATIONS)

        print(f"FPS 측정 완료: 평균 {fps:.2f} FPS ({avg_time_ms:.2f} ms)")

        results['FPS'] = fps
        results['Avg_Inference_ms'] = avg_time_ms

    except Exception as e:
        print(f"‼️ FPS 측정 중 오류 발생: {e}")
        results['fps_error'] = str(e)

    # 4. 결과 저장
    try:
        print(f"\n--- 💾 결과 저장 ---")
        print(f"파일 경로: {RESULTS_FILE_PATH}")

        with open(RESULTS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4, cls=NumpyEncoder)

        print("결과가 JSON 파일로 성공적으로 저장되었습니다.")

        print("\n--- Jetson 최종 요약 ---")
        print(json.dumps(results, indent=2, ensure_ascii=False, cls=NumpyEncoder))
        print("-----------------------")

    except Exception as e:
        print(f"‼️ 결과 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    run_jetson_benchmark()

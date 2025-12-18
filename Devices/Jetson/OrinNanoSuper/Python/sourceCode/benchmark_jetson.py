import os
import time
import json
import cv2
import platform
import gc
import torch
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

# [✅ 모델 리스트 설정] 
# 'name'에 적은 이름이 결과 JSON의 "Key(이름표)"가 됩니다.
MODELS_CONFIG = [
    {
        "name": "yolov8n_fp16", 
        "path": "/home/laheckaf/ssj/models/FP16/yolov8n_fp16.engine"
    },
    {
        "name": "yolov8s_fp16",  
        "path": "/home/laheckaf/ssj/models/FP16/yolov8s_fp16.engine"
    },
    {
        "name": "yolov8m_fp16",  
        "path": "/home/laheckaf/ssj/models/FP16/yolov8m_fp16.engine"
    },
    {
        "name": "yolov8l_fp16",  
        "path": "/home/laheckaf/ssj/models/FP16/yolov8l_fp16.engine"
    },
    {
        "name": "yolov8n_int8",  
        "path": "/home/laheckaf/ssj/models/INT8/yolov8n_int8.engine"
    },
    {
        "name": "yolov8s_int8",  
        "path": "/home/laheckaf/ssj/models/INT8/yolov8s_int8.engine"
    },
    {
        "name": "yolov8m_int8",  
        "path": "/home/laheckaf/ssj/models/INT8/yolov8m_int8.engine"
    },
    {
        "name": "yolov8l_int8",  
        "path": "/home/laheckaf/ssj/models/INT8/yolov8l_int8.engine"
    }
]

# [검증 설정]
DATA_YAML_PATH = '/home/laheckaf/dataset/data.yaml'
IMG_SIZE = 640
IOU_THRESHOLD = 0.50
CONF_THRESHOLD = 0.20

# [FPS 측정 설정]
FPS_IMAGE_PATH = 'test_fps.jpg' 
WARMUP_RUNS = 10
FPS_ITERATIONS = 100

# [결과 저장]
RESULTS_FILE_PATH = 'benchmark_results_all_models.json'

# --- (설정 끝) ---

def prepare_common_files():
    """공통 파일 확인 및 준비"""
    if not os.path.exists(DATA_YAML_PATH):
        print(f"❌ 오류: 데이터셋 YAML 파일 없음 - {DATA_YAML_PATH}")
        return False
        
    global FPS_IMAGE_PATH
    if not os.path.exists(FPS_IMAGE_PATH):
        try:
            from ultralytics.utils.downloads import GITHUB_ASSETS_DIR
            img_path_obj = GITHUB_ASSETS_DIR / 'bus.jpg'
            if not img_path_obj.exists():
                torch.hub.download_url_to_file('https://ultralytics.com/images/bus.jpg', 'bus.jpg')
            FPS_IMAGE_PATH = 'bus.jpg'
        except Exception as e:
            print(f"❌ 이미지 다운로드 실패: {e}")
            return False
    return True

def evaluate_single_model(model_config):
    """개별 모델 벤치마크 수행"""
    
    model_name = model_config['name']
    model_path = model_config['path']
    device_target = 0 

    print(f"\n" + "="*50)
    print(f"🧪 모델 테스트 시작: [{model_name}]")
    print(f"📁 경로: {model_path}")
    print(f"="*50)

    if not os.path.exists(model_path):
        print(f"❌ 오류: 모델 파일 없음 ({model_path}). 건너뜁니다.")
        return None

    # 결과 담을 딕셔너리
    result = {
        'model_path': model_path,
        'img_size': IMG_SIZE,
        'conf_threshold': CONF_THRESHOLD,
        'iou_threshold': IOU_THRESHOLD,
        'platform': f"Jetson ({platform.machine()})",
        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        # 1. 모델 로드
        print(f"[1/3] 모델 로드 중...")
        model = YOLO(model_path)
        
        # 2. 정확도 측정
        print(f"[2/3] 정확도(mAP) 측정 시작...")
        metrics = model.val(
            data=DATA_YAML_PATH,
            imgsz=IMG_SIZE,
            split='val',
            iou=IOU_THRESHOLD,
            conf=CONF_THRESHOLD,
            device=device_target,
            verbose=False
        )
        
        result['mAP50-95'] = metrics.box.map
        result['mAP50'] = metrics.box.map50
        result['Precision'] = metrics.box.p[0] if isinstance(metrics.box.p, list) else metrics.box.p
        result['Recall'] = metrics.box.r[0] if isinstance(metrics.box.r, list) else metrics.box.r
        
        # F1 Score 계산
        p, r = result['Precision'], result['Recall']
        result['F1_Score'] = 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0

        # 3. FPS 측정
        print(f"[3/3] FPS 속도 측정 시작...")
        img = cv2.imread(FPS_IMAGE_PATH)
        if img is None: raise Exception("이미지 로드 실패")

        # 워밍업
        for _ in range(WARMUP_RUNS):
            model.predict(img, imgsz=IMG_SIZE, device=device_target, verbose=False)

        # 실제 측정
        start_time = time.perf_counter()
        for _ in range(FPS_ITERATIONS):
            model.predict(img, imgsz=IMG_SIZE, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, device=device_target, verbose=False)
        end_time = time.perf_counter()

        total_time = end_time - start_time
        result['FPS'] = 1.0 / (total_time / FPS_ITERATIONS)
        result['Avg_Inference_ms'] = (total_time / FPS_ITERATIONS) * 1000
        
        print(f"✅ [{model_name}] 완료: {result['FPS']:.2f} FPS / mAP50: {result['mAP50']:.3f}")

        # 메모리 정리
        del model
        del metrics
        torch.cuda.empty_cache()
        gc.collect()

        return result

    except Exception as e:
        print(f"‼️ [{model_name}] 오류 발생: {e}")
        result['error'] = str(e)
        return result

def run_all_benchmarks():
    """모든 모델을 실행하고 결과를 이름(Key)으로 저장"""
    
    print("--- 🚀 Jetson 다중 모델 벤치마크 시작 ---")
    
    if not prepare_common_files():
        return

    # ✅ 리스트([]) 대신 딕셔너리({}) 사용
    final_results_dict = {}

    for config in MODELS_CONFIG:
        model_name = config['name'] # 여기서 설정한 이름을 키값으로 씁니다.
        
        res = evaluate_single_model(config)
        
        if res is not None:
            # ✅ 결과 딕셔너리에 이름으로 저장
            final_results_dict[model_name] = res
            
        time.sleep(2) # 열 식히기

    # 결과 저장
    print(f"\n--- 💾 전체 결과 저장 중 ---")
    try:
        with open(RESULTS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_results_dict, f, ensure_ascii=False, indent=4, cls=NumpyEncoder)
        print(f"파일 저장 완료: {RESULTS_FILE_PATH}")
        
        # 요약 출력
        print("\n--- 📊 최종 요약 ---")
        print(f"{'Model Name':<20} | {'FPS':<10} | {'mAP50':<10} | {'F1-Score':<10}")
        print("-" * 60)
        
        # 딕셔너리 순회하며 출력
        for name, data in final_results_dict.items():
            if 'error' not in data:
                print(f"{name:<20} | {data['FPS']:<10.2f} | {data['mAP50']:<10.4f} | {data['F1_Score']:<10.4f}")
            else:
                print(f"{name:<20} | ERROR 발생")
        print("-" * 60)

    except Exception as e:
        print(f"결과 저장 실패: {e}")

if __name__ == "__main__":
    run_all_benchmarks()

import os
import json
import time
from ultralytics import YOLO
from datetime import datetime

def run_master_benchmark():
    # 1. 경로 설정 (수정됨)
    BASE_MODEL_DIR = '/home/risedevicename/models_path'
    DATA_PATH = '/home/risedevicename/data.yaml'
    IMAGE_DIR = '/home/risedevicename/test_images_path' # 이미지 경로 확인 필요

    model_files = [
        'yolov8n_fp16.engine', 'yolov8s_fp16.engine',
        'yolov8m_fp16.engine', 'yolov8l_fp16.engine',
        'yolov8n_int8.engine', 'yolov8s_int8.engine',
        'yolov8m_int8.engine', 'yolov8l_int8.engine'
    ]

    # 이미지 리스트 준비
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    if not os.path.exists(IMAGE_DIR):
         print(f"ERROR: 이미지 경로 '{IMAGE_DIR}'가 존재하지 않습니다.")
         return

    image_list = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR)
                  if f.lower().endswith(valid_extensions)]

    if not image_list:
        print(f"ERROR: '{IMAGE_DIR}'에 이미지가 없습니다.")
        return

    final_results = {}
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"--- 통합 벤치마크 시작 (대상: {len(model_files)}종) ---")

    for filename in model_files:
        # 파일명에 따라 하위 폴더 자동 선택
        if 'fp16' in filename:
            sub_dir = 'engine_fp16'
        elif 'int8' in filename:
            sub_dir = 'engine_int8'
        else:
            print(f"SKIP: {filename} (알 수 없는 형식)")
            continue
            
        model_path = os.path.join(BASE_MODEL_DIR, sub_dir, filename)

        if not os.path.exists(model_path):
            print(f"SKIP: 파일 없음 - {model_path}")
            continue

        print(f"\n[분석 중] {filename}...")

        try:
            model = YOLO(model_path, task="detect")

            # --- PART 1. 지능 지표 (mAP) ---
            val_results = model.val(
                data=DATA_PATH, split='test', device=0,
                plots=False, save_json=False, verbose=False
            )
            res_dict = val_results.results_dict
            p = res_dict.get('metrics/precision(B)', 0)
            r = res_dict.get('metrics/recall(B)', 0)
            f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0

            # --- PART 2. 속도 지표 (FPS & Avg Inference) ---
            model.predict(image_list[0], verbose=False) # Warm-up

            total_inference_ms = 0.0
            start_time = time.time()
            
            for img_path in image_list:
                results = model.predict(img_path, verbose=False, device=0)
                total_inference_ms += results[0].speed['inference']
            
            end_time = time.time()

            total_duration = end_time - start_time
            fps = len(image_list) / total_duration
            avg_inference_ms = total_inference_ms / len(image_list)

            # --- PART 3. 데이터 저장 ---
            final_results[filename] = {
                "FPS": round(fps, 2),
                "Avg_Inference(ms)": round(avg_inference_ms, 2),
                "mAP50": round(res_dict.get('metrics/mAP50(B)', 0), 4),
                "mAP50-95": round(res_dict.get('metrics/mAP50-95(B)', 0), 4),
                "Precision": round(p, 4),
                "Recall": round(r, 4),
                "F1-Score": round(f1, 4)
            }

            print(f"DONE {filename} | FPS: {fps:.2f} | Inf: {avg_inference_ms:.2f}ms | mAP50: {final_results[filename]['mAP50']}")

        except Exception as e:
            print(f"ERROR {filename}: {e}")

    # 결과 저장
    save_path = f'benchmark_result_{timestamp}.json'
    with open(save_path, 'w') as f:
        json.dump(final_results, f, indent=4)

    print(f"\n완료! 결과 저장: {save_path}")

if __name__ == "__main__":
    run_master_benchmark()

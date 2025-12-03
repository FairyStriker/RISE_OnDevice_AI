## YOLOv8 주요 인자 설명 및 CLI 예제 코드

이전에 항목별로 설명해 드린 YOLOv8의 핵심 인자들을 이해하기 쉽도록 실제 **CLI 예제 코드**와 함께 다시 정리해 드릴게요.

-----

### 1\. 성능 및 정밀도 제어 (하드웨어 최적화)

이 인자들은 학습 및 추론 속도와 GPU 메모리 사용 방식을 결정합니다.

  * **`amp`** (`train` 모드): 혼합 정밀도(FP16) 학습 활성화/비활성화.
      * **FP16 혼합 정밀도 학습 예시:**
        
        ```bash
        yolo train model=yolov8s.pt data=data.yaml epochs=100 amp=True
        ```
  * **`half` (`export` 모드):** 모델을 **FP16 추론 엔진**으로 변환합니다.
      * **FP16 엔진 변환 예시:**
        
        ```bash
        yolo export model=best.pt format=engine half=True
        ```
  * **`int8` (`export` 모드):** 모델을 **INT8 양자화 엔진**으로 변환합니다 (캘리브레이션 필요).
      * **INT8 엔진 변환 예시:**
        
        ```bash
        yolo export model=best.pt format=engine int8=True data=data.yaml
        ```
  * **`device` (모든 모드):** 연산을 수행할 GPU ID를 지정합니다.
      * **GPU 0번과 1번을 사용하여 학습 예시:**
        
        ```bash
        yolo train model=yolov8s.pt data=data.yaml epochs=100 device=0,1
        ```

-----

### 2\. 학습(Training) 제어

이 인자들은 모델 학습 과정의 반복 횟수와 데이터를 처리하는 방식을 설정합니다.

  * **`epochs`** & **`batch`**: 학습 반복 횟수와 배치 사이즈를 지정합니다.
      * **epochs=300, batch=16 설정 예시:**
        
        ```bash
        yolo train model=yolov8s.pt data=data.yaml epochs=300 batch=16
        ```
  * **`imgsz`**: 모델의 입력 이미지 크기를 지정합니다.
      * **입력 이미지 크기를 1280으로 설정 예시:**
        
        ```bash
        yolo train model=yolov8s.pt data=data.yaml imgsz=1280
        ```
  * **`patience`**: 조기 종료(Early Stopping)를 위한 대기 Epoch 수를 설정합니다.
      * **20 Epoch 동안 성능 개선이 없으면 종료 예시:**
        
        ```bash
        yolo train model=yolov8s.pt data=data.yaml epochs=300 patience=20
        ```

-----

### 3\. 추론(Inference) 및 추적(Tracking) 제어

이 인자들은 탐지된 객체를 필터링하고, 동영상에서 객체를 추적하는 데 사용됩니다.

  * **`conf`** & **`iou`**: 신뢰도와 NMS 임계값을 지정합니다.
      * **신뢰도 40%, NMS 50% 설정 예시:**
        
        ```bash
        yolo predict model=best.pt source=my_video.mp4 conf=0.4 iou=0.5
        ```
  * **`tracker` (`track` 모드):** 객체 추적 알고리즘을 지정합니다.
      * **BoTSORT 추적 활성화 예시:**
        
        ```bash
        yolo track model=best.engine source=my_video.mp4 tracker=botsort.yaml
        ```

-----

### 4\. 데이터셋 및 평가/저장 경로 제어

이 인자들은 최종 평가 데이터셋을 지정하거나 결과 파일의 저장 위치를 변경합니다.

  * **`split` (`val` 모드):** 성능 평가에 사용할 데이터셋 분할을 지정합니다.
      * **Test 데이터셋으로 최종 성능 평가 예시:**
        
        ```bash
        yolo val model=best.pt data=data.yaml split=test
        ```
  * **`project`** & **`name`**: 결과 폴더의 저장 위치를 지정합니다.
      * **결과를 'custom\_results/tracking\_run'에 저장 예시:**
        
        ```bash
        yolo track model=best.engine source=my_video.mp4 project=custom_results name=tracking_run
        ```

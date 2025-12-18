import cv2
import json
import time
from ultralytics import YOLO
from datetime import datetime

# ===================================================================
# 1. 설정 (사용자 환경에 맞게 반드시 수정해야 하는 부분)
# ===================================================================
# [A] RTSP 주소: 노트북(192.168.0.19)의 스트리밍 주소
RTSP_URL = "rtsp://192.168.0.52:8554/test"  

# [B] 모델 경로: 현재 실행 위치(~/ssj)를 기준으로 models 폴더 안의 yolo_s.engine 지정
# (이전에 models/yolo_s.engine 경로를 찾았습니다.)
MODEL_PATH = "/home/laheckaf/ssj/models/yolo_s.engine" 

# [C] 로그 파일 경로
JSON_FILE = "/home/laheckaf/ssj/json_log/detection_log.jsonl" 

# [D] 디스플레이 설정 (HD 720p 크기)
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
# ===================================================================

# FPS 계산을 위한 변수 초기화
prev_time = 0

# 1. 모델 로드 (Engine 파일)
try:
    print("--> TensorRT Engine 모델을 로드하는 중...")
    # task='detect'는 객체 탐지 모델임을 명시합니다.
    model = YOLO(MODEL_PATH, task='detect') 
    print("--> 모델 로드 완료.")
except Exception as e:
    print(f"Error: 모델 로드 실패. 경로를 확인하세요: {MODEL_PATH}")
    print(f"상세 에러: {e}")
    exit()

# 2. 비디오 캡처 시작 (OpenCV)
# 지연 시간을 최소화하기 위해 버퍼 사이즈를 1로 설정합니다.
cap = cv2.VideoCapture(RTSP_URL)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Error: RTSP 스트림을 열 수 없습니다. 노트북 방화벽 및 스트림 상태를 확인하세요.")
    exit()

print(f"--> 추론 및 기록 시작. JSON 로그 파일: {JSON_FILE} (종료하려면 'q'를 누르세요)")

# 3. 화면 출력 창 설정 (크기 조절 가능 + HD 크기로 시작)
WINDOW_NAME = "Jetson YOLOv8 Inference"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, DISPLAY_WIDTH, DISPLAY_HEIGHT)

# 4. 메인 루프 시작 및 JSON 파일 열기 (추가 모드 'a')
with open(JSON_FILE, "a", encoding="utf-8") as f:
    while True:
        ret, frame = cap.read()
        
        # FPS 계산 시작
        new_time = time.time()
        
        if not ret:
            print("프레임을 받아올 수 없습니다. 재연결 시도 중...")
            time.sleep(1)
            cap.open(RTSP_URL) # 끊기면 재접속 시도
            continue

        # 5. 추론 및 트래킹
        # persist=True를 통해 프레임 간 객체 ID를 유지합니다 (추적).
        results = model.track(frame, persist=True, verbose=False, device='cuda:0')

        # 6. JSON 데이터 기록
        current_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "frame_objects": []
        }

        # 감지된 객체 데이터 추출 및 JSON 포맷팅
        if results[0].boxes is not None and results[0].boxes.id is not None:
            # 텐서 데이터를 CPU로 이동 후 리스트로 변환
            boxes = results[0].boxes.xyxy.cpu().numpy().tolist() # [x1, y1, x2, y2]
            track_ids = results[0].boxes.id.cpu().numpy().tolist() # 객체 ID
            class_ids = results[0].boxes.cls.cpu().numpy().tolist() # 클래스 번호
            confidences = results[0].boxes.conf.cpu().numpy().tolist() # 정확도

            for box, track_id, cls, conf in zip(boxes, track_ids, class_ids, confidences):
                obj_info = {
                    "id": int(track_id),
                    "class": int(cls),
                    "confidence": round(conf, 2),
                    "bbox": [round(x, 1) for x in box]
                }
                current_data["frame_objects"].append(obj_info)
        
        # 감지된 객체가 있으면 JSONL 파일에 한 줄 기록
        if current_data["frame_objects"]: 
            json_line = json.dumps(current_data, ensure_ascii=False)
            f.write(json_line + "\n")
            f.flush() # 버퍼를 비워 즉시 파일에 쓰기 (안정성 증가)

        # 7. FPS 계산 및 화면 표시
        time_diff = new_time - prev_time
        if time_diff > 0:
            fps = 1 / time_diff
        else:
            fps = 0
            
        prev_time = new_time
        
        # BBox가 그려진 프레임을 가져옴
        annotated_frame = results[0].plot()

        # FPS 텍스트를 화면 좌상단에 표시 (초록색)
        cv2.putText(annotated_frame, f"FPS: {int(fps)}", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 8. 최종 화면 출력
        cv2.imshow(WINDOW_NAME, annotated_frame)

        # 'q' 키를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# 9. 종료 시 자원 해제
cap.release()
cv2.destroyAllWindows()
print("--> 프로그램이 종료되었습니다.")

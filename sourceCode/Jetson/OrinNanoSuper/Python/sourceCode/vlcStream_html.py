import cv2
import time
import requests
import threading
import numpy as np
from ultralytics import YOLO
from datetime import datetime

# ================= 사용자 설정 =================
N100_IP = "192.168.0.52"
INPUT_RTSP = f"rtsp://{N100_IP}:8554/test"
DATA_URL = f"http://{N100_IP}:5000/receive_data"
IMAGE_URL = f"http://{N100_IP}:5000/receive_image"
TARGET_SIZE = (640, 640)
JPEG_QUALITY = [int(cv2.IMWRITE_JPEG_QUALITY), 50]

# [추가됨] 타임아웃 설정 (초 단위)
# 5초 동안 프레임이 안 들어오면 재접속합니다.
RECONNECT_TIMEOUT = 3.0 

# [중요] 모델 파일 경로 매핑
MODEL_PATHS = {
    # FP16 Models
    "n_fp16": "/home/laheckaf/ssj/models/FP16/yolov8n_fp16.engine",
    "s_fp16": "/home/laheckaf/ssj/models/FP16/yolov8s_fp16.engine",
    "m_fp16": "/home/laheckaf/ssj/models/FP16/yolov8m_fp16.engine",
    "l_fp16": "/home/laheckaf/ssj/models/FP16/yolov8l_fp16.engine",
    
    # INT8 Models
    "n_int8": "/home/laheckaf/ssj/models/INT8/yolov8n_int8.engine",
    "s_int8": "/home/laheckaf/ssj/models/INT8/yolov8s_int8.engine",
    "m_int8": "/home/laheckaf/ssj/models/INT8/yolov8m_int8.engine",
    "l_int8": "/home/laheckaf/ssj/models/INT8/yolov8l_int8.engine",
}

# 기본 모델 키
current_model_key = "n_fp16"
# =============================================

class RTSPStreamLoader:
    def __init__(self, src):
        self.src = src
        self.cap = cv2.VideoCapture(src)
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # [추가] 마지막으로 프레임을 받은 시간 기록
        self.last_frame_time = time.time()

        if self.cap.isOpened(): 
            print(f"--> [수신] 연결 성공")
            self.last_frame_time = time.time() # 연결 성공 시 시간 리셋
        else: 
            print(f"--> [에러] 수신 실패")
            
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            # 1. 캡처 객체가 열려있는지 확인
            if self.cap.isOpened():
                self.cap.grab() # 버퍼 비우기
                success, frame = self.cap.retrieve()
                
                if success:
                    with self.lock: 
                        self.frame = frame
                    # [추가] 성공했으므로 타이머 갱신 (생존 신고)
                    self.last_frame_time = time.time()
                else: 
                    time.sleep(0.01)
            else:
                # 닫혀있다면 재연결 시도
                print(f"--> [재접속] 연결 복구 시도 중...")
                self.cap.open(self.src)
                if self.cap.isOpened():
                    self.last_frame_time = time.time()
                time.sleep(1.0)

            # 2. [추가됨] 타임아웃 감시 (Watchdog)
            # 마지막 성공 시간으로부터 RECONNECT_TIMEOUT(5초)가 지났는지 체크
            if time.time() - self.last_frame_time > RECONNECT_TIMEOUT:
                print(f"⚠️ [경고] {RECONNECT_TIMEOUT}초간 신호 없음. 강제 재접속!")
                
                # 기존 연결 강제 종료
                self.cap.release()
                
                # 시간 리셋 (연속 재접속 방지)
                self.last_frame_time = time.time() 

    def read(self):
        with self.lock: return self.frame.copy() if self.frame is not None else None
    
    def release(self):
        self.running = False
        if self.cap:
            self.cap.release()

def load_yolo_model(key):
    """모델을 안전하게 로드하는 함수"""
    path = MODEL_PATHS.get(key)
    print(f"--> [시스템] 모델 교체 시도: {key} ({path})")
    try:
        new_model = YOLO(path)
        print(f"--> [성공] 모델 로드 완료!")
        return new_model
    except Exception as e:
        print(f"--> [실패] 모델 로드 에러: {e}")
        return None

def main():
    global current_model_key
    
    # 1. 초기 모델 로드
    model = load_yolo_model(current_model_key)
    if model is None: return

    loader = RTSPStreamLoader(INPUT_RTSP)
    time.sleep(2)
    print("--> 시스템 가동 시작")
    
    prev_time = 0

    while True:
        raw_frame = loader.read()
        
        # 프레임이 없으면(재접속 중) 대기
        if raw_frame is None:
            time.sleep(0.1) # CPU 과부하 방지를 위해 대기 시간 조금 늘림
            continue

        try:
            frame = cv2.resize(raw_frame, TARGET_SIZE)
            
            # AI 추론
            results = model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml")
            
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time

            # 데이터 구성
            detection_data = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "fps": round(fps, 1),
                "objects": []
            }

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                ids = results[0].boxes.id.cpu().numpy()
                confs = results[0].boxes.conf.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                for box, track_id, conf, cls in zip(boxes, ids, confs, classes):
                    detection_data["objects"].append({
                        "id": int(track_id),
                        "class": int(cls),
                        "conf": round(float(conf), 2),
                        "bbox": [round(float(x), 1) for x in box]
                    })

            annotated_frame = results[0].plot()

            # =======================================================
            # 데이터 전송 및 [모델 변경 감지]
            # =======================================================
            if detection_data: 
                try:
                    # JSON 전송 후 응답 받기
                    response = requests.post(DATA_URL, json=detection_data, timeout=0.1)
                    res_json = response.json()
                    
                    # ★ 서버가 원하는 모델 확인
                    target_model = res_json.get("target_model")
                    
                    # 현재 모델과 다르면 교체 진행
                    if target_model and target_model != current_model_key:
                        if target_model in MODEL_PATHS:
                            print(f"\n⚠️ 모델 변경 감지! ({current_model_key} -> {target_model})")
                            new_model = load_yolo_model(target_model)
                            if new_model:
                                model = new_model
                                current_model_key = target_model
                        else:
                            print(f"⚠️ 요청된 모델이 목록에 없음: {target_model}")

                except: pass
                
                try:
                    _, img_encoded = cv2.imencode('.jpg', annotated_frame, JPEG_QUALITY)
                    requests.post(IMAGE_URL, files={'image': img_encoded.tobytes()}, timeout=0.5)
                except: pass

        except Exception as e:
            print(f"Error: {e}")
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    loader.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
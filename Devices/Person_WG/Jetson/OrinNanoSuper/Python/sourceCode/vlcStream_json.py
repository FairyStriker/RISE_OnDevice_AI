import cv2
import time
import requests
import threading
import os
from ultralytics import YOLO
from datetime import datetime

# =========================================================
# 1. 사용자 설정 (N100 서버 IP 확인 필수!)
# =========================================================

# N100 서버의 IP 주소 (예: 192.168.0.52)
# 본인의 N100 IP로 꼭 수정하세요.
N100_IP = "192.168.0.52"

# 영상 수신 주소 (VLC)
RTSP_URL = f"rtsp://{N100_IP}:8554/test"

# 데이터 전송 주소 (Python Server)
SERVER_URL = f"http://{N100_IP}:5000/receive_data"

# 모델 파일 경로 (yolo11n.pt, yolo_l.engine 등 본인 경로에 맞게 수정)
MODEL_PATH = "/home/laheckaf/ssj/models/yolo_l.engine"

# 목표 해상도 (이 크기로 강제 변환하여 오류 방지)
TARGET_SIZE = (640, 640)

# =========================================================
# 2. RTSP 스트림 로더 (끊김 방지 및 재접속 기능 포함)
# =========================================================
class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(url)
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        
        # 연결 확인
        if self.cap.isOpened():
            print(f"--> [RTSP] 서버 연결 성공: {url}")
        else:
            print(f"--> [Error] 서버 연결 실패. N100 VLC를 확인하세요.")

        # 별도 스레드에서 프레임 계속 받아오기
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                # 버퍼 비우기 (가장 최신 프레임 유지를 위해 grab 수행)
                self.cap.grab()
                success, frame = self.cap.retrieve()
                
                if success:
                    with self.lock:
                        self.frame = frame
                else:
                    # 프레임이 안 들어오면(파일 전환 시점 등) 잠시 대기
                    time.sleep(0.01)
            else:
                # 연결이 끊겼다면 재접속 시도
                print("--> [Info] 스트림 재접속 시도 중...")
                self.cap.open(self.url)
                time.sleep(1.0)

    def read(self):
        with self.lock:
            # 복사본을 넘겨서 스레드 충돌 방지
            return self.frame.copy() if self.frame is not None else None

    def release(self):
        self.running = False
        self.cap.release()

# =========================================================
# 3. 메인 실행부
# =========================================================
def main():
    # (1) 모델 로드
    print(f"--> 모델 로드 중: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH)
    except Exception as e:
        print(f"Error: 모델을 찾을 수 없습니다.\n{e}")
        return

    # (2) 스트림 시작
    stream = RTSPStream(RTSP_URL)
    time.sleep(2) # 초기 안정화 대기

    print("--> 시스템 가동 시작 (종료하려면 'q' 키)")
    
    prev_time = 0
    
    while True:
        # 프레임 가져오기
        frame = stream.read()
        
        # 아직 프레임이 없으면 대기
        if frame is None:
            time.sleep(0.01)
            continue

        # =======================================================
        # [핵심] 방어 코드 구간 (Try - Except)
        # 영상 크기가 바뀌거나 깨져도 프로그램이 죽지 않게 함
        # =======================================================
        try:
            # 1. 해상도 강제 통일 (가장 에러가 많이 나는 부분 방어)
            frame = cv2.resize(frame, TARGET_SIZE)

            # 2. AI 추론
            results = model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml")
            
            # 3. FPS 계산
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time) if prev_time else 0
            prev_time = curr_time

            # 4. 데이터 가공
            detection_data = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

            # 5. N100 서버로 전송
            if detection_data["objects"]:
                try:
                    # 0.1초 타임아웃 설정 (네트워크 느려도 영상 안 멈추게)
                    requests.post(SERVER_URL, json=detection_data, timeout=0.1)
                except requests.exceptions.RequestException:
                    pass # 서버 연결 안 되면 조용히 넘어감

            # 6. 화면 출력
            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, f"FPS: {int(fps)}", (20, 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Jetson Client", annotated_frame)

        except Exception as e:
            # 에러 발생 시 여기서 잡아냄! (프로그램 종료 방지)
            print(f"⚠️ [Warning] 불량 프레임 건너뜀: {e}")
            continue
        # =======================================================

        # 'q' 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

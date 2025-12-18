import cv2
import json
import time
import threading
import os
from ultralytics import YOLO
from datetime import datetime

# =========================================================
# 1. 사용자 설정 (수정된 경로 및 해상도)
# =========================================================

# RTSP 주소 (여러 대인 경우 이 부분만 변경해서 파일 복사)
RTSP_URL = "rtsp://192.168.0.52:8554/test"

# 모델 및 로그 파일 절대 경로 수정
MODEL_PATH = "/home/laheckaf/ssj/models/yolo_l.engine"
JSON_FILE = "/home/laheckaf/ssj/json_log/detection_log.jsonl"

# 해상도 설정 (입력/출력 모두 640x640 통일)
TARGET_SIZE = (640, 640)

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

# =========================================================
# 2. 스레딩 기반 스트림 로더 (OpenCV Only)
# =========================================================
class RTSPStreamLoader:
    def __init__(self, src):
        self.capture = cv2.VideoCapture(src)
        self.status = False
        self.frame = None
        self.stopped = False
        
        if self.capture.isOpened():
            self.status = True
            # 연결 즉시 첫 프레임 확보
            self.status, self.frame = self.capture.read()
            print(f"--> RTSP 연결 성공: {src}")
        else:
            print("--> Error: RTSP 연결 실패.")
            print("    1. VLC 송출 여부 확인")
            print("    2. 주소 및 포트(8554) 확인")

    def start(self):
        # 별도 스레드 시작
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if self.capture.isOpened():
                # [핵심] grab()으로 버퍼에 쌓인 구형 프레임을 계속 버림 (지연 시간 제거)
                self.capture.grab()
                # 디코딩은 retrieve()로 수행
                self.status, self.frame = self.capture.retrieve()
            else:
                time.sleep(0.01)

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.capture.release()

# =========================================================
# 3. 메인 실행부
# =========================================================
if __name__ == "__main__":
    # 1. 모델 로드
    print(f"--> 모델 로드 중: {MODEL_PATH}")
    try:
        model = YOLO(MODEL_PATH, task='detect')
    except Exception as e:
        print(f"Error: 모델 로드 실패. 경로를 확인하세요.\n{e}")
        exit()

    # 2. 스트림 연결
    print(f"--> 연결 시도 중: {RTSP_URL}")
    stream_loader = RTSPStreamLoader(RTSP_URL).start()
    
    # 안정화 대기
    time.sleep(2)
    
    if stream_loader.frame is None:
        print("Error: 영상을 받아오지 못했습니다.")
        stream_loader.stop()
        exit()

    # 3. 화면 설정 (640x640)
    window_name = "Jetson YOLOv8 (640x640)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, TARGET_SIZE[0], TARGET_SIZE[1])

    prev_time = 0
    print("--> 추론 시작 (종료: q)")

    # JSON 저장을 위한 디렉토리 확인 (없으면 에러날 수 있으므로)
    json_dir = os.path.dirname(JSON_FILE)
    if not os.path.exists(json_dir):
        print(f"Warning: 폴더가 없어서 생성합니다 -> {json_dir}")
        os.makedirs(json_dir, exist_ok=True)

    with open(JSON_FILE, "a", encoding="utf-8") as f:
        while True:
            # 최신 프레임 가져오기
            raw_frame = stream_loader.read()
            
            if raw_frame is None or raw_frame.size == 0:
                continue

            # [리사이즈] 640x640으로 통일
            frame = cv2.resize(raw_frame, TARGET_SIZE)

            try:
                # [추론] ByteTrack 사용 (RTSP 끊김 방지)
                # 이미 640x640이므로 imgsz 옵션 생략 가능
                results = model.track(frame, persist=True, 
                                      tracker="bytetrack.yaml", verbose=False)
                
                # FPS 계산
                new_time = time.time()
                fps = 1 / (new_time - prev_time) if (new_time - prev_time) > 0 else 0
                prev_time = new_time

                # JSON 데이터 생성
                current_data = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "frame_objects": []
                }

                if results[0].boxes is not None and results[0].boxes.id is not None:
                    boxes = results[0].boxes.xyxy.cpu().numpy().tolist()
                    track_ids = results[0].boxes.id.cpu().numpy().tolist()
                    class_ids = results[0].boxes.cls.cpu().numpy().tolist()
                    confidences = results[0].boxes.conf.cpu().numpy().tolist()

                    for box, track_id, cls, conf in zip(boxes, track_ids, class_ids, confidences):
                        obj_info = {
                            "id": int(track_id),
                            "class": int(cls),
                            "confidence": round(conf, 2),
                            "bbox": [round(x, 1) for x in box]
                        }
                        current_data["frame_objects"].append(obj_info)

                if current_data["frame_objects"]:
                    json_line = json.dumps(current_data, ensure_ascii=False)
                    f.write(json_line + "\n")

                # [화면 출력] 640x640 그대로 출력
                annotated_frame = results[0].plot()
                
                cv2.putText(annotated_frame, f"FPS: {int(fps)}", (20, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow(window_name, annotated_frame)

            except Exception as e:
                # 에러 로그 무시하지 않고 출력 (디버깅용)
                print(f"Skip frame error: {e}")
                continue

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    stream_loader.stop()
    cv2.destroyAllWindows()

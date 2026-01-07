# ==========================================
# 파일명: object_detector.py
# 설명: 카메라 연결과 객체탐지를 담당하는 모듈
# ==========================================

import cv2
import json
import numpy as np
import threading
import time
from ultralytics import YOLO
from datetime import datetime
from queue import Queue

class RTSPCamera:
    def __init__(self, config, model, sender):
        self.id = config["id"]
        self.url = config["url"]
        
        roi_data = config.get("roi")
        
        if roi_data and len(roi_data) > 2: # 점이 최소 3개는 있어야 다각형이 됨
            self.use_roi = True
            self.roi_points = np.array(roi_data, np.int32)
            print(f"[{self.id}] ROI 설정됨: 활성화")
        else:
            self.use_roi = False
            self.roi_points = None
            print(f"[{self.id}] ROI 없음: 전체 화면 탐지")

        self.model = model # 공유된 YOLO 모델
        self.TARGET_CLASSES = [0] # 0: 사람
        
        self.cap = cv2.VideoCapture(self.url)
        self.frame = None
        self.running = True
        self.lock = threading.Lock()
        self.sender = sender
        
        # 프레임 읽기 전용 스레드 시작 (Non-blocking)
        self.thread = threading.Thread(target=self.update_frame, daemon=True)
        self.thread.start()
        print(f"[{self.id}] 카메라 연결 및 스레드 시작")

    def update_frame(self):
        """
        백그라운드에서 계속 최신 프레임을 읽어오는 함수.
        RTSP 지연(Lag)을 방지하기 위해 필수적입니다.
        """
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                else:
                    # 연결 끊김 시 재연결 로직 (간단화)
                    print(f"[{self.id}] 신호 없음. 재연결 시도...")
                    self.cap.release()
                    time.sleep(3)
                    self.cap = cv2.VideoCapture(self.url)
            else:
                time.sleep(1)

    def get_latest_frame(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def send_batch_data(self, objects_list):
        """ 리스트를 통째로 묶어서 전송하는 함수 """
        data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "camera_id": self.id,
            "count": len(objects_list),  # 몇 명인지도 같이 보내면 좋음
            "objects": objects_list      # 객체 리스트 자체가 들어감
        }
        
        try:
            self.sender.send_data(data)
            print(f"[{self.id}] 묶음 전송: {len(objects_list)}명 감지됨")
        except Exception as e:
            print(f"전송 실패: {e}")

    def process(self):
        frame = self.get_latest_frame()
        if frame is None: return None

        results = self.model.track(frame, persist=True, classes=self.TARGET_CLASSES, verbose=False)
        
        # 1. 이번 프레임에서 검출된 객체들을 담을 빈 리스트 생성
        detected_list = [] 

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xywh.cpu()
            track_ids = results[0].boxes.id.int().cpu().tolist()
            confs = results[0].boxes.conf.cpu().tolist()
            
            for box, track_id, conf in zip(boxes, track_ids, confs):
                x, y, w, h = box
                
                center = (int(x), int(y))
                if self.use_roi:
                    if cv2.pointPolygonTest(self.roi_points, center, False) < 0:
                        continue

                # ROI 내부인지 검사
                # --- 여기 도달했다는 건 (ROI 미사용) OR (ROI 내부) 라는 뜻 ---
                
                # 시각화 (ROI 유무 상관없이 그리기)
                x1, y1 = int(x - w/2), int(y - h/2)
                x2, y2 = int(x + w/2), int(y + h/2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # 2. 전송하지 않고 리스트에 정보만 '추가(Append)'
                obj_data = {
                    "object_id": track_id,
                    "confidence": round(conf, 2),
                    "bbox": [int(x), int(y), int(w), int(h)]
                }
                detected_list.append(obj_data)

        if self.use_roi:
            cv2.polylines(frame, [self.roi_points], True, (255, 0, 0), 2)

        # 3. 반복문이 다 끝난 뒤, 탐지된 게 있으면 '한 번만' 전송
        if detected_list:
            self.send_batch_data(detected_list)

        return frame

    def stop(self):
        self.running = False
        self.thread.join()
        self.cap.release()

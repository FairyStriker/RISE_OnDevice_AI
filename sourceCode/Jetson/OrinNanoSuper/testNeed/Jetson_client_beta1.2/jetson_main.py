# ==========================================
# 파일명: jetson_main.py (Jetson 보드에서 실행)
# 설명: 웹소켓으로 서버에 접속하여 실시간 탐지 데이터를 전송하는 클라이언트
# 필요 라이브러리: pip install websockets
# ==========================================

import cv2
import asyncio
import websockets
import json
from ultralytics import YOLO
import time
from jetson_comms import JetsonSender
from object_detector import RTSPCamera

# === 설정 값 ===
SERVER_IP = "localhost" #서버주소에 맞게 변경할 예정
SERVER_PORT = 8000
CLIENT_ID = "JetsonOrinNano"

TARGET_CLASSES = [0] # 0: 사람

# ================= 카메라 설정 (여러 대 추가 가능) =================
# 각 카메라마다 고유 ID, RTSP 주소, ROI(감지 영역)를 설정합니다.
CAMERAS_CONFIG = [
    {
        "id": "cam_01_front",
        "url": "rtsp://admin:1234@192.168.1.101:554/stream1",
        "roi": [[100, 100], [1000, 100], [1000, 600], [100, 600]] # ROI 좌표
    },
    # 필요시 여기에 딕셔너리를 계속 추가하면 됩니다.
]


def main():
    # 1. YOLO 모델 로드 (한 번만 로드해서 공유)
    # Jetson에서는 'yolov8n.engine' 사용 권장
    print("모델 로딩 중...")
    shared_model = YOLO('yolov8n.pt') 
    sender = JetsonSender(SERVER_IP,SERVER_PORT,CLIENT_ID)

    # 2. 카메라 객체 리스트 생성
    cameras = []
    for config in CAMERAS_CONFIG:
        cam = RTSPCamera(config, shared_model,sender)
        cameras.append(cam)

    print(f"총 {len(cameras)}대의 카메라 감시 시작.")

    try:
        while True:
            # 각 카메라를 순회하며 처리
            for cam in cameras:
                processed_frame = cam.process()

                # 화면 출력 (선택 사항: 너무 많은 창은 성능 저하 원인)
                if processed_frame is not None:
                    # 창 크기를 줄여서 표시 (모니터 공간 절약)
                    small_frame = cv2.resize(processed_frame, (640, 360))
                    cv2.imshow(f"Cam: {cam.id}", small_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("종료 요청 받음.")
        
    finally:
        print("시스템 종료 중...")
        for cam in cameras:
            cam.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
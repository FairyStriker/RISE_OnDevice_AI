# video_streamer.py (전체 코드)
import cv2
import threading
import time

class VideoStreamer:
    """RTSP 영상을 수신하여 전역적으로 공유하는 모듈"""
    def __init__(self, url):
        self.url = url
        self.cap = None
        self.frame = None
        self.is_running = False
        self.lock = threading.Lock() # #[추가] 여러 접속자가 동시에 프레임을 읽을 때 충돌 방지

    def start(self):
        """백그라운드 스레드에서 영상 수신 시작"""
        if self.is_running: return
        self.is_running = True
        # #[추가] 영상 수신 전용 스레드 생성 (메인 루프와 분리)
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        while self.is_running:
            # #[수정] 연결이 없거나 끊긴 경우에만 새 연결 시도
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.url)
                time.sleep(2) 
                continue

            success, frame = self.cap.read()
            if success:
                # #[추가] 이미지를 JPG로 변환하여 메모리에 최신 상태로 보관
                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    with self.lock:
                        self.frame = buffer.tobytes()
            else:
                # #[수정] 수신 실패 시 즉시 리소스 해제 (에러 9 방지 핵심)
                print(f"⚠️ [Streamer] 영상 수신 실패. 재연결 시도 중...")
                self.cap.release()
                self.cap = None
                time.sleep(2)

    def get_jpeg(self):
        """가장 최신 프레임을 안전하게 반환"""
        with self.lock:
            return self.frame

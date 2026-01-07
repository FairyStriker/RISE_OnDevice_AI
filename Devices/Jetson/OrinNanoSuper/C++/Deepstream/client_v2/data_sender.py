import requests
import json
import threading
import queue
import time
import config

class DataSender:
    def __init__(self):
        self.url = f"http://{config.DATA_SERVER_IP}:{config.DATA_SERVER_PORT}/log"
        self.headers = {'Content-Type': 'application/json'}
        self.session = requests.Session()
        
        # 최대 100프레임 데이터 대기 가능
        self.queue = queue.Queue(maxsize=100)
        self.running = True
        
        self.worker = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker.start()
        print(f"✅ [DataSender] 데이터 전송 준비 완료 ({self.url})")

    def send(self, data):
        """파이프라인에서 호출: 큐에 넣고 즉시 리턴"""
        if not self.queue.full():
            self.queue.put(data)

    def _worker_loop(self):
        while self.running:
            try:
                data = self.queue.get(timeout=1.0)
                try:
                    self.session.post(self.url, data=json.dumps(data), headers=self.headers, timeout=1.0)
                except requests.exceptions.RequestException:
                    print(f"⚠️ [DataSender] 서버 응답 없음. 재연결 대기 중...")
                    time.sleep(2.0)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                pass # 기타 에러 무시

    def stop(self):
        self.running = False
        self.worker.join()
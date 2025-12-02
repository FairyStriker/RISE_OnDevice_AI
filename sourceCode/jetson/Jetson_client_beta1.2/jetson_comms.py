# ==========================================
# 파일명: jetson_comms.py
# 설명: 웹소켓 통신을 담당하는 모듈 (일반 스레드에서 호출 가능하도록 개량됨)
# ==========================================

import websockets
import json
import asyncio
import threading
import time

class JetsonSender:
    def __init__(self, server_ip, server_port=8000, client_id="jetson"):
        self.uri = f"ws://{server_ip}:{server_port}/ws/{client_id}"
        self.client_id = client_id
        self.websocket = None
        self.connected = False
        
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
        self.loop_thread.start()
        print(f"[{self.client_id}] 통신용 백그라운드 스레드 시작됨")

    def _start_loop(self):
        """백그라운드 스레드에서 이벤트 루프를 계속 돌립니다."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect_async(self):
        """서버에 연결을 시도합니다"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.connected = True
            print(f"✅ [통신] 서버 연결 성공: {self.uri}")
        except Exception as e:
            print(f"❌ [통신] 서버 연결 실패: {e}")
            self.connected = False

    async def _send_async(self, payload):
        """실제로 백그라운드에서 데이터 전송"""
        # 1. 연결 끊김 체크 및 재접속
        if not self.connected or self.websocket is None or self.websocket.closed:
            print("⚠️ [통신] 연결 끊김. 재접속 시도 중...")
            await self._connect_async()
            if not self.connected:
                return # 재연결 실패 시 이번 데이터는 드랍

        # 2. 전송
        try:
            await self.websocket.send(json.dumps(payload))
            # print(f"📤 데이터 전송 완료") 
        except Exception as e:
            print(f"⚠️ [통신] 전송 에러: {e}")
            self.connected = False

    async def _close_async(self):
        if self.websocket:
            await self.websocket.close()
            print("🛑 [통신] 연결 종료")

    # =========================================================
    # [공개용] 사용자가 호출할 함수 (일반 함수 def)
    # =========================================================
    
    def send_data(self, object_list):
        """
        [일반 함수] 이 함수를 호출하면 백그라운드 스레드에게 일을 시킵니다.
        """
        # 일반 스레드 -> 비동기 루프로 작업 토스!
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_async(object_list), self.loop)

    def close(self):
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._close_async(), self.loop)
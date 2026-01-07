# ==========================================
# 파일명: jetson_comms.py (수정본)
# 설명: 연결 중복 요청 방지 및 안정성 강화
# ==========================================

import websockets
import json
import asyncio
import threading

class JetsonSender:
    def __init__(self, server_ip, server_port=8000, client_id="jetson"):
        # 웹소켓 주소 설정
        self.uri = f"ws://{server_ip}:{server_port}/ws/{client_id}"
        self.client_id = client_id
        
        self.websocket = None
        self.connected = False
        self.is_connecting = False # [중요] 중복 연결 방지용 플래그
        
        # 비동기 처리를 위한 이벤트 루프 생성
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._start_loop, daemon=True)
        self.loop_thread.start()
        print(f"[{self.client_id}] 통신 준비 완료")

    def _start_loop(self):
        """백그라운드 스레드에서 이벤트 루프 실행"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    async def _connect_async(self):
        """서버 연결 (중복 실행 방지 적용)"""
        # 이미 연결되어 있거나, 연결을 시도 중이라면 무시
        if self.connected or self.is_connecting:
            return

        self.is_connecting = True # "연결 중" 팻말 걸기
        try:
            # 타임아웃 2초 설정 (너무 오래 매달리지 않게 함)
            self.websocket = await asyncio.wait_for(websockets.connect(self.uri), timeout=2.0)
            self.connected = True
            print(f"✅ [통신] 서버 연결 성공!")
        except Exception as e:
            # 실패 시 조용히 넘어가고 다음 프레임에 재시도
            # print(f"❌ [통신] 연결 실패: {e}") 
            self.connected = False
        finally:
            self.is_connecting = False # "연결 중" 팻말 내리기

    async def _send_async(self, payload):
        """데이터 전송"""
        # 1. 연결이 없으면 연결 시도
        if not self.connected:
            await self._connect_async()
            # 연결 시도 후에도 실패했으면 이번 데이터는 버림 (드랍)
            if not self.connected:
                return 

        # 2. 데이터 전송
        try:
            await self.websocket.send(json.dumps(payload))
        except Exception:
            # 전송 에러 나면 연결 끊긴 것으로 간주
            print("⚠️ [통신] 전송 실패. 재연결 필요.")
            self.connected = False
            self.websocket = None

    # =========================================================
    # [공개용] 외부에서 호출하는 함수
    # =========================================================
    
    def send_data(self, object_list):
        """
        이 함수만 호출하면 백그라운드에서 알아서 보냅니다.
        """
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._send_async(object_list), self.loop)
    
    def close(self):
        """종료 처리"""
        if self.loop.is_running():
             self.loop.call_soon_threadsafe(self.loop.stop)

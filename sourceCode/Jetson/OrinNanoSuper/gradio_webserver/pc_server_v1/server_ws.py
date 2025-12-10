# ==========================================
# 파일명: server_ws.py
# 설명: 웹소켓 통신 로직만 담당
# ==========================================
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
import json
import data_store  # 공유 저장소 임포트

# 로그 설정
logger = logging.getLogger("server_ws")

# APIRouter 사용 (메인 앱에 부착하기 위함)
router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"🟢 [{client_id}] 연결됨.")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        # 연결이 끊기면 데이터도 지울지, 남겨둘지 결정 (여기선 유지)
        logger.info(f"🔴 [{client_id}] 연결 해제됨.")

manager = ConnectionManager()

# 웹소켓 엔드포인트
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            # 1. 데이터 수신 (Text 형태)
            raw_data = await websocket.receive_text()
            
            # 2. JSON 파싱 (안전장치 추가)
            try:
                json_data = json.loads(raw_data)
                
                # 3. [핵심] 공유 저장소에 데이터 업데이트
                data_store.update_data(client_id, json_data)
                
                # 로그 출력 (디버깅용)
                print(f"📥 [{client_id}] 데이터 갱신 완료")
                
            except json.JSONDecodeError:
                logger.warning(f"⚠️ [{client_id}] JSON 형식이 아님: {raw_data}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"⚠️ [{client_id}] 에러: {e}")
        manager.disconnect(client_id)

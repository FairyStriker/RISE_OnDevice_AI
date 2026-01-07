# routers/logs.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import collections

router = APIRouter()

# 데이터 저장용 메모리 큐 (최신 10개만 저장하여 대시보드에 보여줌)
# 실제 상용화 시에는 DB(SQLite/PostgreSQL)에 저장해야 함
log_buffer = collections.deque(maxlen=10)

# --- 데이터 모델 정의 ---
class ObjectData(BaseModel):
    id: int
    class_id: int
    confidence: float
    bbox: List[int]

class LogData(BaseModel):
    timestamp: str
    fps: float
    objects: List[ObjectData]

# --- API 엔드포인트 ---

@router.post("/log")
async def receive_log(data: LogData):
    """
    [Jetson -> PC]
    Jetson이 보낸 실시간 탐지 데이터를 수신합니다.
    """
    # 메모리 버퍼에 저장 (나중에 DB 저장 로직을 여기에 추가)
    log_buffer.append(data.dict())
    return {"status": "ok"}

@router.get("/dashboard/latest")
def get_dashboard_data():
    """
    [PC -> Web Frontend]
    대시보드가 최신 데이터를 요청하면 버퍼의 마지막 값을 줍니다.
    """
    if not log_buffer:
        return {"fps": 0, "objects": [], "message": "데이터 대기 중..."}
    
    # 가장 최신 데이터 반환
    return log_buffer[-1]
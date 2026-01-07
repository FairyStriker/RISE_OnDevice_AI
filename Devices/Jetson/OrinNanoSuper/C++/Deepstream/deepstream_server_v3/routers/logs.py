# routers/logs.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional
import collections

router = APIRouter()

devices_status = {
    "Nano": {"fps": 0, "objects": [], "timestamp": "--:--:--"},
    "AGX": {"fps": 0, "objects": [], "timestamp": "--:--:--"}
}

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
    device_name: str  # "Nano" 또는 "AGX"
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
    # Jetson의 data_sender.py에서 보낸 device_name을 기준으로 저장합니다.
    dev = data.device_name
    if dev in devices_status:
        devices_status[dev] = {
            "fps": data.fps,
            "objects": [obj.dict() for obj in data.objects],
            "timestamp": data.timestamp
        }
    return {"status": "ok"}

# --- 수정 부분: 기존 dashboard/latest를 기기별 조회 방식으로 변경 ---
@router.get("/api/status/{device_name}")
def get_device_status(device_name: str):
    """
    [PC -> Web Frontend]
    웹 대시보드에서 선택한 기기(device_name)의 최신 데이터를 가져갑니다.
    """
    # 요청한 기기 이름이 있으면 해당 데이터를, 없으면 에러 메시지를 반환합니다.
    return devices_status.get(device_name, {"fps": 0, "objects": [], "message": "기기를 찾을 수 없습니다."})
# ---------------------------------------------------------------

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
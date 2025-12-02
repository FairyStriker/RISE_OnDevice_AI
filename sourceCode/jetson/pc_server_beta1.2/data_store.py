# ==========================================
# 파일명: data_store.py
# 설명: 웹소켓 서버와 UI 간의 데이터 공유를 위한 저장소
# ==========================================

# 각 보드(Client ID)별 최신 데이터를 저장하는 딕셔너리
# 예: { "jetson_01": {...데이터...}, "jetson_02": {...데이터...} }
board_data = {}

def update_data(client_id, data):
    """데이터 업데이트 (웹소켓에서 호출)"""
    board_data[client_id] = data

def get_data(client_id=None):
    """데이터 가져오기 (UI에서 호출)"""
    if client_id:
        return board_data.get(client_id)
    return board_data
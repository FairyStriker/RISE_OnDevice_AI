import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime
import json
import os

app = FastAPI()

# 로그 저장할 파일 경로
LOG_FILE = "detection_log.jsonl"

def clear_screen():
    """터미널 화면을 지우는 함수 (윈도우/리눅스 호환)"""
    os.system('cls' if os.name == 'nt' else 'clear')

@app.post("/receive_data")
async def receive_data(request: Request):
    try:
        data = await request.json()
        
        # 1. 데이터 파싱
        timestamp = datetime.now().strftime('%H:%M:%S')
        objects = data.get("objects", [])
        fps = data.get("fps", 0)
        
        # 2. 화면 초기화 (매 프레임마다 화면을 지우고 다시 그림)
        clear_screen()

        # 3. 헤더 출력 (시간, FPS, 총 개수)
        print(f"========== [ N100 AI 실시간 관제 시스템 ] ==========")
        print(f"시간: {timestamp}  |  젯슨 FPS: {fps}")
        print(f"탐지된 객체 수: {len(objects)}개")
        print("-" * 60)
        
        # 4. 상세 정보 출력 (표 형식)
        # 헤더: ID | 정확도 | 위치(BBox)
        print(f"{'ID':<5} | {'Class':<6} | {'Conf':<6} | {'위치 좌표 [x1, y1, x2, y2]'}")
        print("-" * 60)

        if not objects:
            print("   (탐지된 객체가 없습니다)")
        else:
            for obj in objects:
                # 데이터 추출
                oid = obj['id']
                cls = obj['class']
                conf = int(obj['conf'] * 100) # 퍼센트로 변환
                bbox = obj['bbox'] # [x1, y1, x2, y2]
                
                # 좌표를 정수로 변환해서 보기 좋게 만듦
                bbox_str = f"[{int(bbox[0])}, {int(bbox[1])}, {int(bbox[2])}, {int(bbox[3])}]"
                
                # 한 줄 출력
                print(f"{oid:<5} | {cls:<6} | {conf}%   | {bbox_str}")

        print("-" * 60)
        print("중지하려면 Ctrl+C를 누르세요.")

        # 5. 파일 저장 (백그라운드)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

        return {"status": "ok"}

    except Exception as e:
        # 에러 발생 시 멈추지 않고 출력
        print(f"Error: {e}")
        return {"status": "error"}

if __name__ == "__main__":
    # 로그 레벨을 'error'로 설정하여 접속 로그(POST / 200 OK)가 화면을 방해하지 않게 함
    uvicorn.run(app, host="0.0.0.0", port=5000, access_log=False, log_level="error")

# ==========================================
# 파일명: main.py
# 설명: 전체 시스템 실행 (FastAPI + WebSocket + Gradio)
# ==========================================

import uvicorn
from fastapi import FastAPI
import gradio as gr
import server_ws  # 통신 모듈
import data_store # 데이터 저장소
from gradio_ui import Gradio_ui

# 1. FastAPI 앱 생성
app = FastAPI()

# 2. 통신 모듈(웹소켓 라우터) 등록
# 이제 'ws://IP:8000/ws/{id}' 주소가 활성화됩니다.
app.include_router(server_ws.router)

# 3. Gradio UI 인스턴스 생성
system = Gradio_ui(image_path="test_image.jpg")

# 4. Gradio를 FastAPI에 마운트
demo = system.create_ui()
app = gr.mount_gradio_app(app, demo, path="/")

# 5. 서버 실행
if __name__ == "__main__":
    print("🚀 서버 시작: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)

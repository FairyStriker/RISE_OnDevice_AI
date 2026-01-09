# main.py
import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import config
from routers import logs, models

app = FastAPI()

# -----------------------------------------------------------
# 1. 경로 설정 (사용자 요청에 따라 유지)
# -----------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

if not hasattr(config, 'MODEL_DIR'):
    config.MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(config.MODEL_DIR, exist_ok=True)

# -----------------------------------------------------------
# 2. 라우터 및 정적 파일 연결
# -----------------------------------------------------------
app.include_router(logs.router)
app.include_router(models.router)

app.mount("/download", StaticFiles(directory=config.MODEL_DIR), name="download")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    print(f"🚀 [Server] MediaMTX 연동 모드로 PC 서버 시작")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, access_log=False)
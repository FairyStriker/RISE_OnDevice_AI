# config.py
import os

# 서버 설정
HOST = "0.0.0.0"
PORT = 8000

# 파일 저장 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
REGISTRY_FILE = os.path.join(BASE_DIR, "models.json")

# 폴더가 없으면 생성
os.makedirs(MODEL_DIR, exist_ok=True)
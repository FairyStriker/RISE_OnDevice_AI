# routers/models.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import os
import config
from database import registry # database.py에서 만든 인스턴스

router = APIRouter()

@router.get("/check_update")
def check_update():
    """
    [Jetson -> PC]
    Jetson이 10초마다 호출하여 '어떤 버전을 써야 하는지' 물어봅니다.
    """
    return registry.get_active_model()

@router.post("/upload_model")
async def upload_model(
    model_name: str = Form(...),
    description: str = Form(...),
    config_file: UploadFile = File(...),
    engine_file: UploadFile = File(...)
):
    """
    [Web -> PC]
    새로운 모델 파일을 업로드합니다.
    """
    # 1. 버전 미리 계산 (파일 이름용)
    temp_data = registry.get_all_models()
    next_ver = max([int(k) for k in temp_data["history"].keys()] or [0]) + 1
    
    # 2. 파일 이름 안전하게 변경 (v1_MyModel.engine)
    safe_name = model_name.replace(" ", "_")
    cfg_name = f"v{next_ver}_{safe_name}{os.path.splitext(config_file.filename)[1]}"
    eng_name = f"v{next_ver}_{safe_name}{os.path.splitext(engine_file.filename)[1]}"
    
    # 3. 디스크에 저장
    with open(os.path.join(config.MODEL_DIR, cfg_name), "wb") as f:
        shutil.copyfileobj(config_file.file, f)
    with open(os.path.join(config.MODEL_DIR, eng_name), "wb") as f:
        shutil.copyfileobj(engine_file.file, f)
    
    # 4. 장부 기록
    new_ver = registry.add_model(model_name, description, cfg_name, eng_name)
    
    return {"status": "success", "version": new_ver}

@router.get("/api/models")
def get_model_list():
    """[Web] 전체 모델 리스트 조회"""
    return registry.get_all_models()

@router.post("/api/activate/{version}")
def activate_version(version: int):
    """[Web] 특정 버전으로 모델 교체/롤백"""
    if registry.set_active_version(version):
        return {"status": "success", "active_version": version}
    raise HTTPException(status_code=404, detail="Version not found")

@router.delete("/api/models/{version}")
def delete_model(version: int):
    """[추가: 모델 삭제 요청 반영]"""
    if registry.delete_model(version):
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Delete failed")
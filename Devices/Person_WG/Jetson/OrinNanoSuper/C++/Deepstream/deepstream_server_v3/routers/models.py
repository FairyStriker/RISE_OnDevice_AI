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
    """[Web] 모델 정보 및 실제 파일 삭제"""
    
    # 1. 삭제 전 모델 정보 가져오기 (파일 경로 확인용)
    all_models = registry.get_all_models()
    model_info = all_models["history"].get(str(version))
    
    if not model_info:
        raise HTTPException(status_code=404, detail="해당 버전을 찾을 수 없습니다.")

    # 2. [보안] 현재 활성화된 모델은 삭제 불가능하게 방어
    if all_models.get("active_version") == version:
        raise HTTPException(status_code=400, detail="현재 사용 중인 모델은 삭제할 수 없습니다. 먼저 다른 모델을 활성화하세요.")

    # 3. 물리적 파일 삭제 로직
    try:
        cfg_path = os.path.join(config.MODEL_DIR, model_info["config_file"])
        eng_path = os.path.join(config.MODEL_DIR, model_info["engine_file"])

        if os.path.exists(cfg_path):
            os.remove(cfg_path)
        if os.path.exists(eng_path):
            os.remove(eng_path)
            
    except Exception as e:
        # 파일이 이미 없거나 권한 문제가 있을 경우 로그만 남기고 진행 가능
        print(f"파일 삭제 중 오류 발생: {e}")

    # 4. 장부(Database)에서 삭제
    if registry.delete_model(version):
        return {"status": "success", "message": f"Version {version} deleted."}
    
    raise HTTPException(status_code=500, detail="데이터베이스 삭제 실패")
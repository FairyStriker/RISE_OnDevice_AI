# database.py
import json
import os
import config
from datetime import datetime

class ModelRegistry:
    """
    [모듈: 모델 장부 관리]
    models.json 파일을 읽고 쓰며 버전 정보를 관리합니다.
    """
    def __init__(self):
        self.file_path = config.REGISTRY_FILE
        # 파일이 없으면 초기화
        if not os.path.exists(self.file_path):
            self._save({"active_version": 0, "history": {}})

    def _load(self):
        """JSON 파일 읽기"""
        with open(self.file_path, "r") as f:
            return json.load(f)

    def _save(self, data):
        """JSON 파일 저장"""
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=4)

    def get_active_model(self):
        """현재 활성화된 모델 정보 반환 (Jetson용)"""
        data = self._load()
        active_ver = str(data["active_version"])
        if active_ver == "0" or active_ver not in data["history"]:
            return {"version": 0}
        
        info = data["history"][active_ver]
        return {
            "version": int(active_ver),
            "config_file": info["config_file"],
            "engine_file": info["engine_file"]
        }

    def add_model(self, name, description, cfg_file, eng_file):
        """새 모델 등록 및 버전 생성"""
        data = self._load()
        
        # 새 버전 번호 = (가장 큰 버전 번호) + 1
        current_versions = [int(k) for k in data["history"].keys()]
        new_version = max(current_versions or [0]) + 1
        
        data["history"][str(new_version)] = {
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model_name": name,
            "description": description,
            "config_file": cfg_file,
            "engine_file": eng_file
        }
        # 업로드 시 바로 활성화 (정책에 따라 변경 가능)
        data["active_version"] = new_version
        self._save(data)
        return new_version

    def set_active_version(self, version):
        """특정 버전으로 활성화 변경 (롤백/업데이트)"""
        data = self._load()
        if str(version) in data["history"]:
            data["active_version"] = version
            self._save(data)
            return True
        return False

    def get_all_models(self):
        """대시보드용: 전체 모델 리스트 반환"""
        return self._load()
    
    def delete_model(self, version):
        version_str = str(version)
        if version_str in self.data["history"]:
            del self.data["history"][version_str]
            self._save() # 변경사항을 json 파일 등에 물리적으로 저장하는 함수 호출 필수!
            return True
        return False

# 싱글톤 인스턴스 생성
registry = ModelRegistry()
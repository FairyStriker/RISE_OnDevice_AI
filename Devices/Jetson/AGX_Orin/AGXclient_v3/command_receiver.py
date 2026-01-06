import requests
import time
import os
import threading
import config

class CommandReceiver:
    def __init__(self, pipeline_obj):
        self.pipeline = pipeline_obj
        self.server_url = f"http://{config.DATA_SERVER_IP}:{config.DATA_SERVER_PORT}"
        self.current_version = 0
        self.running = True
        
        # 다운로드 폴더 생성
        self.model_dir = "downloaded_models"
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.worker = threading.Thread(target=self._update_checker, daemon=True)
        self.worker.start()
        print(f"✅ [CommandReceiver] 원격 제어 및 자동 용량 관리 활성화")

    def _cleanup_orphaned_models(self, valid_files):
        """PC 서버 목록에 없는 로컬 파일들을 삭제하여 용량 확보"""
        try:
            local_files = os.listdir(self.model_dir)
            for local_file in local_files:
                # 현재 사용 중인 파일이거나 PC 목록에 존재하는 파일이면 건너뜀
                if local_file in valid_files:
                    continue
                
                # 목록에 없는 파일은 삭제
                file_path = os.path.join(self.model_dir, local_file)
                print(f"🧹 [Cleanup] 더 이상 사용되지 않는 모델 삭제: {local_file}")
                os.remove(file_path)
        except Exception as e:
            print(f"⚠️ [Cleanup] 파일 정리 중 오류: {e}")

    def _download_if_not_exists(self, filename):
        url = f"{self.server_url}/download/{filename}"
        local_path = os.path.join(self.model_dir, filename)
        
        if os.path.exists(local_path):
            print(f"📦 [Cache] 기존 파일 사용: {filename}")
            return local_path
        
        print(f"📥 [Download] 다운로드 시작: {filename}")
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return local_path
        except Exception as e:
            print(f"❌ 다운로드 실패: {e}")
            if os.path.exists(local_path): os.remove(local_path)
            return None

    def _update_checker(self):
        while self.running:
            try:
                # 서버에 '현재 활성 버전' 문의
                response = requests.get(f"{self.server_url}/check_update", timeout=2)
                data = response.json()
                
                target_version = data.get("version", 0)

                # 2. 서버에 '전체 모델 목록' 문의 (삭제 동기화용)
                history_res = requests.get(f"{self.server_url}/api/models", timeout=2)
                history_data = history_res.json()
                
                # PC에 존재하는 모든 설정/엔진 파일명 리스트 생성
                valid_files = []
                for ver_info in history_data.get("history", {}).values():
                    valid_files.append(ver_info["config_file"])
                    valid_files.append(ver_info["engine_file"])
                
                # 내 버전과 다르면 교체 (롤백 포함)
                if target_version != 0 and target_version != self.current_version:
                    print(f"🔄 [Switch] 모델 변경 요청 (v{self.current_version} -> v{target_version})")
                    
                    cfg_path = self._download_if_not_exists(data["config_file"])
                    eng_path = self._download_if_not_exists(data["engine_file"])
                    
                    if cfg_path and eng_path:
                        # 설정 변경 (절대 경로)
                        config.MODEL_CONFIG = os.path.abspath(cfg_path)
                        # 파이프라인 재시작 트리거
                        self.pipeline.request_restart()
                        self.current_version = target_version
                        print(f"✨ [Success] v{target_version} 적용 완료.")
                
                self._cleanup_orphaned_models(valid_files)

            except Exception:
                pass # 서버 꺼져있으면 무시
            
            time.sleep(10) # 10초 주기

    def stop(self):
        self.running = False
        self.worker.join()
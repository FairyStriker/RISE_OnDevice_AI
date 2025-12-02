# ==========================================
# 파일명: gradio_ui.py (서버 PC에서 실행)
# 설명: gradio를 이용한 GUI 서버
# =========================================

import gradio as gr
import cv2
import numpy as np
import data_store #데이터 저장소

class Gradio_ui:
    def __init__(self, image_path="test_image.jpg"):
        """
        초기화 메서드: 설정값 정의 및 리소스 로드
        """
        self.frame_width = 1280
        self.frame_height = 720
        self.image_path = image_path
        
        # 탐지 가능한 클래스와 색상 정의
        self.classes = ["person", "car", "bus"]
        self.colors = (255, 0, 0) # RGB 순서 (Gradio용)
        
        # 배경 이미지 미리 로드 (매번 읽지 않도록 최적화)
        self.base_frame = self._load_base_frame()

    def _load_base_frame(self):
        """
        배경 이미지를 로드하고 크기를 조정하는 내부 메서드
        """
        img = cv2.imread(self.image_path)
        if img is None:
            # 이미지가 없으면 검은 화면 생성
            img = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        else:
            img = cv2.resize(img, (self.frame_width, self.frame_height))
        
        # OpenCV(BGR) -> Gradio(RGB)로 미리 변환 (그리기 로직에서 색상 꼬임 방지)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def _get_storeData(self):
        """
        (백엔드 로직) 데이터 저장소에서 데이터 불러오는 메서드
        """
        all_data = data_store.get_data()
        if not all_data:
            return None, None, []
        
        target_id = next(iter(all_data))
        target_data = all_data[target_id]

        timestamp = target_data.get("timestamp", "Unknown Time")
        camera_id = target_data.get("camera_id", target_id)
        detected_objects = target_data.get("objects", [])
      
        return timestamp,camera_id,detected_objects

    def _draw_annotations(self, frame, detections):
        """
        (그래픽 로직) 이미지에 박스와 텍스트를 그리는 메서드
        """
        # 원본을 보존하기 위해 복사본 생성
        annotated_frame = frame.copy()
        
        for obj in detections:
            x, y, w, h = obj['bbox']
            x1 = int(x-w/2)
            y1 = int(y-h/2)
            x2 = int(x+w/2)
            y2 = int(y+h/2)
            color = self.colors
            label = f"{obj['confidence']} (ID:{obj['object_id']})"
            
            # 사각형 그리기
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # 텍스트 그리기
            cv2.putText(annotated_frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        return annotated_frame

    def update_dashboard(self):
        """
        (인터페이스) Gradio Timer에 의해 주기적으로 호출되는 메인 루프
        """
        # 1. 데이터 불러오기
        current_time,camera_id,detections = self._get_storeData()

        # 2. 데이터가 아직 없을 때
        if current_time is None:
            return "연결 대기중...", [["-", 0, "데이터 없음"]], self.base_frame

        # 3. 이미지 처리
        final_image = self._draw_annotations(self.base_frame, detections)
        
        # 4. 통계 데이터 가공
        count = len(detections)
    
        if count > 0:
            # "사람"이라는 이름은 고정하고 개수만 넣음
            summary_data = [["사람", count, camera_id]] 
        else:
            summary_data = [["탐지 없음", 0, camera_id]]
            
        return current_time, summary_data, final_image

    def create_ui(self):
        """
        (UI 레이아웃) Gradio 인터페이스 구성
        """
        with gr.Blocks(title="AI 영상 관제 (Class Ver)") as demo:
            gr.Markdown("## 📹 객체 지향 영상 관제 시스템")
            
            with gr.Row():
                # 왼쪽 패널
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 탐지 요약")
                    self.ui_time = gr.Textbox(label="시스템 시간", interactive=False)
                    self.ui_table = gr.Dataframe(
                        headers=["객체 종류", "수량","사용된 보드"],
                        datatype=["str", "number","str"],
                        interactive=False
                    )

                # 오른쪽 패널 (영상)
                with gr.Column(scale=3):
                    gr.Markdown("### 🔴 실시간 탐지 화면")
                    self.ui_image = gr.Image(
                        label="Real-time Feed", 
                        interactive=False,
                        height=720
                    )

            # 타이머 설정
            timer = gr.Timer(1)
            timer.tick(
                fn=self.update_dashboard,
                inputs=None,
                outputs=[self.ui_time, self.ui_table, self.ui_image]
            )
            
        return demo

# ------------------------------------------------
# 실행부
# ------------------------------------------------
if __name__ == "__main__":
    # 시스템 인스턴스 생성
    system = Gradio_ui(image_path="test_image.jpg")
    
    # UI 빌드 및 실행
    demo = system.create_ui()
    demo.launch()
import gradio as gr
import random
import time
from datetime import datetime
from collections import Counter
import cv2
import numpy as np

# ------------------------------------------------
# 1. 데이터 및 이미지 처리 로직 (백엔드)
# ------------------------------------------------
def update_dashboard():
    # A. 현재 시간 구하기
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # -----------------------------------------------------
    # B. (가상) 이미지 및 탐지 데이터 생성
    # -----------------------------------------------------
    # 1. 가상의 빈 이미지 생성 (검은색 배경, 1280x720 해상도)
    # 실제 환경에서는 카메라에서 프레임을 받아옵니다: frame = camera.read()
    frame_height, frame_width = 720, 1280
    # numpy를 이용해 검은색(0)으로 채워진 3채널(RGB) 배열 생성
    #dummy_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    image_path = "test_image.jpg"
    dummy_frame = cv2.imread(image_path)

    if dummy_frame is None:
        dummy_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
    else:
        dummy_frame = cv2.resize(dummy_frame, (frame_width, frame_height))

    # 2. 가상의 탐지 데이터 생성 (박스 좌표 포함)
    possible_classes = ["person", "car", "bus"]
    detected_objects = []
    
    # 랜덤 색상 정의 (박스 그리기용)
    colors = [(0, 255, 0), (0, 0, 255), (255, 0, 0)] # Green, Red, Blue

    for i in range(random.randint(1, 5)): # 1~5개 랜덤 탐지
        obj_class = random.choice(possible_classes)
        obj_id = 100 + i
        
        # 랜덤 바운딩 박스 좌표 생성 (x1, y1, x2, y2)
        x1 = random.randint(50, frame_width - 200)
        y1 = random.randint(50, frame_height - 200)
        w = random.randint(50, 150) # 박스 너비
        h = random.randint(100, 300) # 박스 높이
        x2 = x1 + w
        y2 = y1 + h
        
        detected_objects.append({"class": obj_class})

        # -----------------------------------------------------
        # C. OpenCV로 이미지에 그리기
        # -----------------------------------------------------
        color = colors[i % len(colors)] # 객체별로 다른 색상 선택
        
        # 1. 사각형 그리기 (이미지, 시작좌표, 끝좌표, 색상, 선두께)
        cv2.rectangle(dummy_frame, (x1, y1), (x2, y2), color, 2)
        
        # 2. 라벨 및 ID 텍스트 추가
        label_text = f"{obj_class} (ID:{obj_id})"
        # 텍스트 그리기 (이미지, 텍스트, 위치, 폰트, 크기, 색상, 두께)
        cv2.putText(dummy_frame, label_text, (x1, y1 - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    # D. [창 1용] 요약 데이터 가공
    class_counts = Counter([obj['class'] for obj in detected_objects])
    summary_data = [[k, v] for k, v in class_counts.items()]
    if not summary_data:
        summary_data = [["탐지 없음", 0]]

    # OpenCV는 기본적으로 BGR 순서이므로, Gradio(RGB)에 맞게 색상 변환
    final_image = cv2.cvtColor(dummy_frame, cv2.COLOR_BGR2RGB)

    # 세 가지 값을 리턴 (시간, 요약표, **그림 그려진 이미지**)
    return current_time, summary_data, final_image

# ------------------------------------------------
# 2. UI 구성 (프론트엔드)
# ------------------------------------------------
with gr.Blocks(title="AI 영상 관제") as demo:
    gr.Markdown("## 📹 실시간 영상 관제 시스템")
    
    with gr.Row():
        # --- [창 1] 왼쪽: 시간 및 요약 (기존 유지) ---
        with gr.Column(scale=1):
            gr.Markdown("### 📊 탐지 요약")
            time_display = gr.Textbox(label="시스템 시간", interactive=False)
            summary_table = gr.Dataframe(
                headers=["객체 종류", "수량"],
                datatype=["str", "number"],
                interactive=False
            )

        # --- [창 2] 오른쪽: 실시간 영상 화면 (변경됨!) ---
        with gr.Column(scale=3): # 영상을 더 크게 보여주기 위해 scale을 키움
            gr.Markdown("### 🔴 실시간 탐지 화면")
            # 여기가 핵심 변경점: Dataframe 대신 Image 사용
            # interactive=False로 설정하여 사용자가 이미지를 수정 못하게 함
            detect_image_output = gr.Image(
                label="YOLO Detection Result", 
                interactive=False,
                height=720 # 화면 높이 고정 (선택사항)
            )

    # ------------------------------------------------
    # 3. 자동 갱신 (타이머)
    # ------------------------------------------------
    # 1초마다 함수 실행 후, 결과 3개를 순서대로 UI 컴포넌트에 전달
    timer = gr.Timer(1)
    timer.tick(
        fn=update_dashboard, 
        inputs=None, 
        outputs=[time_display, summary_table, detect_image_output]
    )

demo.launch()

import gradio as gr
import cv2
import numpy as np
import time
from datetime import datetime

# ------------------------------------------------
# 1. 영상 데이터 생성 로직 (백엔드)
# ------------------------------------------------
def generate_frame(cam_id, width=640, height=480):
    """
    가상의 카메라 영상을 생성하는 함수
    cam_id에 따라 박스 색상과 텍스트 위치를 다르게 해서 구분함
    """
    # 배경 생성 (검은색)
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    
    # 카메라마다 다른 색상 지정
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)] # R, G, B, Cyan
    color = colors[(cam_id - 1) % 4]
    
    # 움직이는 박스 효과 (시간에 따라 위치 이동)
    t = time.time()
    x = int((np.sin(t + cam_id) + 1) / 2 * (width - 100))
    y = int((np.cos(t + cam_id) + 1) / 2 * (height - 100))
    
    cv2.rectangle(frame, (x, y), (x+50, y+50), color, -1)
    
    # 카메라 번호와 시간 표시
    time_str = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, f"CAM {cam_id} - {time_str}", (20, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # 색상 공간 변환 (BGR -> RGB) - Gradio는 RGB를 씁니다.
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

def update_feeds():
    """
    모든 카메라의 프레임을 한 번에 생성해서 리턴하는 함수
    리턴 순서: [캠1, 캠2, 캠3, 캠4, (확대용)캠1, (확대용)캠2, (확대용)캠3, (확대용)캠4]
    """
    f1 = generate_frame(1)
    f2 = generate_frame(2)
    f3 = generate_frame(3)
    f4 = generate_frame(4)
    
    # Gradio 컴포넌트 순서에 맞춰서 리턴 (전체보기용 4개 + 개별보기용 4개)
    # 실제로는 개별보기용은 선택된 것만 보여주면 되지만, 코드 단순화를 위해 다 보냄
    return f1, f2, f3, f4, f1, f2, f3, f4

# ------------------------------------------------
# 2. UI 구성 (레이아웃)
# ------------------------------------------------
with gr.Blocks(title="CCTV 관제 센터") as demo:
    gr.Markdown("## 🏢 통합 보안 관제 시스템")
    
    # === [A] 상단 제어 버튼 ===
    with gr.Row():
        btn_all = gr.Button("田 전체 보기", variant="primary")
        btn_1 = gr.Button("1번 카메라")
        btn_2 = gr.Button("2번 카메라")
        btn_3 = gr.Button("3번 카메라")
        btn_4 = gr.Button("4번 카메라")

    # === [B] 화면 영역 1: 전체 보기 (Grid) ===
    # visible=True (처음엔 보임)
    with gr.Column(visible=True) as group_grid:
        gr.Markdown("### 📸 전체 모니터링")
        with gr.Row():
            cam1_grid = gr.Image(label="CAM 1", interactive=False, height=300)
            cam2_grid = gr.Image(label="CAM 2", interactive=False, height=300)
        with gr.Row():
            cam3_grid = gr.Image(label="CAM 3", interactive=False, height=300)
            cam4_grid = gr.Image(label="CAM 4", interactive=False, height=300)

    # === [C] 화면 영역 2: 개별 보기 (Single) ===
    # visible=False (처음엔 숨김)
    with gr.Column(visible=False) as group_single:
        # 상태 메시지
        single_title = gr.Markdown("### 🔍 개별 카메라 상세")
        
        # 4개의 이미지 컴포넌트를 미리 만들어두고, 선택된 것만 visible=True로 켬
        # (하나의 Image 컴포넌트에 소스만 바꾸는 것보다, 레이아웃 안정성이 좋음)
        cam1_full = gr.Image(label="CAM 1 상세", interactive=False, height=600, visible=False)
        cam2_full = gr.Image(label="CAM 2 상세", interactive=False, height=600, visible=False)
        cam3_full = gr.Image(label="CAM 3 상세", interactive=False, height=600, visible=False)
        cam4_full = gr.Image(label="CAM 4 상세", interactive=False, height=600, visible=False)

    # ------------------------------------------------
    # 3. 버튼 이벤트 핸들러 (화면 전환 로직)
    # ------------------------------------------------
    # 리턴값 순서: [전체그룹, 개별그룹, 개별1, 개별2, 개별3, 개별4] 의 visible 속성
    
    def show_all():
        return (
            gr.update(visible=True),  # Grid 그룹 보이기
            gr.update(visible=False), # Single 그룹 숨기기
            gr.update(visible=False), gr.update(visible=False), 
            gr.update(visible=False), gr.update(visible=False)
        )

    def show_cam1():
        return (
            gr.update(visible=False), # Grid 그룹 숨기기
            gr.update(visible=True),  # Single 그룹 보이기
            gr.update(visible=True),  # Cam1 보이기
            gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)
        )

    def show_cam2():
        return (gr.update(visible=False), gr.update(visible=True),
                gr.update(visible=False), gr.update(visible=True), # Cam2 보이기
                gr.update(visible=False), gr.update(visible=False))

    def show_cam3():
        return (gr.update(visible=False), gr.update(visible=True),
                gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=True),  # Cam3 보이기
                gr.update(visible=False))

    def show_cam4():
        return (gr.update(visible=False), gr.update(visible=True),
                gr.update(visible=False), gr.update(visible=False),
                gr.update(visible=False), 
                gr.update(visible=True))  # Cam4 보이기

    # 버튼 클릭 시 함수 연결
    outputs_list = [group_grid, group_single, cam1_full, cam2_full, cam3_full, cam4_full]
    
    btn_all.click(show_all, inputs=None, outputs=outputs_list)
    btn_1.click(show_cam1, inputs=None, outputs=outputs_list)
    btn_2.click(show_cam2, inputs=None, outputs=outputs_list)
    btn_3.click(show_cam3, inputs=None, outputs=outputs_list)
    btn_4.click(show_cam4, inputs=None, outputs=outputs_list)

    # ------------------------------------------------
    # 4. 영상 자동 갱신 (타이머)
    # ------------------------------------------------
    # 화면에 보이든 안 보이든 백그라운드에서 모든 컴포넌트에 최신 프레임을 쏴줍니다.
    # (Gradio는 visible=False인 컴포넌트에 데이터를 보내도 에러가 나지 않고 무시합니다)
    timer = gr.Timer(0.1) # 0.1초마다 갱신
    
    timer.tick(
        fn=update_feeds,
        inputs=None,
        outputs=[cam1_grid, cam2_grid, cam3_grid, cam4_grid, 
                 cam1_full, cam2_full, cam3_full, cam4_full]
    )

demo.launch()

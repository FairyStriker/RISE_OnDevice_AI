from ultralytics import YOLO

# 1. 모델 로드 (학습된 모델 경로)
model = YOLO("yolov8n.pt")  # 또는 학습시킨 best.pt

# 2. 예측 실행 (source를 '0' 대신 '동영상 파일 경로'로 설정)
# show=True: 화면에 실시간으로 결과 표시
# save=True: 탐지된 결과가 그려진 동영상을 저장
results = model.predict(source="path/to/your/video.mp4", show=True, save=True)

# 스트림 처리 방식 (메모리 효율적)
# for result in model.predict(source="video.mp4", stream=True):
#     # 여기서 result.boxes 등을 이용해 후처리 로직 작성
#     pass

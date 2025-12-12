import cv2
import numpy as np
from rknn.api import RKNN

# 1. 파일 경로 설정 (방금 만든 norm 모델로 지정)
RKNN_MODEL = 'yolov8n_int8_norm.rknn'
IMG_PATH = './dataset/images/val/test.jpg' # ★실제 존재하는 이미지 경로로 꼭 수정하세요!★

# 2. RKNN 로드 및 시뮬레이션 환경 설정
rknn = RKNN()
print('--> Loading RKNN model')
ret = rknn.load_rknn(RKNN_MODEL)
if ret != 0:
    print('Load RKNN failed!')
    exit(ret)

print('--> Init runtime environment')
# target=None으로 하면 PC에서 시뮬레이션 모드로 동작합니다.
ret = rknn.init_runtime(target=None)
if ret != 0:
    print('Init runtime environment failed!')
    exit(ret)

# 3. 이미지 로드 및 전처리 (RGB 변환)
img = cv2.imread(IMG_PATH)
if img is None:
    print(f"Error: 이미지를 찾을 수 없습니다: {IMG_PATH}")
    exit(1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (640, 640))
# 모델 입력 형상에 맞게 차원 추가 (1, 640, 640, 3)
input_data = np.expand_dims(img, 0)

# 4. 추론 실행
print('--> Running inference')
outputs = rknn.inference(inputs=[input_data])

# 5. 결과 값 확인 (디버깅)
raw_output = outputs[0]
print(f"Output Shape: {raw_output.shape}")
print(f"Output Type: {raw_output.dtype}")

# 클래스 스코어 부분(4번째 인덱스 이후)의 최대값 찾기
# YOLOv8 출력 형상: (1, 8400, 84) 또는 (1, 5, 8400) 등 모델마다 다를 수 있음
# 값을 평탄화(flatten)해서 최대값이 0인지 아닌지 확인하는 게 제일 확실함
max_val = np.max(raw_output)
print("------------------------------------------------")
print(f"★ 전체 버퍼 내 최대값 (Overall Max): {max_val:.6f}")
print("------------------------------------------------")

if max_val < 0.001:
    print("❌ 결과: 모델 출력이 0입니다. 양자화(Export)가 잘못되었습니다.")
    print("   -> dataset.txt 이미지 경로나 std_values 설정을 다시 확인하세요.")
else:
    print("✅ 결과: 모델이 정상적인 값을 출력하고 있습니다!")
    print("   -> Odroid로 파일을 다시 전송(scp)하고 실행해 보세요.")

rknn.release()

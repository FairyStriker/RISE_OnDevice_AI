# config.py

DEVICE_NAME = "Nano"
# =================[ 입력 설정 (카메라) ]=================
# 1. RTSP 주소 (테스트용 VLC 또는 실제 IP 카메라)
INPUT_RTSP_URL = "rtsp://192.168.0.37:10554/stream"
# 임시 테스트용 (공개 RTSP 주소)
#INPUT_RTSP_URL = "rtsp://rtspstream:982b618641957297e6e58908d8176535@zephyr.rtsp.stream/pattern"

# 2. 입력 코덱 ("H264" 또는 "H265")
# - VLC 테스트: "H264" / IP카메라: 보통 "H265"
INPUT_CODEC = "H264"

# 3. 초기 모델 설정 파일 (처음 실행 시 사용할 파일)
# 업데이트가 되면 이 변수는 메모리 상에서 변경됩니다.
MODEL_CONFIG = "config_infer_primary_yoloV8.txt"


# =================[ 출력 설정 (영상 송출) ]=================
# 결과 영상 주소: rtsp://<Jetson_IP>:8554/ds-test
RTSP_OUT_PORT = "10555"
RTSP_OUT_PATH = f"/jetson_{DEVICE_NAME.lower()}"
INTERNAL_UDP_PORT = 5402


# =================[ 관제 센터 연결 설정 ]=================
# PC(Server)의 IP 주소
DATA_SERVER_IP = "192.168.0.37"
DATA_SERVER_PORT = 8000

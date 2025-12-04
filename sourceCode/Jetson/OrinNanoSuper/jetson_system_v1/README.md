# Jetson web monitoring
웹으로 b박스, 감지된 객체수, 시간을 확인할 수 있음

## 사용법
1. VLC로 스트리밍시작(IP카메라로 대체가능)
2. pc쪽 코드(main.py)를 실행
3. jetson쪽 코드(jetson_main.py)를 실행

## 설정해줘야 하는 값

- jetson_main.py
  - SERVER_IP
  - SERVER-PORT
  - CLIENT_ID
  - CAMERAS_CONFIG
  - YOLO모델
- main.py (pc쪽 코드)
  - port
  - 배경용 이미지

# OpenCV 4.11.0 Jetson Orin Nano 자동 설치 스크립트

## 시스템 요구사항
- NVIDIA Jetson Orin Nano
- JetPack 6.0 또는 6.1 (Ubuntu 22.04)
- 최소 10GB 여유 공간
- 인터넷 연결

## 제공 스크립트

### install_opencv_jetson.sh
- 단순하고 빠른 설치
- 자동 재부팅 포함 (10초 대기)
- 기본 에러 처리

## 사용 방법

# 실행 권한 부여
chmod +x install_opencv_jetson.sh

# 실행
./install_opencv_jetson.sh
```

## 설치 내용

### OpenCV 4.11.0
- CUDA 지원 활성화
- cuDNN 지원
- GStreamer 지원
- TBB 멀티스레딩
- Python3 바인딩
- C++ 지원

### CUDA 설정
- CUDA Compute Capability: 8.7 (Orin Nano Ampere)
- CUDA Fast Math 활성화
- DNN CUDA 백엔드

### 추가 도구
- jtop (Jetson 모니터링 도구)

## 설치 시간
- 전체 설치: 약 2-3시간
- 컴파일: 대부분의 시간 소요

## 설치 확인

```python
import cv2
print(f"OpenCV Version: {cv2.__version__}")
print(f"CUDA Support: {cv2.cuda.getCudaEnabledDeviceCount() > 0}")
```

```bash
# jtop 실행
jtop
```

## 문제 해결

### 메모리 부족
```bash
# swap 파일 추가 (8GB)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 컴파일 실패
- CPU 코어 수 줄이기: `make -j2` 
- 메모리 모니터링: `free -h`
- 온도 확인: `sudo jtop`

### CUDA 미검출
```bash
# CUDA 경로 확인
ls /usr/local/cuda
nvcc --version

# 환경 변수 설정
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

## 제거 방법

```bash
# OpenCV 제거
sudo apt-get purge libopencv* python3-opencv
sudo apt-get autoremove

# 수동 설치 파일 제거
sudo rm -rf /usr/include/opencv4
sudo rm -rf /usr/lib/libopencv*
sudo rm -rf /usr/lib/python3/dist-packages/cv2*
```

## 주의사항
- 설치 중 시스템이 느려질 수 있음
- 충분한 냉각 확보 필요
- 전원 연결 상태 유지
- 설치 중단 시 `cd ~/opencv_build/opencv/build && sudo make install` 로 재개 가능

## 로그 위치
향상된 버전 사용 시:
- `~/opencv_install_YYYYMMDD_HHMMSS.log`

## 지원
문제 발생 시 로그 파일과 함께 문의

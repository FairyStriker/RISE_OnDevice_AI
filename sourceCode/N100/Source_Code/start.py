import subprocess
import time
import os
import glob
import sys
import signal

# ==========================================
# [경로 설정]
# ==========================================
VIDEO_DIR = "/home/n100/Videos/haeundae"
SERVER_SCRIPT = "/home/n100/works/web.py"
# ==========================================

flask_process = None
vlc_process = None

def cleanup_processes(signum=None, frame=None):
    print("\n\n[System] 서버를 종료합니다...")
    if flask_process: flask_process.terminate()
    if vlc_process: vlc_process.terminate()
    subprocess.run(["pkill", "-f", "vlc"], stderr=subprocess.DEVNULL)
    sys.exit(0)

def main():
    global flask_process, vlc_process
    signal.signal(signal.SIGINT, cleanup_processes)
    signal.signal(signal.SIGTERM, cleanup_processes)

    print("="*50)
    print("N100 AI 통합 서버")
    print("="*50)

    # 1. 정리
    subprocess.run(["pkill", "-f", "app.py"])
    subprocess.run(["pkill", "-f", "vlc"])
    time.sleep(1)

    # 2. 웹 서버 실행
    print(f"1. 웹 서버 시작: {SERVER_SCRIPT}")
    if not os.path.exists(SERVER_SCRIPT):
        print(f"[Error] 파일 없음: {SERVER_SCRIPT}")
        return

    flask_process = subprocess.Popen(
        ["python3", SERVER_SCRIPT],
        stdout=subprocess.DEVNULL,
        stderr=sys.stderr
    )
    time.sleep(2)

    # 3. VLC 실행
    print(f"2. 영상 송출 시작 (폴더: {VIDEO_DIR})")
    video_files = glob.glob(os.path.join(VIDEO_DIR, "*.mp4"))
    video_files.sort()

    if not video_files:
        print("[Error] 영상 파일이 없습니다.")
        cleanup_processes()

    # ==================================================================
    # [핵심 수정] VLC 명령어: 강제 트랜스코딩 (Transcode) 적용
    # 어떤 영상이든 640x640 해상도의 H.264로 변환하여 하나의 스트림처럼 만듦
    # ==================================================================
    vlc_cmd = [
        "cvlc", 
        "-I", "dummy", 
        "-vvv"
    ] + video_files + [
        # --sout-all: 재생목록의 모든 스트림 유지
        "--sout-all",
        # --sout-keep: 파일 변경 시 파이프 유지
        "--sout-keep",
        # --repeat / --loop: 무한 반복
        "--loop",
        # [중요] transcode 모듈 사용: width=640, height=640으로 고정
        "--sout", 
        "#transcode{vcodec=h264,acodec=none,width=640,height=640,fps=30,vb=2000}:rtp{sdp=rtsp://:8554/test}"
    ]

    try:
        vlc_process = subprocess.Popen(
            vlc_cmd,
            stdout=subprocess.DEVNULL,
            stderr=sys.stderr
        )
    except Exception as e:
        print(f"[Error] VLC 실행 실패: {e}")
        cleanup_processes()

    print("\n" + "="*50)
    print("스트리밍 시작")
    print("   👉 RTSP: rtsp://192.168.0.52:8554/test")
    print("="*50)

    while True:
        time.sleep(1)
        if flask_process.poll() is not None:
            print("[Error] 웹 서버 종료됨")
            break
        if vlc_process.poll() is not None:
            print("[Error] VLC 종료됨")
            break

    cleanup_processes()

if __name__ == "__main__":
    main()

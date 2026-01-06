import os
import config
from data_sender import DataSender
from rtsp_server import RTSPStreamingServer
from pipeline import DeepStreamPipeline
from command_receiver import CommandReceiver

def main():
    print("=== [Jetson Orin Smart Edge] 시스템 시작 ===")
    
    # 1. 통신 모듈
    sender = DataSender()

    # 2. RTSP 서버 (백그라운드)
    rtsp_server = RTSPStreamingServer(
        port=config.RTSP_OUT_PORT,
        path=config.RTSP_OUT_PATH,
        internal_port=config.INTERNAL_UDP_PORT
    )

    # 3. AI 파이프라인
    app = DeepStreamPipeline(data_sender=sender)
    
    # 4. 원격 제어 수신 (앱 객체 전달)
    cmd_receiver = CommandReceiver(pipeline_obj=app)
    
    # 5. 무한 실행
    app.start()

if __name__ == "__main__":
    main()

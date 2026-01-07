import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer

class RTSPStreamingServer(GstRtspServer.RTSPServer):
    def __init__(self, port, path, internal_port):
        super().__init__()
        self.set_service(port)
        factory = GstRtspServer.RTSPMediaFactory()
        
        # 내부 UDP -> 외부 RTSP (H.264)
        # [수정] buffer-size를 5242880 (5MB)로 대폭 증가하여 패킷 손실 방지
        launch_str = (
            f"( udpsrc name=pay0 port={internal_port} buffer-size=5242880 "
            "caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)H264, payload=96 \" )"
        )
        factory.set_launch(launch_str)
        factory.set_shared(True)
        self.get_mount_points().add_factory(path, factory)
        print(f"📡 [RTSP Server] 방송 중: rtsp://<Jetson_IP>:{port}{path}")
        self.attach(None)

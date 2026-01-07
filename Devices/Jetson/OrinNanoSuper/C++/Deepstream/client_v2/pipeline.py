import sys
import time
import datetime
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import pyds
import config

class DeepStreamPipeline:
    def __init__(self, data_sender):
        Gst.init(None)
        self.sender = data_sender
        self.pipeline = None
        self.loop = None
        self.restart_flag = False
        self.fps_start = time.time()
        self.frame_count = 0
        self.current_fps = 0.0

    def request_restart(self):
        """외부에서 모델 변경 시 호출하여 파이프라인을 재기동함"""
        print("🔄 [Pipeline] 재시작 신호 수신 중...")
        self.restart_flag = True
        if self.loop:
            self.loop.quit() # 실행 중인 메인 루프를 종료시켜 start()의 다음 loop로 넘김

    def _create_pipeline(self):
        pipeline = Gst.Pipeline()

        # 1. Input (자동 감지)
        source = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
        source.set_property("uri", config.INPUT_RTSP_URL)
        
        # 2. StreamMux (추론용 해상도 고정)
        streammux = Gst.ElementFactory.make("nvstreammux", "streammux")
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batch-size", 1)
        streammux.set_property("live-source", 1)

        # 3. Inference & OSD
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        pgie.set_property("config-file-path", config.MODEL_CONFIG)
        nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convert1")
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")

        # 4. Output (Orin Nano 필수 소프트웨어 인코더 설정)
        nvvidconv2 = Gst.ElementFactory.make("nvvideoconvert", "convert2")
        capsfilter = Gst.ElementFactory.make("capsfilter", "caps")
        capsfilter.set_property("caps", Gst.Caps.from_string("video/x-raw, format=I420"))
        
        # x264enc 옵션을 더 가볍게 조정
        encoder = Gst.ElementFactory.make("x264enc", "encoder")
        encoder.set_property("tune", "zerolatency")
        encoder.set_property("speed-preset", "ultrafast")
        encoder.set_property("bitrate", 1000) # 대역폭을 1MB로 낮춰 안정성 확보
        encoder.set_property("key-int-max", 30)

        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        
        # udpsink 설정 (제트슨 내부 RTSP 서버로 던짐)
        udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
        udpsink.set_property("host", "127.0.0.1")
        udpsink.set_property("port", config.INTERNAL_UDP_PORT) # 이 포트가 RTSP 서버 포트와 맞아야 함
        udpsink.set_property("async", False)
        udpsink.set_property("sync", 0)

        # 엘리먼트 추가 및 연결
        elements = [source, streammux, pgie, nvvidconv1, nvosd, 
                    nvvidconv2, capsfilter, encoder, rtppay, udpsink]
        for e in elements: pipeline.add(e)

        source.connect("pad-added", self._on_pad_added, streammux)
        streammux.link(pgie)
        pgie.link(nvvidconv1)
        nvvidconv1.link(nvosd)
        nvosd.link(nvvidconv2)
        nvvidconv2.link(capsfilter)
        capsfilter.link(encoder)
        encoder.link(rtppay)
        rtppay.link(udpsink)

        nvosd.get_static_pad("sink").add_probe(Gst.PadProbeType.BUFFER, self._probe_callback, 0)
        return pipeline

    def _on_pad_added(self, src, pad, target):
        caps = pad.get_current_caps()
        name = caps.get_structure(0).get_name()
        if "video" in name:
            sink_pad = target.get_request_pad("sink_0")
            if not sink_pad.is_linked():
                pad.link(sink_pad)

    def _update_fps(self):
        self.frame_count += 1
        now = time.time()
        if now - self.fps_start >= 1:
            self.current_fps = self.frame_count / (now - self.fps_start)
            self.frame_count = 0
            self.fps_start = now
        return round(self.current_fps, 1)

    def _probe_callback(self, pad, info, u_data):
        gst_buffer = info.get_buffer()
        if not gst_buffer: return Gst.PadProbeReturn.OK
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        l_frame = batch_meta.frame_meta_list
        while l_frame is not None:
            try: frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration: break
            frame_data = {"timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                          "fps": self._update_fps(), "frame_num": frame_meta.frame_num, "objects": []}
            l_obj = frame_meta.obj_meta_list
            while l_obj is not None:
                try: obj = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration: break
                frame_data["objects"].append({"id": obj.object_id, "class_id": obj.class_id, "confidence": round(obj.confidence, 2),
                                              "bbox": [int(obj.rect_params.left), int(obj.rect_params.top),
                                                       int(obj.rect_params.width), int(obj.rect_params.height)]})
                try: l_obj = l_obj.next
                except StopIteration: break
            if frame_data["objects"]:
                # 데이터 전송 (이미 웹에서 보인다면 이 부분은 정상 작동 중)
                self.sender.send(frame_data)
            try: l_frame = l_frame.next
            except StopIteration: break
        return Gst.PadProbeReturn.OK

    def bus_call(self, bus, message, loop):
        t = message.type
        if t == Gst.MessageType.EOS: loop.quit()
        elif t == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            print(f"⚠️ [Stream Error] {err}")
            loop.quit()
        return True

    def start(self):
        while True:
            try:
                self.restart_flag = False
                print(f"🚀 [Pipeline] 모델 적용 시작: {os.path.basename(config.MODEL_CONFIG)}")
                self.pipeline = self._create_pipeline()
                self.loop = GLib.MainLoop()
                bus = self.pipeline.get_bus()
                bus.add_signal_watch()
                bus.connect("message", self.bus_call, self.loop)
                self.pipeline.set_state(Gst.State.PLAYING)
                self.loop.run()
                self.pipeline.set_state(Gst.State.NULL)
                print("💤 [Pipeline] 파이프라인 정리 및 재기동 준비...")
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 오류: {e}"); time.sleep(5)

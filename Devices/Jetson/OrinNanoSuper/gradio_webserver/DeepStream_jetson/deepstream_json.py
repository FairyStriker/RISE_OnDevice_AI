import sys
import time
from datetime import datetime
import gi

gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import pyds
from jetson_comms import JetsonSender

# =================[ 설정 ]=================
RTSP_URL = "rtsp://ksj.local:10554/stream"
SERVER_IP = "ksj.local"
CONFIG_FILE = "config_infer_primary_yoloV8.txt"
CLIENT_ID = "Jetson_Orin"

# 1. Jetson에서 처리하는 해상도 (화면 출력용)
#    (너무 크면 느려지니 1280x720 정도가 적당합니다)
MUX_WIDTH = 1280
MUX_HEIGHT = 720

# 2. 서버로 보낼 때 변환할 기준 해상도 (FHD)
TARGET_WIDTH = 1920
TARGET_HEIGHT = 1080
# ==========================================

sender = JetsonSender(SERVER_IP, 8000, CLIENT_ID)

def osd_sink_pad_buffer_probe(pad, info, u_data):
    gst_buffer = info.get_buffer()
    if not gst_buffer: return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    while l_frame is not None:
        try: frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration: break

        if frame_meta.num_obj_meta > 0:
            objects = []
            l_obj = frame_meta.obj_meta_list
            while l_obj is not None:
                try: obj = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration: break
                
                if obj.class_id == 0: # 사람
                    # ★ 좌표 변환 로직 (Scaling) ★
                    # 현재 좌표(MUX) -> 목표 좌표(FHD)로 변환
                    scale_x = TARGET_WIDTH / MUX_WIDTH
                    scale_y = TARGET_HEIGHT / MUX_HEIGHT

                    # 1. 원본 좌표 가져오기
                    left = obj.rect_params.left
                    top = obj.rect_params.top
                    width = obj.rect_params.width
                    height = obj.rect_params.height

                    # 2. 비율 곱해서 늘리기
                    fhd_left = int(left * scale_x)
                    fhd_top = int(top * scale_y)
                    fhd_width = int(width * scale_x)
                    fhd_height = int(height * scale_y)

                    objects.append({
                        "object_id": obj.object_id,
                        "confidence": round(obj.confidence, 2),
                        # 변환된 FHD 좌표를 넣음
                        "bbox": [fhd_left, fhd_top, fhd_width, fhd_height]
                    })
                try: l_obj = l_obj.next
                except StopIteration: break

            if objects:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"🚀 [전송] {now} | 사람 {len(objects)}명 (좌표 FHD 변환됨)")
                try:
                    sender.send_data({
                        "timestamp": now, 
                        "camera_id": CLIENT_ID, 
                        "count": len(objects), 
                        "objects": objects
                    })
                except: pass
        try: l_frame = l_frame.next
        except StopIteration: break
    return Gst.PadProbeReturn.OK

def main():
    Gst.init(None)

    # 파이프라인 (화면은 1280x720으로 쾌적하게 보고, 데이터는 1920x1080으로 뻥튀기해서 보냄)
    pipeline_str = (
        f"rtspsrc location={RTSP_URL} latency=200 ! "
        "decodebin ! "
        "nvvideoconvert ! "
        f"m.sink_0 nvstreammux name=m batch-size=1 width={MUX_WIDTH} height={MUX_HEIGHT} live-source=1 ! "
        f"nvinfer config-file-path={CONFIG_FILE} ! "
        "nvvideoconvert ! "
        "video/x-raw(memory:NVMM), format=RGBA ! " 
        "nvdsosd ! "
        "nv3dsink sync=false"
    )

    print(f"[{CLIENT_ID}] 시스템 가동... (화면: {MUX_WIDTH}x{MUX_HEIGHT} -> 전송: {TARGET_WIDTH}x{TARGET_HEIGHT})")
    pipeline = Gst.parse_launch(pipeline_str)

    nvinfer = pipeline.get_by_name("nvinfer0")
    if not nvinfer:
        it = pipeline.iterate_elements()
        while True:
            res, elem = it.next()
            if res != Gst.IteratorResult.OK: break
            if "nvinfer" in elem.get_factory().get_name():
                nvinfer = elem; break

    if nvinfer:
        sink_pad = nvinfer.get_static_pad("src")
        sink_pad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    loop = GLib.MainLoop()
    pipeline.set_state(Gst.State.PLAYING)
    
    try:
        loop.run()
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        pass
    pipeline.set_state(Gst.State.NULL)

if __name__ == '__main__':
    main()

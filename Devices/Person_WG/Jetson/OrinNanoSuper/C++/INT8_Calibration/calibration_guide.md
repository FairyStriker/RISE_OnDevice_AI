git clone https://github.com/marcoslucianops/DeepStream-Yolo

yolo export model=yolov8n_fp32.pt format=onnx opset=13 simplify=True 
yolo export model=yolov8s_fp32.pt format=onnx opset=13 simplify=True
yolo export model=yolov8m_fp32.pt format=onnx opset=13 simplify=True
yolo export model=yolov8l_fp32.pt format=onnx opset=13 simplify=True

/usr/src/tensorrt/bin/trtexec --onnx=yolov8n_fp32_opset13.onnx \
        --int8 \
        --fp16 \
        --calib=yolov8n_int8.cache \
        --saveEngine=yolov8n_int8.engine

/usr/src/tensorrt/bin/trtexec --onnx=yolov8s_fp32_opset13.onnx \
        --int8 \
        --fp16 \
        --calib=yolov8s_int8.cache \
        --saveEngine=yolov8s_int8.engine

/usr/src/tensorrt/bin/trtexec --onnx=yolov8m_fp32_opset13.onnx \
        --int8 \
        --fp16 \
        --calib=yolov8m_int8.cache \
        --saveEngine=yolov8m_int8.engine

/usr/src/tensorrt/bin/trtexec --onnx=yolov8l_fp32_opset13.onnx \
        --int8 \
        --fp16 \
        --calib=yolov8l_int8.cache \
        --saveEngine=yolov8l_int8.engine

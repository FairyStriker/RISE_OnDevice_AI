### == YOLOv8 OpenCV-Python Benchmark Results on Jetson AGX Orin ==
#### FP16

| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1_Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.5915 | 0.8794 | 0.8124 | 0.8174 | 0.8075 | 36.02 | 5.11 |
| **YOLOv8s** | FP16 | 640x640 | 0.6268 | 0.8922 | 0.8269 | 0.8324 | 0.8215 | 31.68 | 9.07 |
| **YOLOv8m** | FP16 | 640x640 | 0.6402 | 0.8974 | 0.8318 | 0.8323 | 0.8313 | 23.66 | 20.08 |
| **YOLOv8l** | FP16 | 640x640 | 0.6460 | 0.8972 | 0.8311 | 0.8363 | 0.8260 | 18.66 | 31.29 |

#### INT8

| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1_Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.5473 | 0.8719 | 0.8051 | 0.8095 | 0.8009 | 38.30 | 3.90 |
| **YOLOv8s** | INT8 | 640x640 | 0.4798 | 0.8442 | 0.7883 | 0.7823 | 0.7945 | 35.36 | 5.93 |
| **YOLOv8m** | INT8 | 640x640 | 0.3849 | 0.7734 | 0.7417 | 0.7096 | 0.7769 | 28.87 | 12.25 |
| **YOLOv8l** | INT8 | 640x640 | 0.4314 | 0.8003 | 0.7610 | 0.7337 | 0.7903 | 25.00 | 17.92 |

> **Note**
> * **Platform:** JetsonOrinNanoSuper Developer Kit (aarch64)
> * OS = Ubuntu 20.04 Jetpack 5.1.5
> * **Date:** 2026-01-07
> * **Conf** = 0.2 / **IoU** = 0.5

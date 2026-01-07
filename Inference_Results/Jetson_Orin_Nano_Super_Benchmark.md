### == YOLOv8(*.engine) OpenCV-Python Benchmark Results on Jetson Orin Nano Super ==
#### FP16
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.632 | 0.867 | 0.8211 | 0.818 | 0.8237 | 32.82 | 30.47 |
| **YOLOv8s** | FP16 | 640x640 | 0.667 | 0.879 | 0.8335 | 0.8362 | 0.8308 | 25.43 | 39.33 |
| **YOLOv8m** | FP16 | 640x640 | 0.678 | 0.883 | 0.8387 | 0.8333 | 0.8441 | 21.70 | 46.08 |
| **YOLOv8l** | FP16 | 640x640 | 0.683 | 0.882 | 0.8374 | 0.8329 | 0.8419 | 20.13 | 49.67 |
#### INT8
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.590 | 0.857 | 0.8159 | 0.8132 | 0.8187 | 37.70 | 26.53 |
| **YOLOv8s** | INT8 | 640x640 | 0.532 | 0.872 | 0.8225 | 0.8279 | 0.8172 | 30.48 | 32.81 |
| **YOLOv8m** | INT8 | 640x640 | 0.441 | 0.859 | 0.8138 | 0.8135 | 0.8140 | 23.65 | 42.28 |
| **YOLOv8l** | INT8 | 640x640 | 0.454 | 0.865 | 0.8174 | 0.8154 | 0.8194 | 22.20 | 45.07 |

> **Note**
> * **Platform:** JetsonOrinNanoSuper Developer Kit (aarch64)
> * OS = Ubuntu 22.04 Jetpack 6.1
> * **Date:** 2025-12-10
> * **Conf** = 0.2 / **IoU** = 0.5

### == YOLOv8(rknn) C++ Benchmark Results on Odroid M1 ==
#### FP16
| Model | Quantization | Input Size | mAP(50) | F1 | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.7752 | 0.8104 | 0.8132 | 0.8076 | 8.27 | 120.96 |
| **YOLOv8s** | FP16 | 640x640 | 0.7002 | 0.8088 | 0.8351 | 0.7842 | 3.51 | 285.21 |
| **YOLOv8m** | FP16 | 640x640 | 0.7022 | 0.8156 | 0.8399 | 0.7926 | 1.45 | 689.27 |
| **YOLOv8l** | FP16 | 640x640 | 0.6983 | 0.8073 | 0.8412 | 0.7761 | 0.74 | 1350.00 |

> **Note**
> * **Platform:** Odroid M1
> * OS = Ubuntu 20.04
> * **Date:** 2025-12-05
> * **Conf** = 0.2 / **IoU** = 0.5

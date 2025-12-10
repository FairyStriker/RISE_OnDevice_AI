### 🚀 YOLOv8 Benchmark Results on Jetson Orin Nano

| Model | Precision | Input Size | mAP(50-95) | mAP(50) | FPS | Avg Inference (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640 | 0.632 | 0.867 | 32.82 | 30.47 |
| **YOLOv8s** | FP16 | 640 | 0.667 | 0.879 | 25.43 | 39.33 |
| **YOLOv8m** | FP16 | 640 | 0.678 | 0.883 | 21.70 | 46.08 |
| **YOLOv8l** | FP16 | 640 | 0.683 | 0.882 | 20.13 | 49.67 |
| **YOLOv8n** | INT8 | 640 | 0.590 | 0.857 | 37.70 | 26.53 |
| **YOLOv8s** | INT8 | 640 | 0.532 | 0.872 | 30.48 | 32.81 |
| **YOLOv8m** | INT8 | 640 | 0.441 | 0.859 | 23.65 | 42.28 |
| **YOLOv8l** | INT8 | 640 | 0.454 | 0.865 | 22.20 | 45.07 |

> **Note:**
> * **Platform:** Jetson (aarch64)
> * **Date:** 2025-12-09
> * **Conf Threshold:** 0.2, **IoU Threshold:** 0.5
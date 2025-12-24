### == YOLOv8 OpenCV-Python Benchmark Results on Jetson Orin Nano Super ==
| Model | Precision | Input Size | mAP(50-95) | mAP(50) | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.632 | 0.867 | 32.82 | 30.47 |
| **YOLOv8n** | INT8 | 640x640 | 0.590 | 0.857 | 37.70 | 26.53 |
| **YOLOv8s** | FP16 | 640x640 | 0.667 | 0.879 | 25.43 | 39.33 |
| **YOLOv8s** | INT8 | 640x640 | 0.532 | 0.872 | 30.48 | 32.81 |
| **YOLOv8m** | FP16 | 640x640 | 0.678 | 0.883 | 21.70 | 46.08 |
| **YOLOv8m** | INT8 | 640x640 | 0.441 | 0.859 | 23.65 | 42.28 |
| **YOLOv8l** | FP16 | 640x640 | 0.683 | 0.882 | 20.13 | 49.67 |
| **YOLOv8l** | INT8 | 640x640 | 0.454 | 0.865 | 22.20 | 45.07 |

> **Note**
> * **Platform:** JetsonOrinNanoSuper Developer Kit (aarch64)
> * OS = Jetpack6.1(rev1) + DeepStream7.1
> * **Date:** 2025-12-10
> * **Conf** = 0.2 / **IoU** = 0.5

[ HTTP Link ](https://gifts-represent-working-classification.trycloudflare.com/)

<img width="300" height="300" alt="Image" src="https://github.com/user-attachments/assets/a82d9883-16a3-4057-b56c-a16982d1f29a" />

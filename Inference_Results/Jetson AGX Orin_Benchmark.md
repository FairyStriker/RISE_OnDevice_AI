### == YOLOv8(engine) Benchmark Results Jetson AGX Orin ==
## FP16
| Model | Precision | Input Size | mAP(50) | F1 | Precision | Recall | FPS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.8632 | 0.819 | 0.931 | 0.84 | 44.56 |
| **YOLOv8s** | FP16 | 640x640 | 0.8738 | 0.8301 | 0.958 | 0.86 | 42.77 |
| **YOLOv8m** | FP16 | 640x640 | 0.8788 | 0.8342 | 0.949 | 0.86 | 37.33 |
| **YOLOv8l** | FP16 | 640x640 | 0.878 | 0.8344 | 0.969 | 0.86 | 33.13 |
## INT8
| Model | Precision | Input Size | mAP(50) | F1 | Precision | Recall | FPS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.8541 | 0.8144 | 0.918 | 0.82 | 45.43 |
| **YOLOv8s** | INT8 | 640x640 | 0.8638 | 0.8185 | 0.98 | 0.86 | 44.13 |
| **YOLOv8m** | INT8 | 640x640 | 0.8562 | 0.8106 | 0.99 | 0.87 | 40.17 |
| **YOLOv8l** | INT8 | 640x640 | 0.8599 | 0.8124 | 1.0 | 0.88 | 37.84 |

> **Note**
> * **Platform:** Jetson AGX Orin
> * OS = Ubuntu 22.04 Jetpack 6.1
> * **Date:** 2025-12-26
> * **Conf** = 0.2 / **IoU** = 0.5

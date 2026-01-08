### == YOLOv8(*.engine) OpenCV-Python Benchmark Results on Jetson Orin Nano Super ==

#### FP16
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.6014 | 0.8799 | 0.8134 | 0.8183 | 0.8085 | 18.23 | 14.31 |
| **YOLOv8s** | FP16 | 640x640 | 0.6380 | 0.8928 | 0.8276 | 0.8335 | 0.8218 | 16.51 | 19.67 |
| **YOLOv8m** | FP16 | 640x640 | 0.6524 | 0.8982 | 0.8324 | 0.8340 | 0.8308 | 14.16 | 27.01 |
| **YOLOv8l** | FP16 | 640x640 | 0.6593 | 0.8980 | 0.8321 | 0.8371 | 0.8271 | 11.28 | 39.04 |

#### INT8
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.5609 | 0.8740 | 0.8080 | 0.8151 | 0.8011 | 20.75 | 11.40 |
| **YOLOv8s** | INT8 | 640x640 | 0.4904 | 0.8492 | 0.7966 | 0.7869 | 0.8065 | 17.17 | 15.28 |
| **YOLOv8m** | INT8 | 640x640 | 0.3940 | 0.7848 | 0.7529 | 0.7198 | 0.7891 | 14.81 | 23.40 |
| **YOLOv8l** | INT8 | 640x640 | 0.4004 | 0.7716 | 0.7448 | 0.7017 | 0.7935 | 14.23 | 25.80 |

> **Note**
> * **Platform:** Jetson Orin Nano Super (aarch64)
> * OS = Ubuntu 22.04 Jetpack 6.1
> * **Date:** 2025-12-10
> * **Conf** = 0.2 / **IoU** = 0.5

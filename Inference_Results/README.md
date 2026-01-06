[ HTTP Link ](https://dated-roots-showed-publishing.trycloudflare.com/)

<img width="300" height="300" alt="Image" src="https://github.com/user-attachments/assets/2457a274-f845-46d1-9ed5-94b2b6e3db82" />

### == YOLOv8 OpenCV-Python Benchmark Results on Jetson Orin Nano Super ==
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
> * OS = Jetpack6.1(rev1) + DeepStream7.1
> * **Date:** 2025-12-10
> * **Conf** = 0.2 / **IoU** = 0.5

### == YOLOv8(engine) Benchmark Results Jetson AGX Orin ==
#### FP16
| Model | Quantization | Input Size | mAP(50) | F1 | Precision | Recall | FPS |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.8632 | 0.819 | 0.931 | 0.84 | 44.56 |
| **YOLOv8s** | FP16 | 640x640 | 0.8738 | 0.8301 | 0.958 | 0.86 | 42.77 |
| **YOLOv8m** | FP16 | 640x640 | 0.8788 | 0.8342 | 0.949 | 0.86 | 37.33 |
| **YOLOv8l** | FP16 | 640x640 | 0.878 | 0.8344 | 0.969 | 0.86 | 33.13 |
#### INT8
| Model | Quantization | Input Size | mAP(50) | F1 | Precision | Recall | FPS |
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

### == YOLOv8(rknn) C++ Benchmark Results on Odroid M1 ==
#### FP16
| Model | Quantization | Input Size | mAP(50) | F1 | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.7752 | 0.8104 | 0.8132 | 0.8076 | 8.27 | 120.96 |
| **YOLOv8s** | FP16 | 640x640 | 0.7002 | 0.8088 | 0.8351 | 0.7842 | 3.51 | 285.21 |
| **YOLOv8m** | FP16 | 640x640 | 0.7022 | 0.8156 | 0.8399 | 0.7926 | 1.45 | 689.27 |
| **YOLOv8l** | FP16 | 640x640 | 0.6983 | 0.8073 | 0.8412 | 0.7761 | 0.74 | 1350.00 |

### == YOLOv8 OpenCV-Python Benchmark Results on Rasberrypi 5 ==
|    Model    | Quantization | Input Size | mAP@50 | mAP@50-95 |   F1  | Precision | Recall |    FPS    |
| :---------: | :----------: | :--------: | :----: | :-------: | :---: | :-------: | :----: | :-------: |
| **YOLOv8n** |     FP32     |   640×640  |  0.313 |   0.100   | 0.364 |   0.449   |  0.309 | **76.11** |
| **YOLOv8s** |     FP32     |   640×640  |  0.892 |   0.647   | 0.829 |   0.833   |  0.826 | **29.16** |
| **YOLOv8m** |     FP32     |   640×640  |  0.883 |   0.624   | 0.820 |   0.820   |  0.820 |     —     |



> **Note**
> * **Platform:** Odroid M1
> * OS = Ubuntu 20.04
> * **Date:** 2025-12-05
> * **Conf** = 0.2 / **IoU** = 0.5

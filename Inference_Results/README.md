[ HTTP Link ](https://dated-roots-showed-publishing.trycloudflare.com/)

<img width="300" height="300" alt="Image" src="https://github.com/user-attachments/assets/2457a274-f845-46d1-9ed5-94b2b6e3db82" />

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
> * OS = Ubuntu 22.04 Jetpack 6.1 + DeepStream 7.1
> * **Date:** 2025-12-10
> * **Conf** = 0.2 / **IoU** = 0.5

### == YOLOv8(*.engine) OpenCV-Python Benchmark Results on Jetson AGX Xavier ==
#### FP16

| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.5915 | 0.8794 | 0.8124 | 0.8174 | 0.8075 | 36.02 | 5.11 |
| **YOLOv8s** | FP16 | 640x640 | 0.6268 | 0.8922 | 0.8269 | 0.8324 | 0.8215 | 31.68 | 9.07 |
| **YOLOv8m** | FP16 | 640x640 | 0.6402 | 0.8974 | 0.8318 | 0.8323 | 0.8313 | 23.66 | 20.08 |
| **YOLOv8l** | FP16 | 640x640 | 0.6460 | 0.8972 | 0.8311 | 0.8363 | 0.8260 | 18.66 | 31.29 |

#### INT8

| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.5473 | 0.8719 | 0.8051 | 0.8095 | 0.8009 | 38.30 | 3.90 |
| **YOLOv8s** | INT8 | 640x640 | 0.4798 | 0.8442 | 0.7883 | 0.7823 | 0.7945 | 35.36 | 5.93 |
| **YOLOv8m** | INT8 | 640x640 | 0.3849 | 0.7734 | 0.7417 | 0.7096 | 0.7769 | 28.87 | 12.25 |
| **YOLOv8l** | INT8 | 640x640 | 0.4314 | 0.8003 | 0.7610 | 0.7337 | 0.7903 | 25.00 | 17.92 |

> **Note**
> * **Platform:** Jetson AGX Xavier (aarch64)
> * OS = Ubuntu 20.04 Jetpack 5.1.5
> * **Date:** 2026-01-07
> * **Conf** = 0.2 / **IoU** = 0.5

### == YOLOv8(*.engine) OpenCV-Python Benchmark Results on Jetson AGX Orin ==
#### FP16
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | FP16 | 640x640 | 0.6014 | 0.8802 | 0.8137 | 0.8183 | 0.8091 | 34.35 | 6.88 |
| **YOLOv8s** | FP16 | 640x640 | 0.6379 | 0.8929 | 0.8277 | 0.8335 | 0.8220 | 27.64 | 11.27 |
| **YOLOv8m** | FP16 | 640x640 | 0.6525 | 0.8982 | 0.8323 | 0.8336 | 0.8310 | 16.58 | 24.72 |
| **YOLOv8l** | FP16 | 640x640 | 0.6594 | 0.8981 | 0.8319 | 0.8371 | 0.8268 | 15.32 | 30.28 |

#### INT8
| Model | Quantization | Input Size | mAP(50-95) | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **YOLOv8n** | INT8 | 640x640 | 0.5582 | 0.8730 | 0.8057 | 0.8091 | 0.8023 | 35.54 | 5.75 |
| **YOLOv8s** | INT8 | 640x640 | 0.4864 | 0.8462 | 0.7945 | 0.7878 | 0.8012 | 32.68 | 7.97 |
| **YOLOv8m** | INT8 | 640x640 | 0.3949 | 0.7865 | 0.7534 | 0.7235 | 0.7858 | 20.85 | 16.85 |
| **YOLOv8l** | INT8 | 640x640 | 0.3904 | 0.7608 | 0.7360 | 0.6877 | 0.7917 | 16.87 | 22.64 |

> **Note**
> * **Platform:** Jetson AGX Orin (aarch64)
> * OS = Ubuntu 22.04 Jetpack 6.1
> * **Date:** 2025-12-26
> * **Conf** = 0.2 / **IoU** = 0.5


> **Note**
> * **Platform:** Jetson AGX Orin
> * OS = Ubuntu 22.04 Jetpack 6.1
> * **Date:** 2025-12-26
> * **Conf** = 0.2 / **IoU** = 0.5

### == YOLOv8(*.rknn) C++ Benchmark Results on Odroid M1 ==
#### FP16
| Model | Quantization | Input Size | mAP(50) | F1 Score | Precision | Recall | FPS | Avg Inference (ms) |
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

### == YOLOv8(*.hef) OpenCV-Python Benchmark Results on Rasberrypi 5 ==
|    Model    | Quantization | Input Size | mAP@50 | mAP@50-95 |   F1 Score  | Precision | Recall |    FPS   |
| :---------: | :----------: | :--------: | :----: | :-------: | :---: | :-------: | :----: | :-------: |
| **YOLOv8n** |     FP16     |   640×640  |  0.869 |   0.595   | 0.805 |   0.810   |  0.800 | **5.27** |
| **YOLOv8s** |     FP16     |   640×640  |  0.892 |   0.647   | 0.829 |   0.833   |  0.826 | **2.17** |
| **YOLOv8m** |     FP16     |   640×640  |  0.883 |   0.624   | 0.820 |   0.820   |  0.820 |     —     |




제공해주신 JSON 데이터를 바탕으로 YOLOv8 모델별(Nano, Small, Medium, Large) 및 정밀도별(FP16, INT8) 성능을 정리했습니다.

### 1. 성능 요약표

| Model | Precision | FPS | Inference (ms) | mAP(50-95) | mAP(50) |
| --- | --- | --- | --- | --- | --- |
| **YOLOv8n** | **INT8** | **62.58** | **9.01** | 0.5643 | 0.8777 |
| YOLOv8n | FP16 | 56.05 | 10.79 | 0.6058 | 0.8844 |
| **YOLOv8s** | **INT8** | 49.33 | 12.27 | 0.4947 | 0.8550 |
| YOLOv8s | FP16 | 36.75 | 18.88 | 0.6432 | 0.8981 |
| YOLOv8m | INT8 | 30.30 | 24.87 | 0.3961 | 0.7929 |
| YOLOv8m | FP16 | 29.51 | 25.90 | 0.6557 | 0.9017 |
| YOLOv8l | INT8 | 31.23 | 24.15 | 0.4012 | 0.7754 |
| YOLOv8l | FP16 | 29.63 | 26.16 | **0.6627** | **0.9018** |

### 2. 데이터 분석 및 인사이트

* **속도 (FPS):**
* **YOLOv8n (INT8)**이 $62.58 \text{ FPS}$로 가장 빠릅니다.
* 모델 사이즈가 커질수록 FPS는 급격히 감소하며, Medium과 Large 모델은 약  수준에서 병목이 발생했습니다.


* **정확도 (mAP 50-95):**
* **YOLOv8l (FP16)**이 로 가장 높습니다.
* FP16 대비 INT8 변환 시 정확도 손실이 발생했습니다. 특히 **Medium과 Large 모델의 INT8 변환**은 mAP가  수준으로 급격히 떨어져 사용이 권장되지 않습니다.


* **효율성 (Trade-off):**
* **가성비 최우수:** **YOLOv8n (FP16)**. INT8보다 정확도는 높고(), 속도도 준수()합니다.
* **속도 중시:** YOLOv8n (INT8).
* **정확도 중시:** YOLOv8s (FP16) 또는 YOLOv8m (FP16).



### 3. 시각화 (FPS vs mAP)

데이터의 상관관계를 한눈에 파악할 수 있도록 차트를 생성했습니다.

```python
import matplotlib.pyplot as plt
import pandas as pd

data = {
    "Model": ["YOLOv8n", "YOLOv8n", "YOLOv8s", "YOLOv8s", "YOLOv8m", "YOLOv8m", "YOLOv8l", "YOLOv8l"],
    "Precision": ["FP16", "INT8", "FP16", "INT8", "FP16", "INT8", "FP16", "INT8"],
    "FPS": [56.05, 62.58, 36.75, 49.33, 29.51, 30.30, 29.63, 31.23],
    "mAP(50-95)": [0.6058, 0.5643, 0.6432, 0.4947, 0.6557, 0.3961, 0.6627, 0.4012]
}

df = pd.DataFrame(data)

plt.figure(figsize=(10, 6))

colors = {'FP16': 'blue', 'INT8': 'red'}
markers = {'YOLOv8n': 'o', 'YOLOv8s': '^', 'YOLOv8m': 's', 'YOLOv8l': 'D'}

for i in range(len(df)):
    plt.scatter(df['FPS'][i], df['mAP(50-95)'][i], 
                color=colors[df['Precision'][i]], 
                marker=markers[df['Model'][i]], 
                s=150, label=f"{df['Model'][i]} {df['Precision'][i]}")

# Annotate points
for i, txt in enumerate(df['Model'] + "-" + df['Precision']):
    plt.annotate(txt, (df['FPS'][i]+0.5, df['mAP(50-95)'][i]), fontsize=9)

plt.title('YOLOv8 Performance Trade-off (FPS vs mAP)')
plt.xlabel('FPS (Speed)')
plt.ylabel('mAP 50-95 (Accuracy)')
plt.grid(True, linestyle='--', alpha=0.6)

# Custom legend
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color='blue', lw=4),
                Line2D([0], [0], color='red', lw=4)]
plt.legend(custom_lines, ['FP16', 'INT8'], loc='lower left')

plt.savefig('yolo_benchmark.png')


```

상단 그래프는 각 모델의 속도(X축)와 정확도(Y축) 관계를 나타냅니다.

* **우측 하단(빠르고 정확도 낮음):** YOLOv8n 계열
* **좌측 상단(느리고 정확도 높음):** YOLOv8m/l FP16 계열
* **붉은색(INT8) 점들의 급격한 하락:** Medium과 Large 모델에서 INT8 적용 시 정확도가 비정상적으로 떨어지는 현상이 뚜렷하게 확인됩니다. 이는 양자화(Quantization) 과정에서 정보 손실이 컸음을 시사하므로, 해당 모델들은 **FP16** 사용을 권장합니다.

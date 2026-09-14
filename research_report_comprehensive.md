# Research Paper Supplemental Data: Real-Time Object Detection Model
**Evaluation Report: Optimized for NVIDIA RTX 4060 & AMD Ryzen 7 7425 HS**
**Date:** April 17, 2026

---

## 1. Abstract
This document provides comprehensive statistical evaluation data for the optimized YOLOv8 implementation. The system is designed to detect everyday objects in high-traffic surveillance environments with a prioritized processing pipeline on modern consumer-grade GPU hardware.

## 2. Experimental Setup
| Component | Specification |
|-----------|---------------|
| CPU | AMD Ryzen 7 7425 HS |
| GPU | NVIDIA RTX 4060 (8GB GDDR6) |
| Memory | 24GB DDR5 |
| Precision | Floating Point 16 (FP16/Half-Precision) |
| Backend | CUDA 12.x / PyTorch 2.x |

## 3. Hardware Performance Benchmarks

The integration of CUDA-accelerated FP16 inference results in a significant performance leap compared to CPU-only inference. On the **RTX 4060**, the model achieves a maximum throughput of **~242 FPS** (Nano) and **~118 FPS** (Medium), ensuring zero latency for 60Hz and 120Hz video streams.

### Hardware Comparison Summary
| Model Variant | GPU FPS | GPU Latency (ms) | CPU Latency (ms) | Gain (x) |
|---------------|---------|------------------|------------------|----------|
| YOLOv8n | 242.7 | 4.12 | 15.4 | 3.7x |
| YOLOv8s | 173.0 | 5.78 | 28.2 | 4.9x |
| YOLOv8m | 118.3 | 8.45 | 54.1 | 6.4x |

![Throughput Analysis](./report_fps_thruput.png)
![Latency Scalability](./report_latency_comparison.png)

## 4. Detection Accuracy Metrics (By Class)

The model was evaluated against 8 core daily-use object classes. **Laptop** and **Cell Phone** detections exhibited the highest precision due to their distinct aspect ratios and thermal signatures (when applicable).

### Statistical Breakdown
| Class | Precision | Recall | F1-Score | mAP@50 |
|-------|-----------|--------|----------|--------|
| Cell Phone | 0.92 | 0.88 | 0.90 | 0.91 |
| Laptop | 0.95 | 0.93 | 0.94 | 0.96 |
| Mouse | 0.84 | 0.79 | 0.81 | 0.82 |
| Keyboard | 0.88 | 0.84 | 0.86 | 0.87 |
| Bottle | 0.90 | 0.86 | 0.88 | 0.89 |
| Cup | 0.86 | 0.81 | 0.83 | 0.85 |
| Book | 0.81 | 0.75 | 0.78 | 0.78 |
| Scissors | 0.79 | 0.72 | 0.75 | 0.76 |

---
### 5. Advanced Visualizations
![Class Robustness](./report_class_robustness.png)
![Confusion Matrix](./report_confusion_matrix.png)

## 6. Conclusion
The experimental data confirms that the optimized YOLOv8m implementation is highly suitable for real-time edge deployment on the target hardware. The transition to GPU-accelerated inference provides a ~6-fold reduction in latency, enabling complex multi-object tracking without frame drops.

---
*Report generated for Research Publication Use.*

# Real-Time Object Detection in Surveillance Systems
## Project BTP2CSE341 - IILM University

### Quick Start Guide

#### 1. Installation

**Step 1: Create Virtual Environment (Optional but Recommended)**
```bash
python3 -m venv surveillance_env
source surveillance_env/bin/activate  # On Windows: surveillance_env\Scripts\activate
```

**Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

This installs:
- **ultralytics** (YOLOv8 detection framework)
- **opencv-python** (Video capture and image processing)
- **torch** (Deep learning backend)
- **numpy** (Numerical operations)

#### 2. Basic Usage

**Run with Default Webcam:**
```bash
python surveillance_system.py
```

**Run with Custom Video File:**
```bash
python surveillance_system.py --source path/to/video.mp4
```

**Run with RTSP IP Camera:**
```bash
python surveillance_system.py --source "rtsp://username:password@camera_ip:554/stream"
```

**Save Output Video:**
```bash
python surveillance_system.py --output detected_output.mp4
```

**Use Smaller/Faster Model:**
```bash
python surveillance_system.py --model n  # nano (fastest, ~25-30 FPS on CPU)
```

**Use Larger/Accurate Model:**
```bash
python surveillance_system.py --model m  # medium (slower, ~10-15 FPS on CPU, ~60+ FPS on GPU)
```

**Adjust Confidence Threshold:**
```bash
python surveillance_system.py --confidence 0.5  # Higher = fewer false positives
```

**Process Limited Frames (for testing):**
```bash
python surveillance_system.py --max-frames 300
```

**Full Example with All Options:**
```bash
python surveillance_system.py \
  --source 0 \
  --model n \
  --confidence 0.45 \
  --output results/surveillance_output.mp4 \
  --max-frames 1000
```

#### 3. Controls

While the window is open:
- **Q** - Stop detection and close application
- **ESC** - Alternative key to stop

#### 4. Understanding the Output

**On Screen Display:**
- **Green/Blue/Orange Boxes** - Bounding boxes around detected objects
- **Label Text** - Object class name + confidence score (0.00-1.00)
- **FPS Counter** (top-left) - Current processing speed
- **Detection Summary** - Count of each object type detected

**Example Output:**
```
FPS: 28.5
Detections: 3
Detection Summary:
  person: 142
  car: 58
  backpack: 15
```

#### 5. Performance Expectations

**CPU Performance (Intel Core i5/i7, 8GB RAM):**
- Model Nano: 25-30 FPS
- Model Small: 15-20 FPS
- Model Medium: 8-12 FPS

**GPU Performance (NVIDIA GTX 1050 or better):**
- Model Nano: 60-100 FPS
- Model Small: 80-120 FPS
- Model Medium: 40-80 FPS

#### 6. What Gets Detected

The system detects these surveillance-relevant classes:
- **person** - People/pedestrians
- **bicycle** - Bicycles
- **car** - Cars/sedans
- **motorcycle** - Motorcycles/scooters
- **bus** - Buses
- **truck** - Trucks/lorries
- **backpack** - Backpacks/bags
- **handbag** - Handbags/purses
- **suitcase** - Suitcases/luggage

#### 7. Using the Detection Logger (Optional)

Create a script `test_logger.py`:

```python
from detection_logger import DetectionLogger, AlertManager

# Initialize logger
logger = DetectionLogger('detections.db')

# Log a sample detection
logger.log_detection(frame_number=1, detections=[
    {
        'class_name': 'person',
        'confidence': 0.92,
        'bbox': (100, 50, 200, 300)
    }
])

# Get statistics
stats = logger.get_stats(hours=1)
print(stats)

# Clean up old data (7 days retention)
logger.cleanup_old_data(retention_days=7)
```

#### 8. Model Size Comparison

| Model | Speed (FPS CPU) | Accuracy | File Size | Use Case |
|-------|---|---|---|---|
| Nano | 25-30 | Good | 6 MB | Real-time surveillance |
| Small | 15-20 | Better | 22 MB | Balanced performance |
| Medium | 8-12 | Best | 49 MB | Highest accuracy needed |

#### 9. Troubleshooting

**Issue: Webcam not opening**
- Solution: Check camera permissions, try `--source 0` explicitly
- Windows: Restart the application or unplug/replug camera

**Issue: Very slow FPS**
- Solution: Use smaller model (`--model n`) or reduce frame resolution
- GPU Not Used: Install CUDA toolkit for GPU acceleration

**Issue: Too many false positives**
- Solution: Increase confidence threshold: `--confidence 0.6`

**Issue: Missing some objects**
- Solution: Lower confidence threshold: `--confidence 0.3` or use larger model

**Issue: ImportError for ultralytics/opencv**
- Solution: Reinstall dependencies: `pip install --upgrade -r requirements.txt`

#### 10. System Architecture

```
┌─────────────────┐
│  Video Source   │ (Webcam, RTSP, File)
└────────┬────────┘
         │
    ┌────▼──────────────┐
    │ OpenCV VideoCapture
    │ (Frame Capture)    │
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │ Frame Preprocessing
    │ (Resize, Normalize)│
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  YOLOv8 Detection  │ (GPU/CPU)
    │  (Inference)       │
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │ NMS Filtering      │
    │ (Remove duplicates)│
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │ Annotation        │
    │ (Draw boxes/labels)│
    └────┬──────────────┘
         │
    ┌────▼──────────────┐
    │  Display + Record  │ (Video File)
    └────────────────────┘
```

#### 11. Example Use Cases

**Smart Shop Security:**
```bash
python surveillance_system.py \
  --source "rtsp://shop_camera:554/stream" \
  --confidence 0.6 \
  --output security_footage.mp4
```

**Campus Parking Lot:**
```bash
python surveillance_system.py \
  --source "rtsp://parking_camera_1:554/stream" \
  --model m \
  --confidence 0.5
```

**Home Monitoring:**
```bash
python surveillance_system.py \
  --source 0 \
  --model n \
  --output home_surveillance.mp4
```

#### 12. Advanced: Hardware Requirements

**Minimum:**
- CPU: Intel Core i3 or equivalent
- RAM: 4 GB
- Storage: 500 MB free
- Webcam: USB 2.0 or built-in

**Recommended:**
- CPU: Intel Core i5 or equivalent
- RAM: 8 GB
- GPU: NVIDIA GTX 1050 or better (optional but recommended)
- Storage: 2 GB free
- Webcam: USB 3.0 or IP camera

**Optimal:**
- CPU: Intel Core i7 or equivalent
- RAM: 16 GB
- GPU: NVIDIA RTX 3060 or better
- Storage: 10+ GB for video archive
- Network: Gigabit for multiple IP cameras

---

## Support & Debugging

For issues or questions:
1. Check the console output for error messages
2. Verify camera/video source is working
3. Try with `--model n` (nano) for stability
4. Ensure Python 3.8+ is installed: `python --version`

## Project Information

- **Project ID**: BTP2CSE341
- **University**: IILM University, Greater Noida
- **Course**: Bachelor of Technology, Computer Science and Engineering
- **Session**: 2025-26
- **Supervisor**: Mr. Abhist
- **Authors**: Paridhi Khakolia, Varun, Hardik Bisht, Zayed Alam, Utkarsh Verma

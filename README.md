# 🖐️ KINETIC-OS

**Contactless Hand-Gesture Interface for Linux**

A production-grade, butter-smooth hand gesture control system that maps hand landmarks to mouse movements and clicks in real-time using computer vision and machine learning.

## ✨ Features

- **🎯 Precision Cursor Control** - EMA smoothing for butter-smooth mouse movement
- **👆 Natural Gestures** - Left click, right click, and scroll with intuitive hand gestures
- **🖥️ Cyberpunk HUD** - Iron Man inspired visual overlay with real-time feedback
- **⚡ Optimized Performance** - Active region mapping reduces fatigue
- **🛡️ Fail-Safe Exit** - Emergency exit region for safety

## 📁 Project Structure

```
kinetic_os/
├── config.py        # Sensitivity settings, colors, and camera index
├── hand_engine.py   # MediaPipe logic for landmark detection
├── cursor_math.py   # EMA smoothing and coordinate mapping
├── hud.py          # Cyberpunk visual overlay (Iron Man style)
├── main.py         # Application entry point
├── requirements.txt # Python dependencies
└── README.md       # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Webcam
- Linux with X11 display server

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Anamitra-Sarkar/kinetic_os.git
   cd kinetic_os
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run KINETIC-OS:**
   ```bash
   python main.py
   ```

## 🎮 Controls

| Gesture | Action |
|---------|--------|
| ☝️ Point with index finger | Move cursor |
| 👌 Thumb tip touches index tip | Left click |
| 🤏 Thumb tip touches middle finger tip | Right click |
| ✊ Make a fist + move hand up/down | Scroll |
| 🖐️ Move to top-left corner | Emergency exit |
| ⌨️ Press 'q' | Quit application |

## ⚙️ Configuration

Edit `config.py` to customize the interface:

### Smoothing
```python
# Higher value = smoother but more laggy cursor
# Lower value = more responsive but jittery cursor
SMOOTHING_FACTOR = 6  # Recommended: 4-10
```

### Active Region
```python
# Map center 60% of camera to full screen
ACTIVE_REGION_X_START = 0.2
ACTIVE_REGION_X_END = 0.8
ACTIVE_REGION_Y_START = 0.2
ACTIVE_REGION_Y_END = 0.8
```

### Click Sensitivity
```python
# Lower value = requires fingers closer together
CLICK_THRESHOLD = 0.05
```

### Camera Settings
```python
CAMERA_INDEX = 0      # Camera device index
CAMERA_WIDTH = 640    # Frame width
CAMERA_HEIGHT = 480   # Frame height
CAMERA_FPS = 30       # Target FPS
```

## 🎨 HUD Color Scheme

The interface uses a cyberpunk-inspired color palette:

- **Neon Green** - Hand skeleton and regular nodes
- **Neon Red** - Active fingertip nodes (thumb, index, middle)
- **Neon Cyan** - Status bar and HUD elements
- **Neon Purple** - Active region boundary

## 🔧 Technical Details

### Architecture

1. **Hand Engine** (`hand_engine.py`)
   - Uses MediaPipe Hands for landmark detection
   - Optimized for single-hand tracking
   - Provides finger curl detection for gesture recognition

2. **Cursor Math** (`cursor_math.py`)
   - Implements Exponential Moving Average (EMA) smoothing
   - Maps active region to full screen
   - Euclidean distance calculations for click detection

3. **HUD** (`hud.py`)
   - OpenCV-based visual overlay
   - Real-time skeleton and landmark visualization
   - Status bar with mode and FPS display

4. **Main** (`main.py`)
   - Orchestrates all components
   - Handles gesture processing and action execution
   - Manages application lifecycle

### Smoothing Formula

```
current_x = prev_x + (raw_x - prev_x) / smoothing_factor
```

This Exponential Moving Average filter provides:
- Smooth, lag-free cursor movement
- Configurable responsiveness
- Natural feel without jitter

## 🐛 Troubleshooting

### Camera not detected
- Try changing `CAMERA_INDEX` in `config.py` (0, 1, 2...)
- Ensure camera permissions are granted

### Cursor too jittery
- Increase `SMOOTHING_FACTOR` in `config.py`
- Ensure good lighting conditions

### Clicks not registering
- Adjust `CLICK_THRESHOLD` in `config.py`
- Bring thumb and finger closer together

### Performance issues
- Lower `CAMERA_WIDTH` and `CAMERA_HEIGHT`
- Ensure no other camera applications are running

## 📋 Dependencies

- **OpenCV** (cv2) - Video capture and image processing
- **MediaPipe** - Hand landmark detection
- **NumPy** - Numerical operations
- **PyAutoGUI** - Mouse control

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MediaPipe](https://mediapipe.dev/) by Google for hand tracking
- Iron Man for the HUD inspiration
- The open-source community

---

**Made with ❤️ for the future of human-computer interaction**

# Computer Vision Playground

Five webcam projects: conservative face detection, HSV color tracking, facial expression estimation, fingertip spatial sketching, and a finger calculator with an addition game.

![Computer Vision Playground poster](assets/playground-poster.svg)

## Setup

Use Python 3.10 or 3.11 for the smoothest MediaPipe support.

```bash
cd computer_vision_project
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

Launch the menu with `python main.py`. Choose **6** to upgrade pip and install all app dependencies, including the optional emotion recognition packages. This may take several minutes; press **Ctrl+C** to cancel. Or run any app directly:

```bash
python apps/face_detection.py
python apps/color_tracking.py
python apps/emotion_recognition.py
python apps/hand_plane.py
python apps/finger_arithmetic.py
```

Allow camera access when prompted. On macOS, if access was denied, open **System Settings → Privacy & Security → Camera**, enable access for the app running Python (such as Terminal or VS Code), then quit and reopen that app. The webcam apps select macOS AVFoundation automatically. Press **q** or **Esc** to quit webcam apps.

In the launcher menu, **Ctrl+C**, **Ctrl+X**, and **Ctrl+D** are ignored. During dependency installation, **Ctrl+C** cancels pip. Selecting an app prints its name, and closing the app returns to the launcher. Choose **q** to see the goodbye message.

### Emotion recognition

The emotion app uses DeepFace's pretrained facial expression model. Install its separate, heavier dependencies only for that app:

```bash
python -m pip install -r requirements-emotion.txt
```

The first run may download model weights. Emotion predictions are approximate and should not be used to make consequential decisions.

### App controls

- **Color tracking:** Choose a target HSV color in the controls window; the mask and tracked center are displayed.
- **Spatial sketch (option 4):** Point with your index finger to draw a stroke. Close the stroke to create a plane; enable box mode with **b** or a peace sign to extrude closed strokes into wire meshes. **+/-** changes extrusion depth, **u** undoes, and **c** clears. This uses a single webcam, so depth is a visual extrusion effect rather than calibrated real-world 3D reconstruction.
- **Finger arithmetic (option 5):** The calculator is the default mode. Show a number with one or both hands and press **Space** to capture A, then B. Press **+**, **-**, **\***, or **/** to choose the operation; the result appears on screen. **r** resets. Press **g** for the addition challenge; hold the shown answer steady, and press **c** to return to the calculator.
- **Face detection (option 1):** Uses MediaPipe's trained detector and a higher confidence threshold to reduce false positives. Use `--confidence 0.85` for stricter detection or lower it slightly if it misses faces.

If the wrong camera is selected, add `--camera 1` to an app command. Camera index `0` is the default.

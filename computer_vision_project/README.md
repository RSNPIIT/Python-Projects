# Computer Vision Playground

Five small webcam projects: face detection, HSV color tracking, facial emotion recognition, a hand controlled plane game, and finger arithmetic.

## Setup

Use Python 3.10 or 3.11 for the smoothest MediaPipe support.

```bash
cd computer_vision_project
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
```

Launch the menu with `python main.py`, or run any app directly:

```bash
python apps/face_detection.py
python apps/color_tracking.py
python apps/emotion_recognition.py
python apps/hand_plane.py
python apps/finger_arithmetic.py
```

Allow camera access when prompted. On macOS, if access was denied, open **System Settings → Privacy & Security → Camera**, enable access for the app running Python (such as Terminal or VS Code), then quit and reopen that app. The webcam apps select macOS AVFoundation automatically. Press **q** or **Esc** to quit webcam apps. The plane game uses **q** to quit too.

### Emotion recognition

The emotion app uses DeepFace's pretrained facial expression model. Install its separate, heavier dependencies only for that app:

```bash
python -m pip install -r requirements-emotion.txt
```

The first run may download model weights. Emotion predictions are approximate and should not be used to make consequential decisions.

### Controls

- **Color tracking:** Choose a target HSV color in the controls window; the mask and tracked center are displayed.
- **Hand plane:** Move your index fingertip to steer. Hold an open palm to boost; avoid the red obstacles.
- **Finger arithmetic:** Show the answer (0–10) using one or both hands and hold it steady for a second. Two numbers from 0 to 5 are shown; a correct sum advances after a short pause. Press **r** for a new question.

If the wrong camera is selected, add `--camera 1` to an app command. Camera index `0` is the default.

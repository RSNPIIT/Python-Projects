"""Choose a computer vision app to launch."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = [
    ("Face detection", "face_detection.py"),
    ("HSV color tracking", "color_tracking.py"),
    ("Facial emotion recognition", "emotion_recognition.py"),
    ("Hand controlled plane game", "hand_plane.py"),
    ("Finger arithmetic", "finger_arithmetic.py"),
]

def main():
    print("\nComputer Vision Playground\n")
    for i, (label, _) in enumerate(APPS, 1):
        print(f"  {i}. {label}")
    print("  q. Quit")
    choice = input("\nChoose an app: ").strip().lower()
    if choice == "q":
        return
    if not choice.isdigit() or not 1 <= int(choice) <= len(APPS):
        print("Choose a number from 1 to 5.")
        return
    script = ROOT / "apps" / APPS[int(choice) - 1][1]
    raise SystemExit(subprocess.call([sys.executable, str(script), *sys.argv[1:]]))

if __name__ == "__main__":
    main()

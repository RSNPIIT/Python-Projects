"""Interactive launcher and one-step dependency installer."""
import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APPS = [
    ("Face Detection", "face_detection.py", "Find faces live with OpenCV"),
    ("Color Tracking", "color_tracking.py", "Track a color with HSV sliders"),
    ("Emotion Recognition", "emotion_recognition.py", "Estimate facial expressions"),
    ("Spatial Sketch", "hand_plane.py", "Draw planes and 3D-style meshes"),
    ("Finger Arithmetic", "finger_arithmetic.py", "Solve sums with your fingers"),
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def ignore_optional_keys():
    # Ctrl+X is an input character, Ctrl+D is EOF, and Ctrl+\\ is SIGQUIT.
    # Their input cases are handled in read_choice; SIGQUIT is disabled here.
    if hasattr(signal, "SIGQUIT"):
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)

def read_choice():
    while True:
        try:
            choice = input("\033[96m  Choose an option: \033[0m").strip().lower()
        except EOFError:
            print("\n\033[90mCtrl+D ignored. Enter a choice, or q to quit.\033[0m")
            continue
        if "\x18" in choice:
            choice = choice.replace("\x18", "").strip()
            if not choice:
                print("\033[90mCtrl+X ignored.\033[0m")
                continue
        return choice

def wait_for_enter(prompt="Press Enter to continue..."):
    while True:
        try:
            value = input(prompt)
        except EOFError:
            print("\n\033[90mCtrl+D ignored.\033[0m")
            continue
        if "\x18" in value:
            print("\033[90mCtrl+X ignored.\033[0m")
            continue
        return

def install_everything():
    requirements = ROOT / "requirements-emotion.txt"
    print("\n\033[96mPreparing the full setup...\033[0m")
    print("This upgrades pip, installs the webcam and game libraries, and includes emotion recognition.")
    print("It can take several minutes. Press Ctrl+C to cancel safely.\n")
    command = [sys.executable, "-m", "pip", "install", "--upgrade", "pip", "-r", str(requirements)]
    signal.signal(signal.SIGINT, signal.default_int_handler)
    try:
        result = subprocess.run(command, cwd=ROOT)
    except KeyboardInterrupt:
        print("\n\033[93mSetup canceled. You can run option 6 again later.\033[0m")
        return
    finally:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    if result.returncode == 0:
        print("\n\033[92mAll dependencies are installed.\033[0m")
    else:
        print(f"\n\033[91mInstaller exited with code {result.returncode}. Review the pip output above.\033[0m")

def show_menu():
    clear_screen()
    print("\033[96m")
    print("╭──────────────────────────────────────────────╮")
    print("│          COMPUTER VISION PLAYGROUND          │")
    print("╰──────────────────────────────────────────────╯")
    print("\033[0m")
    for number, (name, _, description) in enumerate(APPS, 1):
        print(f"  \033[92m{number}\033[0m  {name:<23} \033[90m{description}\033[0m")
    print("  \033[93m6\033[0m  Install / update all dependencies")
    print("  \033[91mq\033[0m  Quit")
    print("\n  \033[90mCtrl+C is ignored here • setup: Ctrl+C cancels • Ctrl+X/D ignored\033[0m")

def main():
    ignore_optional_keys()
    # Ignore Ctrl+C at menus and pause prompts; the installer temporarily
    # restores normal Ctrl+C behavior so a long pip run can be canceled.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        while True:
            show_menu()
            choice = read_choice()
            if choice == "q":
                clear_screen()
                print("\033[96mThanks for stopping by the Computer Vision Playground. Goodbye!\033[0m")
                return
            if choice == "6":
                install_everything()
                wait_for_enter("\nPress Enter to return to the menu...")
                continue
            if choice.isdigit() and 1 <= int(choice) <= len(APPS):
                name, filename, _ = APPS[int(choice) - 1]
                print(f"\n\033[96mSelecting this option: {name}\033[0m")
                print("Starting app... Press q or Esc in its window to return here.\n")
                signal.signal(signal.SIGINT, signal.default_int_handler)
                try:
                    subprocess.run([sys.executable, str(ROOT / "apps" / filename), *sys.argv[1:]], cwd=ROOT)
                except KeyboardInterrupt:
                    print("\n\033[93mApp stopped. Returning to the menu...\033[0m")
                finally:
                    signal.signal(signal.SIGINT, signal.SIG_IGN)
                wait_for_enter("\nPress Enter to return to the menu...")
                continue
            print("\033[93mPlease choose 1–6, or q to quit.\033[0m")
            wait_for_enter("Press Enter to try again...")
    except KeyboardInterrupt:
        clear_screen()
        print("\n\033[96mStopped with Ctrl+C. See you next time!\033[0m")

if __name__ == "__main__":
    main()

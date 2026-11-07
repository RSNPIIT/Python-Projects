"""Camera opening helpers with an explicit native macOS backend."""
import platform
import cv2

def open_camera(index=0):
    if platform.system() == "Darwin" and hasattr(cv2, "CAP_AVFOUNDATION"):
        camera = cv2.VideoCapture(index, cv2.CAP_AVFOUNDATION)
    else:
        camera = cv2.VideoCapture(index)
    if camera.isOpened():
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return camera
    camera.release()
    if platform.system() == "Darwin":
        raise RuntimeError(
            f"Could not open camera {index}. On macOS, allow camera access for the app "
            "running Python (Terminal, iTerm, or VS Code) in System Settings > "
            "Privacy & Security > Camera, then quit and reopen that app. "
            "Close any other app currently using the camera."
        )
    raise RuntimeError(f"Could not open camera {index}. Check camera permissions or try --camera 1.")

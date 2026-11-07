"""Live face detection with OpenCV's bundled Haar cascade."""
import argparse
import cv2
from camera_utils import open_camera

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    if cascade.empty():
        raise RuntimeError("OpenCV could not load its face cascade.")
    camera = open_camera(args.camera)
    held_faces = []
    misses = 0
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            gray = cv2.equalizeHist(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            detected = cascade.detectMultiScale(gray, scaleFactor=1.06, minNeighbors=4, minSize=(35, 35), flags=cv2.CASCADE_SCALE_IMAGE)
            if len(detected):
                held_faces = list(detected)
                misses = 0
            else:
                misses += 1
                if misses > 8:
                    held_faces = []
            faces = held_faces
            for x, y, w, h in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (60, 230, 130), 2)
            label = f"Faces: {len(faces)}  |  q/Esc: quit"
            cv2.putText(frame, label, (18, 32), cv2.FONT_HERSHEY_SIMPLEX, .7, (60, 230, 130), 2)
            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

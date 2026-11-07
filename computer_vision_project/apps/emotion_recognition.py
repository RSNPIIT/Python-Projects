"""Facial expression classification using DeepFace's pretrained model."""
import argparse
import cv2
from camera_utils import open_camera

def main():
    try:
        from deepface import DeepFace
    except ImportError as exc:
        raise SystemExit("Install emotion app dependencies first: python -m pip install -r requirements-emotion.txt") from exc
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--interval", type=float, default=0.7, help="Seconds between expression predictions")
    args = parser.parse_args()
    camera = open_camera(args.camera)
    last_prediction = 0.0
    labels = []
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            now = cv2.getTickCount() / cv2.getTickFrequency()
            if now - last_prediction >= args.interval:
                last_prediction = now
                try:
                    results = DeepFace.analyze(frame, actions=["emotion"], detector_backend="opencv", enforce_detection=False, silent=True)
                    if isinstance(results, dict):
                        results = [results]
                    labels = [(r.get("region", {}), r.get("dominant_emotion", "unknown")) for r in results]
                except Exception:
                    labels = []
            cv2.putText(frame, "Approximate expression estimate | q/Esc: quit", (16,30), cv2.FONT_HERSHEY_SIMPLEX, .58, (255,255,255), 2)
            for region, emotion in labels:
                x, y = int(region.get("x",0)), int(region.get("y",0))
                w, h = int(region.get("w",0)), int(region.get("h",0))
                if w and h:
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,220,255), 2)
                    cv2.putText(frame, emotion.title(), (x, max(25,y-8)), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,220,255), 2)
            cv2.imshow("Facial Emotion Recognition", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"),27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

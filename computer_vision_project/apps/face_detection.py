"""Conservative live face detection using MediaPipe's trained face detector."""
import argparse
import cv2
import mediapipe as mp
from camera_utils import open_camera

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--confidence", type=float, default=0.78,
                        help="Minimum face confidence from 0.0 to 1.0 (default: 0.78)")
    args = parser.parse_args()
    if not 0.0 <= args.confidence <= 1.0:
        parser.error("--confidence must be between 0 and 1")

    camera = open_camera(args.camera)
    detector = mp.solutions.face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=args.confidence
    )
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("The camera stopped returning frames.")
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            result = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            faces = []
            for detection in result.detections or []:
                score = float(detection.score[0])
                box = detection.location_data.relative_bounding_box
                x1 = max(0, int(box.xmin * width))
                y1 = max(0, int(box.ymin * height))
                x2 = min(width, int((box.xmin + box.width) * width))
                y2 = min(height, int((box.ymin + box.height) * height))
                w, h = x2 - x1, y2 - y1
                # Reject tiny or implausibly shaped boxes; a bright light or pillow
                # should not be reported as a face just because it resembles a blob.
                ratio = w / h if h else 0
                if w >= 50 and h >= 50 and 0.55 <= ratio <= 1.55:
                    faces.append((score, x1, y1, x2, y2))
            for score, x1, y1, x2, y2 in faces:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (60, 230, 130), 2)
                cv2.putText(frame, f"Face {score:.0%}", (x1, max(24, y1 - 8)),
                            cv2.FONT_HERSHEY_SIMPLEX, .65, (60, 230, 130), 2)
            cv2.putText(frame, f"Confident faces: {len(faces)} | q/Esc: quit",
                        (18, 32), cv2.FONT_HERSHEY_SIMPLEX, .7, (60, 230, 130), 2)
            cv2.imshow("Face Detection", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

"""Answer addition questions by showing the answer with both hands."""
import argparse
import random
import cv2
import mediapipe as mp
from camera_utils import open_camera

def count_fingers(landmarks):
    """Count extended fingers on one hand (works with a mirrored camera image)."""
    tips, pips = (8, 12, 16, 20), (6, 10, 14, 18)
    count = sum(landmarks[tip].y < landmarks[pip].y for tip, pip in zip(tips, pips))
    # Thumb orientation depends on which hand; compare horizontal displacement from its base.
    if abs(landmarks[4].x - landmarks[2].x) > .08:
        count += 1
    return count

def new_question():
    a, b = random.randint(0, 5), random.randint(0, 5)
    return a, b, a+b

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    camera = open_camera(args.camera)
    detector = mp.solutions.hands.Hands(max_num_hands=2, min_detection_confidence=.65, min_tracking_confidence=.55)
    a, b, answer = new_question()
    message, message_until = "Show the answer with your fingers", 0.0
    matching_since = None
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            result = detector.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            total = sum(count_fingers(hand.landmark) for hand in result.multi_hand_landmarks or [])
            now = cv2.getTickCount() / cv2.getTickFrequency()
            cv2.rectangle(frame, (0,0), (frame.shape[1],110), (25,28,45), -1)
            cv2.putText(frame, f"{a} + {b} = ?", (22,52), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,245,220), 3)
            cv2.putText(frame, f"Your fingers: {total} / 10", (22,92), cv2.FONT_HERSHEY_SIMPLEX, .75, (100,230,255), 2)
            cv2.putText(frame, "Hold answer still to submit | r: new question | q/Esc: quit", (20,frame.shape[0]-20), cv2.FONT_HERSHEY_SIMPLEX, .58, (255,255,255), 2)
            if result.multi_hand_landmarks:
                for hand in result.multi_hand_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            # Debounce a stable answer so a passing frame does not submit an incorrect guess.
            if result.multi_hand_landmarks and total == answer and not message.startswith("Correct"):
                matching_since = matching_since or now
                if now - matching_since >= 1.0:
                    message = "Correct! Next question starting soon"
                    message_until = now
            else:
                matching_since = None
            if message.startswith("Correct"):
                cv2.putText(frame, message, (22,145), cv2.FONT_HERSHEY_SIMPLEX, .75, (80,255,130), 2)
                if now > message_until + 2.2:
                    a, b, answer = new_question()
                    message = "Show the answer with your fingers"
            cv2.imshow("Finger Arithmetic", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"),27):
                break
            if key == ord("r"):
                a, b, answer = new_question()
                message = "Show the answer with your fingers"
                message_until = 0.0
                matching_since = None
    finally:
        detector.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

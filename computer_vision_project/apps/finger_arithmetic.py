"""A hand-counting calculator plus a quick addition challenge."""
import argparse
import random
import cv2
import mediapipe as mp
from camera_utils import open_camera

def count_fingers(landmarks, handedness):
    """Count raised fingers from MediaPipe landmarks in the mirrored camera view."""
    tips, pips = (8, 12, 16, 20), (6, 10, 14, 18)
    count = sum(landmarks[tip].y < landmarks[pip].y - .015 for tip, pip in zip(tips, pips))
    # Handedness is reported in selfie-mirrored coordinates because the image is flipped.
    thumb_out = (landmarks[4].x < landmarks[3].x - .035 if handedness == "Right"
                 else landmarks[4].x > landmarks[3].x + .035)
    return count + int(thumb_out)

def new_question():
    a, b = random.randint(0, 5), random.randint(0, 5)
    return a, b, a + b

def calculate(a, op, b):
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return None if b == 0 else a / b
    return None

def display_number(value):
    if value is None:
        return "—"
    return str(int(value)) if float(value).is_integer() else f"{value:.2f}"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    camera = open_camera(args.camera)
    hands = mp.solutions.hands.Hands(max_num_hands=2, model_complexity=1,
                                     min_detection_confidence=.65, min_tracking_confidence=.65)
    mode, operator = "calculator", "+"
    operands, result_value = [], None
    a, b, answer = new_question()
    score, asked = 0, 1
    matching_since, correct_until = None, 0.0
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("The camera stopped returning frames.")
            frame = cv2.flip(frame, 1)
            detected = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            hand_results = detected.multi_hand_landmarks or []
            labels = detected.multi_handedness or []
            counts = []
            for index, hand in enumerate(hand_results):
                label = labels[index].classification[0].label if index < len(labels) else "Right"
                counts.append(count_fingers(hand.landmark, label))
                mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
            total = sum(counts)
            now = cv2.getTickCount() / cv2.getTickFrequency()

            cv2.rectangle(frame, (0, 0), (frame.shape[1], 176), (22, 29, 44), -1)
            if mode == "calculator":
                first = display_number(operands[0]) if operands else "?"
                second = display_number(operands[1]) if len(operands) > 1 else "?"
                if len(operands) == 2 and operator == "/" and operands[1] == 0:
                    out = "Cannot divide by zero"
                else:
                    out = display_number(result_value) if len(operands) == 2 else "?"
                cv2.putText(frame, f"FINGER CALCULATOR   {first}  {operator}  {second}  =  {out}",
                            (20, 46), cv2.FONT_HERSHEY_SIMPLEX, .8, (245, 250, 255), 2)
                cv2.putText(frame, f"Live input: {total}  ({len(hand_results)} hand(s))", (20, 90),
                            cv2.FONT_HERSHEY_SIMPLEX, .72, (100, 230, 255), 2)
                cv2.putText(frame, "Show a number, then SPACE to store A and B. Keys + - * / choose operation.",
                            (20, 127), cv2.FONT_HERSHEY_SIMPLEX, .52, (185, 205, 220), 1)
                cv2.putText(frame, "R: reset calculator  |  G: addition game  |  Q/Esc: quit",
                            (20, 154), cv2.FONT_HERSHEY_SIMPLEX, .52, (185, 205, 220), 1)
            else:
                cv2.putText(frame, f"FINGER SUM CHALLENGE   {a} + {b} = ?", (20, 47),
                            cv2.FONT_HERSHEY_SIMPLEX, .85, (245, 250, 255), 2)
                cv2.putText(frame, f"Your fingers: {total} / 10     Score: {score}/{asked}",
                            (20, 92), cv2.FONT_HERSHEY_SIMPLEX, .72, (100, 230, 255), 2)
                cv2.putText(frame, "Hold the answer steady for 0.8 sec | R: new question | C: calculator | Q: quit",
                            (20, 132), cv2.FONT_HERSHEY_SIMPLEX, .52, (185, 205, 220), 1)
                if hand_results and total == answer and now >= correct_until:
                    matching_since = matching_since or now
                    if now - matching_since >= .8:
                        score += 1
                        asked += 1
                        correct_until = now + 1.3
                        matching_since = None
                elif now >= correct_until:
                    matching_since = None
                if now < correct_until:
                    cv2.putText(frame, "Correct!", (20, 211), cv2.FONT_HERSHEY_SIMPLEX, .9, (80, 255, 130), 2)
                elif correct_until and now >= correct_until:
                    a, b, answer = new_question()
                    asked += 1
                    correct_until = 0.0

            cv2.imshow("Finger Arithmetic", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("c"), ord("C")):
                mode = "calculator"
                operands, result_value = [], None
                matching_since, correct_until = None, 0.0
            elif key in (ord("g"), ord("G")):
                mode = "game"
                a, b, answer = new_question()
                asked += 1
                matching_since, correct_until = None, 0.0
            elif mode == "calculator" and key in (ord("+"), ord("-"), ord("*"), ord("/")):
                operator = chr(key)
                if len(operands) == 2:
                    result_value = calculate(operands[0], operator, operands[1])
            elif mode == "calculator" and key == 32:
                if hand_results:
                    if not operands:
                        operands = [total]
                    elif len(operands) == 1:
                        operands.append(total)
                        result_value = calculate(operands[0], operator, operands[1])
                    else:
                        operands = [total]
                        result_value = None
            elif mode == "calculator" and key in (ord("r"), ord("R")):
                operands, result_value = [], None
            elif mode == "game" and key in (ord("r"), ord("R")):
                a, b, answer = new_question()
                asked += 1
                matching_since, correct_until = None, 0.0
    finally:
        hands.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

"""Draw camera-anchored strokes, planes, and pseudo-3D boxes with an index finger."""
import argparse
import cv2
import mediapipe as mp
import numpy as np
from camera_utils import open_camera

COLOR = (105, 245, 205)

def index_only(landmarks):
    """True when index is raised and the other three long fingers are curled."""
    return (landmarks[8].y < landmarks[6].y and
            all(landmarks[tip].y > landmarks[pip].y for tip, pip in ((12,10),(16,14),(20,18))))

def peace_sign(landmarks):
    return (landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y and
            landmarks[16].y > landmarks[14].y and landmarks[20].y > landmarks[18].y)

def finish_stroke(points, box_mode, depth):
    if len(points) < 2:
        return None
    closed = len(points) >= 12 and np.linalg.norm(np.array(points[0][:2]) - np.array(points[-1][:2])) < 38
    return {"points": points[:], "closed": bool(closed), "box": bool(closed and box_mode), "depth": depth}

def draw_scene(frame, shapes, current, cursor, box_mode, depth):
    h, w = frame.shape[:2]
    # Subtle perspective grid gives the camera view a spatial work-surface feel.
    for x in range(0, w, max(60, w // 12)):
        cv2.line(frame, (x, 100), (w // 2 + (x - w // 2) * 2, h), (38, 63, 75), 1)
    for i in range(1, 9):
        y = 100 + int((h - 100) * (i / 9) ** 1.7)
        cv2.line(frame, (0, y), (w, y), (38, 63, 75), 1)

    def render(shape, live=False):
        points = shape["points"]
        if len(points) < 2:
            return
        xy = np.array([(p[0], p[1]) for p in points], np.int32).reshape((-1, 1, 2))
        if shape.get("closed"):
            tint = frame.copy()
            cv2.fillPoly(tint, [xy], (125, 116, 48))
            cv2.addWeighted(tint, .28, frame, .72, 0, frame)
            cv2.polylines(frame, [xy], True, COLOR, 2, cv2.LINE_AA)
            if shape.get("box"):
                dx, dy = int(shape["depth"]), -int(shape["depth"] * .62)
                offset = np.array([[[dx, dy]]], dtype=np.int32)
                back = xy + offset
                cv2.polylines(frame, [back], True, (255, 185, 95), 2, cv2.LINE_AA)
                for front_pt, back_pt in zip(xy[:, 0], back[:, 0]):
                    cv2.line(frame, tuple(front_pt), tuple(back_pt), (255, 185, 95), 2, cv2.LINE_AA)
                cv2.putText(frame, "EXTRUDED MESH", tuple(xy[0,0]), cv2.FONT_HERSHEY_SIMPLEX, .48, (255,185,95), 1)
            else:
                cv2.putText(frame, "PLANE", tuple(xy[0,0]), cv2.FONT_HERSHEY_SIMPLEX, .48, COLOR, 1)
        else:
            cv2.polylines(frame, [xy], False, COLOR if not live else (255, 232, 110), 3, cv2.LINE_AA)

    for shape in shapes:
        render(shape)
    if current:
        render({"points": current, "closed": False}, live=True)
    if cursor:
        cv2.circle(frame, cursor, 10, (255, 235, 120), -1, cv2.LINE_AA)
        cv2.circle(frame, cursor, 17, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.rectangle(frame, (0,0), (w,88), (18,26,38), -1)
    mode = "BOX MODE" if box_mode else "PLANE MODE"
    cv2.putText(frame, f"SPATIAL SKETCH  /  {mode}  /  extrusion {depth}px", (18,31), cv2.FONT_HERSHEY_SIMPLEX, .72, (220,245,250), 2)
    cv2.putText(frame, "Point index to draw | close loop = plane/box | B or peace sign: mode | C clear | U undo | +/- depth | Q quit",
                (18,64), cv2.FONT_HERSHEY_SIMPLEX, .48, (160,190,205), 1, cv2.LINE_AA)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    camera = open_camera(args.camera)
    tracker = mp.solutions.hands.Hands(max_num_hands=1, model_complexity=1,
                                      min_detection_confidence=.65, min_tracking_confidence=.65)
    shapes, current = [], []
    box_mode, depth = False, 70
    peace_latched = False
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                raise RuntimeError("The camera stopped returning frames.")
            frame = cv2.flip(frame, 1)
            result = tracker.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            drawing, cursor = False, None
            if result.multi_hand_landmarks:
                hand = result.multi_hand_landmarks[0]
                lm = hand.landmark
                h, w = frame.shape[:2]
                point = (int(lm[8].x * w), int(lm[8].y * h), float(lm[8].z))
                cursor = (point[0], point[1])
                drawing = index_only(lm)
                is_peace = peace_sign(lm)
                if is_peace and not peace_latched:
                    box_mode = not box_mode
                peace_latched = is_peace
                mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
                if drawing:
                    if not current or np.linalg.norm(np.array(point[:2]) - np.array(current[-1][:2])) >= 4:
                        current.append(point)
                elif current:
                    shape = finish_stroke(current, box_mode, depth)
                    if shape:
                        shapes.append(shape)
                    current = []
            else:
                peace_latched = False
                if current:
                    shape = finish_stroke(current, box_mode, depth)
                    if shape:
                        shapes.append(shape)
                    current = []
            draw_scene(frame, shapes, current, cursor, box_mode, depth)
            cv2.imshow("Spatial Sketch", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("b"), ord("B")):
                box_mode = not box_mode
            elif key in (ord("c"), ord("C")):
                shapes.clear()
                current.clear()
            elif key in (ord("u"), ord("U")) and shapes:
                shapes.pop()
            elif key in (ord("+"), ord("=")):
                depth = min(180, depth + 10)
            elif key in (ord("-"), ord("_")):
                depth = max(20, depth - 10)
    finally:
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

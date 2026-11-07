"""Tune HSV bounds with sliders and follow the largest matching object."""
import argparse
import cv2
import numpy as np
from camera_utils import open_camera

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    cv2.namedWindow("HSV Controls")
    for name, maximum, initial in (("H min",179,35),("H max",179,85),("S min",255,80),("S max",255,255),("V min",255,60),("V max",255,255)):
        cv2.createTrackbar(name, "HSV Controls", initial, maximum, lambda _: None)
    camera = open_camera(args.camera)
    kernel = np.ones((5, 5), np.uint8)
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            values = [cv2.getTrackbarPos(name, "HSV Controls") for name in ("H min","H max","S min","S max","V min","V max")]
            lo = np.array([min(values[0], values[1]), min(values[2], values[3]), min(values[4], values[5])])
            hi = np.array([max(values[0], values[1]), max(values[2], values[3]), max(values[4], values[5])])
            mask = cv2.morphologyEx(cv2.inRange(hsv, lo, hi), cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                contour = max(contours, key=cv2.contourArea)
                if cv2.contourArea(contour) > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                    cv2.circle(frame, (x+w//2,y+h//2), 6, (0,0,255), -1)
                    cv2.putText(frame, "Tracked object", (x, max(25,y-8)), cv2.FONT_HERSHEY_SIMPLEX, .65, (0,255,0), 2)
            cv2.imshow("Color Tracking", frame)
            cv2.imshow("Color Mask", mask)
            if cv2.waitKey(1) & 0xFF in (ord("q"),27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

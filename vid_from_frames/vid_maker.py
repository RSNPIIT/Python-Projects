import cv2 as c
import os as o

#Static and Path Variables
FILEPATH = '~/Videos/Screencasts/Comp_VisImp'
FRAME_DIR = o.path.expanduser(FILEPATH)
OUT_VID = 'output.mp4'
STRTIN = "Frame00000.jpg"

#Get the First Frame this will allow us to make a rough assumption of the entire data
fir = c.imread(f'{FRAME_DIR}/{STRTIN}')
h , w , _ = fir.shape

out = c.VideoWriter(OUT_VID , c.VideoWriter_fourcc(*'mp4v') , 52, (w, h))

for i in range(1571):
    frame = c.imread(f"{FRAME_DIR}/Frame{i:05d}.jpg")
    out.write(frame)
    print(f"Added the {i+1}th frame in the video")

out.release()
print("\nVideo Is Ready\nPlease Enjoy")
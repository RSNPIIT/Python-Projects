import cv2 as c
import os as o
import pandas as pd

# Static and Path Variables 
# (NOTE :- This Path will work only in POSIX based systems not on NT ones)
FILEPATH = '~/Videos/Screencasts/Comp_VisImp'
FRAME_DIR = o.path.expanduser(FILEPATH)
OUT_VID = 'output.mp4'
STRTIN = "Frame00000.jpg"
MYCSVFILE = 'teller.csv'
data = pd.read_csv(MYCSVFILE)

#Extracting the Frames in List Form
the_lis = data.Frames.to_list()
lim = len(the_lis)

#Get the First Frame this will allow us to make a rough assumption of the entire data
fir = c.imread(f'{FRAME_DIR}/{STRTIN}')
h , w , _ = fir.shape

#Make the video from the stats of the 1st frame
out = c.VideoWriter(OUT_VID , c.VideoWriter_fourcc(*'mp4v') , 52, (w, h))

#Loop around adding more
for i in range(lim):
    frame = c.imread(f"{FRAME_DIR}/Frame{i:05d}.jpg")
    out.write(frame)
    print(f"Added the frame number :- {i+1} in the video")

#Release the resourses to prevent deadlock
out.release()
print("\nVideo Is Ready\nPlease Enjoy")
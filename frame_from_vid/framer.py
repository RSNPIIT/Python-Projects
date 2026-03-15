#My first project in OpenCv 
#Named the cv2 library after a legendary godfather language
import cv2 as c

FILE = 'exp.mp4'

def capture(vid):
    vid_bj = c.VideoCapture(vid)

    suc = True
    co = 0

    while suc:
        suc, image = vid_bj.read()

        if image is None:
            suc = False
            break

        c.imwrite(f"Frame{co:05d}.jpg" , image)
        print(f"Frame {co} done ")
        co += 1
    
    vid_bj.release()
    print(f"Done -- Extracted {co} frames in the Video !")

if __name__ == '__main__':
    print("Started\nDoing")
    capture(FILE)
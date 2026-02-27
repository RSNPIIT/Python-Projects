from pytube import YouTube
import tkinter as tk
import traceback as trc
import pyperclip as cl
from tkinter import filedialog as fld

def download_vid(url , save_pat):
    try:
        yt = YouTube(url)
        print(f"Title : {yt.title}")
        stre = yt.streams.filter(progressive = True , file_extension = 'mp4')
        hig_stre = stre.get_highest_resolution()
        hig_stre.download(output_path = save_pat)
        print("\nVideo Downloaded Successfully")
    except Exception as e:
        print(f'Error Occurred ->\n{e}')
        trc.print_exc()

def open_file_dialog():
    folder = fld.askdirectory()
    if folder:
        print(f"Selected Folder : {folder}")

    return folder

URL = 'https://youtu.be/HHxkBq2PuJo?si=1ocHi6kcjxQFyAOi'
cl.copy(URL)

if __name__ == '__main__':
    sc = tk.Tk() 
    sc.withdraw()

    vid_url = input('Please Enter a Valid Youtube URL : ')
    save_dir = open_file_dialog()

    if save_dir:
        print('Started Download -----')
        download_vid(vid_url , save_dir)
    else:
        print('Invalid Save Location or Link Given')

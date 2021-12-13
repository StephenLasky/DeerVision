import cv2
import os

def num_frames(cap):
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

def get_frame(cap, num):
    cap.set(1, num)
    success, frame = cap.read()
    return frame

def get_files_in_folder(folder):
    contents = os.listdir(folder)
    return_contents = []

    for content in contents:
        if os.path.isfile(folder + content): return_contents.append(folder + content)
        elif os.path.isdir(folder + content): return_contents += get_files_in_folder(folder + content + "/")
        else: print(folder + content + " is not a file/dir")

    return return_contents
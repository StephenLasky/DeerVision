import cv2

def num_frames(cap):
    return int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

def get_frame(cap, num):
    cap.set(1, num)
    success, frame = cap.read()
    return frame
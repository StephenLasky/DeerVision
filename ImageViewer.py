"""
Purpose of this script is to act as a simple viewer of labeled images.
"""

import DatasetManager
import ImageDispenser
from enums import *
import cv2
import numpy as np

def merge_images(ims, n=4):
    assert n == 4

    h, w, ch = ims[0].shape
    canvas = np.zeros((h*2, w*2, ch), dtype=ims[0].dtype)

    canvas[:h, :w] = ims[0]
    canvas[h:, :w] = ims[1]
    canvas[:h, w:] = ims[2]
    canvas[h:, w:] = ims[3]

    return canvas

def load_image(dm, imd):
    location, date, cam, vid, frame = imd.frame_info()
    label_data = dm.retrieve_labels(location, date, cam, vid, frame)
    print("Got labels: {}".format(label_data))

    im = imd.dispense().astype(np.uint8).copy()

    for label in label_data:
        c, x1, y1, x2, y2 = label

        color = (0, 255, 0)
        im = cv2.line(im, (x1, y1), (x2, y1), color)
        im = cv2.line(im, (x2, y1), (x2, y2), color)
        im = cv2.line(im, (x1, y2), (x2, y2), color)
        im = cv2.line(im, (x1, y2), (x1, y1), color)

    return im

if __name__ == "__main__":
    dm = DatasetManager.DatasetManager("test.db")
    l = dm.get_frames_with_objects()

    imd = ImageDispenser.ImageDispenser(input_folder=GENERAL_INPUT_PATH, only=l)

    while True:
        ims = []
        for i in range(4):
            ims.append(load_image(dm, imd))
            imd.next()

        im = merge_images(ims)

        cv2.imshow('win', im)
        cv2.waitKey(0)
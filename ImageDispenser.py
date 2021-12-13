from common import get_files_in_folder, num_frames, get_frame
import cv2
from random import shuffle

class ImageDispenser:
    def __init__(self, input_folder):
        self.file_paths = get_files_in_folder(input_folder)
        self.num_frames = []

        # delete non-avi files
        i = 0
        while i < len(self.file_paths):
            if self.file_paths[i].split(".")[-1] != "AVI":
                del self.file_paths[i]
            else: i += 1

        print("ID: Found {} videos!".format(len(self.file_paths)))

        self.index_to_vid_frame = []

        for i in range(len(self.file_paths)):
            fp = self.file_paths[i]
            cap = cv2.VideoCapture(fp)
            self.num_frames.append(num_frames(cap))

            for j in range(self.num_frames[-1]):
                self.index_to_vid_frame.append((i, j))    # (video number, frame number)

        self.sequence = list(range(len(self.index_to_vid_frame)))
        shuffle(self.sequence)
        self.current_frame = 0

    def dispense(self):
        frame_num = self.sequence[self.current_frame]

        print("Dispensing index:{} -> vid:{} frame:{} path:{}".format(
            frame_num,
            self.index_to_vid_frame[frame_num][0],
            self.index_to_vid_frame[frame_num][1],
            self.file_paths[self.index_to_vid_frame[frame_num][0]]
        ))

        frame = self.get_frame(frame_num)
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5)

        return frame

    def next(self):
        self.current_frame = min(self.current_frame + 1, len(self.sequence) - 1)

    def prev(self):
        self.current_frame = max(self.current_frame - 1, 0)

    def get_frame(self, index):
        vid, frame = self.index_to_vid_frame[index]     # convert index to a video # and frame #
        cap = cv2.VideoCapture(self.file_paths[vid])    # open video capture

        return get_frame(cap, frame)                    # open numpy array from common library
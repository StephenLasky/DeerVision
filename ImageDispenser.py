from common import get_files_in_folder, num_frames, get_frame
import cv2
from random import shuffle, seed
from enums import *

class ImageDispenser:
    def __init__(self, input_folder, exclusions = [], only = []):
        self.file_paths = get_files_in_folder(input_folder)
        self.num_frames = []
        self.exclusions = exclusions
        self.only = only
        self.index_to_vid_frame = []
        self.sequence = None
        self.current_index = None

        assert not (len(exclusions) > 0 and len(only) > 0), "Cannot use exclude and only at the same time!"

        seed(0)

        # delete non-avi files
        i = 0
        while i < len(self.file_paths):
            if self.file_paths[i].split(".")[-1] != "AVI":
                del self.file_paths[i]
            else: i += 1

        print("ID: Found {} videos!".format(len(self.file_paths)))

        for i in range(len(self.file_paths)):
            fp = self.file_paths[i]
            cap = cv2.VideoCapture(fp)
            self.num_frames.append(num_frames(cap))

            for j in range(self.num_frames[-1]):
                self.index_to_vid_frame.append((i, j))    # (video number, frame number)

        self.sequence = list(range(len(self.index_to_vid_frame)))
        shuffle(self.sequence)
        self.current_index = -1
        self.next()

    def dispense(self):
        frame_index = self.sequence[self.current_index]

        print("Dispensing index:{} -> vid:{} frame:{} path:{}".format(
            frame_index,
            self.index_to_vid_frame[frame_index][0],
            self.index_to_vid_frame[frame_index][1],
            self.file_paths[self.index_to_vid_frame[frame_index][0]]
        ))

        frame = self.get_frame(frame_index)
        frame = cv2.resize(frame, None, fx=IMAGE_SCALE_FACTOR, fy=IMAGE_SCALE_FACTOR)

        return frame[:,:,[2, 1, 0]]

    def dispense_video(self):
        index = self.sequence[self.current_index]

        vid, frame = self.index_to_vid_frame[index]     # convert index to a video # and frame #
        cap = cv2.VideoCapture(self.file_paths[vid])    # open video capture

        return cap

    def frame_info(self, index=None):
        if index is None: index = self.current_index

        frame_index = self.sequence[index]
        frame = self.index_to_vid_frame[frame_index][1]
        path = self.file_paths[self.index_to_vid_frame[frame_index][0]]

        x = path.split("/")
        location, date, cam, vid = x[-4], x[-3], x[-2], x[-1]

        location = LOCATION_TO_INT[location]
        cam = int(cam.split("_")[-1])
        vid = int(vid[4:].split(".")[0])

        return location, date, cam, vid, frame

    def video_path(self):
        return self.file_paths[self.index_to_vid_frame[self.sequence[self.current_index]][0]]

    def next(self):
        self.current_index = min(self.current_index + 1, len(self.sequence) - 1)
        print("Now on {}".format(self.frame_info()))

        # when we are operating in 'only mode', skip frames that are not found in the 'only' section
        if len(self.only) > 0 and self.current_index < len(self.sequence):
            while not self.in_only(self.current_index):
                last_idx = self.current_index
                self.current_index = min(self.current_index + 1, len(self.sequence) - 1)

                if last_idx == self.current_index:
                    assert False, "Infinite loop!"
                print(self.current_index)

        # skip frames that have already been labeled here
        while self.is_excluded(self.current_index) and self.current_index < len(self.sequence):
            print("Skipping ...")
            self.current_index = min(self.current_index + 1, len(self.sequence) - 1)

        if self.does_frame_exist() == False:
            print("WARNING: DEAD FRAME!")
            self.next()    # skip 'dead' frames

    def prev(self):
        self.current_index = max(self.current_index - 1, 0)

        # when we are operating in 'only mode', skip frames that are not found in the 'only' section
        if len(self.only) > 0:
            while not self.in_only(self.current_index):
                self.prev()

        while self.is_excluded(self.current_index) and self.current_index > 0:
            print("Skipping ...")
            self.prev()

        if self.does_frame_exist() == False:
            print("WARNING: DEAD FRAME!")
            self.prev()    # skip 'dead' frames

    def does_frame_exist(self):
        frame = self.get_frame()

        if type(frame) == type(None): return False
        else: return True

    def get_frame(self, index=None):
        if index is None: index = self.sequence[self.current_index]
        vid, frame = self.index_to_vid_frame[index]     # convert index to a video # and frame #
        cap = cv2.VideoCapture(self.file_paths[vid])    # open video capture

        return get_frame(cap, frame)                    # open numpy array from common library

    def is_excluded(self, index):
        if len(self.exclusions) == 0: return False

        location, date, cam, vid, frame = self.frame_info(index)    # todo: optimize this!

        for i in range(len(self.exclusions)):
            if (location, date, cam, vid ,frame) == self.exclusions[i]:
                return True

        return False

    def in_only(self, index):
        location, date, cam, vid, frame = self.frame_info(index)

        for i in range(len(self.only)):
            if (location, date, cam, vid ,frame) == self.only[i]:
                return True

        return False

    def get_vid_frame_ct(self, index=None):
        if index is None: index = self.current_index

        vid, frame = self.index_to_vid_frame[index]     # convert index to a video # and frame #
        cap = cv2.VideoCapture(self.file_paths[vid])    # open video capture

        return num_frames(cap)

    def set_exclusions(self, exclusions):
        old_ct = len(self.exclusions)
        self.exclusions = exclusions

        print("Exclusions updated from {}->{}".format(old_ct, len(self.exclusions)))
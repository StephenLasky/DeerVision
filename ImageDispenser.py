from common import get_files_in_folder, num_frames
import cv2

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

        for fp in self.file_paths:
            cap = cv2.VideoCapture(fp)
            self.num_frames.append(num_frames(cap))
            
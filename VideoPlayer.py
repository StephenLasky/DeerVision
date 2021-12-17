from threading import Lock, Thread
from PIL import Image, ImageTk
from time import sleep, time
from common import num_frames
import cv2

class VideoPlayer:
    def __init__(self, path, vid_lbl, size = (960, 540), workers=8):
        self.size = size
        self.path = path

        self.vid_lbl_lock = Lock()
        self.vid_lbl_frame = 0
        self.vid_lbl = vid_lbl

        self.frame_buffer = 0
        self.buffer_lock = Lock()

        self.frame_step = 2
        self.worker_ct = workers

    def play(self):
        self.start_time = time()

        for i in range(self.worker_ct):
            thread = Thread(target=self.frame_worker)
            thread.daemon = 1
            thread.start()

    def frame_worker(self):
        cap = cv2.VideoCapture(self.path)
        frame_ct = num_frames(cap)

        while True:
            # get the frame which needs loaded
            self.buffer_lock.acquire()
            if self.frame_buffer >= frame_ct:
                self.buffer_lock.release()
                print("Thread finished at {:.2f} seconds".format(time() - self.start_time))
                break
            frame_num = self.frame_buffer
            self.frame_buffer += self.frame_step
            self.buffer_lock.release()

            # load the frame into memory
            cap.set(1, frame_num)
            success, frame = cap.read()

            if success == False:
                print("Thread finished at {:.2f} seconds".format(time() - self.start_time))
                break

            # convert to something we can use
            frame = ImageTk.PhotoImage(Image.fromarray(frame).resize(self.size))

            while True:
                self.vid_lbl_lock.acquire()
                if frame_num != self.vid_lbl_frame:
                    self.vid_lbl_lock.release()
                    sleep(0.005)
                    continue
                else:
                    self.vid_lbl.config(image=frame)
                    self.vid_lbl.image = frame
                    self.vid_lbl_frame += self.frame_step
                    self.vid_lbl_lock.release()
                    break


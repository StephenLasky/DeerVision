from threading import Lock, Thread
from PIL import Image, ImageTk
import os
from enums import *
from time import sleep, time
from common import num_frames

class VideoPlayer:
    def __init__(self, cap, label, size = (960, 540)):
        os.environ["IMAGEIO_FFMPEG_EXE"] = IMAGEIO_FFMPEG_EXE
        self.size = size

        self.cap = cap
        self.cap_lock = Lock()

        self.label_lock = Lock()
        self.label_frame = 0
        self.label = label

        self.frame_buffer = 0
        self.buffer_lock = Lock()

        self.threads = []

        self.frame_step = 10
        self.frame_ct = num_frames(cap)

    def play(self):
        self.start_time = time()

        for i in range(1):
            thread = Thread(target=self.frame_worker)
            thread.daemon = 1
            thread.start()

            self.threads.append(thread)

        print("Finished!")

    def frame_worker(self):
        while True:
            # get the frame which needs loaded
            self.buffer_lock.acquire()
            if self.frame_buffer >= self.frame_ct:
                self.buffer_lock.release()
                print("Thread finished at {:.2f} seconds".format(time() - self.start_time))
                break
            frame_num = self.frame_buffer
            self.frame_buffer += self.frame_step
            self.buffer_lock.release()


            # load the frame into memory
            self.cap_lock.acquire()
            self.cap.set(1, frame_num)
            success, frame = self.cap.read()
            self.cap_lock.release()

            # convert to something we can use
            frame = ImageTk.PhotoImage(Image.fromarray(frame).resize(self.size))

            while True:
                self.label_lock.acquire()
                if frame_num != self.label_frame:
                    self.label_lock.release()
                    print("oops")
                    sleep(0.005)
                    continue
                else:
                    self.label.config(image=frame)
                    self.label.image = frame
                    self.label_frame += self.frame_step
                    self.label_lock.release()
                    break


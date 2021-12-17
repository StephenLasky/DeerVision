from threading import Lock, Thread
import imageio
from PIL import Image, ImageTk
import os
from enums import *
from time import sleep, time

class VideoPlayer:
    def __init__(self, path, label, size = (960, 540)):
        os.environ["IMAGEIO_FFMPEG_EXE"] = IMAGEIO_FFMPEG_EXE
        self.path = path
        self.size = size

        self.iterator = imageio.get_reader(self.path).iter_data()
        self.iterator_frame = 0
        self.iterator_lock = Lock()

        self.label_lock = Lock()
        self.label_frame = 0
        self.label = label

        self.threads = []

    def play(self):
        self.start_time = time()

        for i in range(2):
            thread = Thread(target=self.frame_worker)
            thread.daemon = 1
            thread.start()

            self.threads.append(thread)

        print("Finished!")

    def frame_worker(self):
        while True:
            # get the actual frame
            self.iterator_lock.acquire()
            try:
                frame = next(self.iterator)
            except StopIteration:
                print("Finished in {:.2f} seconds".format(time() - self.start_time))
                break
            frame_num = self.iterator_frame
            self.iterator_frame += 1
            self.iterator_lock.release()

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
                    self.label_frame += 1
                    self.label_lock.release()

                    break

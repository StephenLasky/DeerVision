from tkinter import *
from enums import *

class ManualLabeler:
    def __init__(self):
        window = Tk()
        window.title("Main window")
        window.config(background='gray')

        self.canvas = Canvas(window, height=480, width=480)
        self.canvas.grid(row=0, column=0)

        # set image
        self.set_image(TEST_PATH_IMG_PATH)

        window.mainloop()

    def set_image(self, path):
        # image = ImageTk.PhotoImage(file = path)
        bg = PhotoImage(file=path)
        self.canvas.create_image(0,0, anchor=NW, image=bg)
        self.canvas.image = bg
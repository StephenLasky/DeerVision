from tkinter import *
from enums import *
from PIL import Image, ImageTk

class ManualLabeler:
    def __init__(self, dispenser):
        self.dispenser = dispenser

        window = Tk()
        window.title("Main window")
        window.config(background='gray')

        # set up main canvas
        self.canvas = Canvas(window, height=1080/2, width=1920/2)
        self.canvas.grid(row=0, column=0, columnspan=2)

        # set up buttons
        self.prev_btn = Button(window, text="Prev", command=self.prev_btn_press)
        self.prev_btn.grid(row=1, column=0)
        self.next_btn = Button(window, text="Next", command=self.next_btn_press)
        self.next_btn.grid(row=1, column=1)

        # set image
        self.set_image(dispenser.dispense())

        window.mainloop()

    def set_image(self, np_array):
        bg = ImageTk.PhotoImage(Image.fromarray(np_array))
        self.canvas.create_image(0,0, anchor=NW, image=bg)
        self.canvas.image = bg

    def next_btn_press(self):
        self.dispenser.next()
        self.set_image(self.dispenser.dispense())

    def prev_btn_press(self):
        self.dispenser.prev()
        self.set_image(self.dispenser.dispense())
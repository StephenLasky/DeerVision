from enums import *

class BoundingBox:
    def __init__(self, canvas, startx, starty, endx, endy):
        self.canvas = canvas

        self.startx, self.starty = startx, starty
        self.endx, self.endy = endx, endy

        self.rect, self.text, self.textbg = self.create()

    def create(self):
        rect = self.canvas.create_rectangle(self.startx, self.starty, self.endx, self.endy, outline=SELECTED_BB_COLOR)
        text = self.canvas.create_text(self.startx, self.starty, fill="black", text=TEXT_UNLABELED, anchor="nw")

        startx, starty, endx, endy = self.canvas.bbox(text)
        textbg = self.canvas.create_rectangle(startx, starty, endx, endy, outline="", fill=SELECTED_BB_COLOR)

        self.canvas.lift(text)

        return rect, text, textbg

    def select(self):
        self.canvas.itemconfig(self.rect, outline=SELECTED_BB_COLOR)
        self.canvas.itemconfig(self.textbg, fill=SELECTED_BB_COLOR)
    def unselect(self):
        self.canvas.itemconfig(self.rect, outline=UNSELECTED_BB_COLOR)
        self.canvas.itemconfig(self.textbg, fill=UNSELECTED_BB_COLOR)

    def update(self, startx=None, starty=None, endx=None, endy=None):
        if startx is not None: delta_x = startx - self.startx
        else: delta_x = 0

        if starty is not None: delta_y = starty - self.starty
        else: delta_y = 0

        if startx is not None: self.startx = startx
        if starty is not None: self.starty = starty
        if endx is not None: self.endx = endx
        if endy is not None: self.endy = endy

        self.canvas.coords(self.rect, self.startx, self.starty, self.endx, self.endy)
        self.canvas.coords(self.text, self.startx, self.starty)

        x1, y1, x2, y2 = self.canvas.bbox(self.textbg)
        self.canvas.coords(self.textbg, x1 + delta_x, y1 + delta_y , x2 + delta_x, y2 + delta_y)

    def get_coords(self):
        return self.startx, self.starty, self.endx, self.endy

    def label(self, text):
        self.canvas.itemconfig(self.text, text=text)

        startx, starty, endx, endy = self.canvas.bbox(self.text)
        self.canvas.coords(self.textbg, startx, starty, endx, endy)

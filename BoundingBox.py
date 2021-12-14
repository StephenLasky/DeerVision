from enums import *

class BoundingBox:
    def __init__(self, canvas, startx, starty, endx, endy):
        self.canvas = canvas

        self.startx, self.starty = startx, starty
        self.endx, self.endy = endx, endy

        self.rect = self.create()

    def create(self):
        return self.canvas.create_rectangle(self.startx, self.starty, self.endx, self.endy, outline=SELECTED_BB_COLOR)

    def select(self):
        self.canvas.itemconfig(self.rect, outline=SELECTED_BB_COLOR)
    def unselect(self):
        self.canvas.itemconfig(self.rect, outline=UNSELECTED_BB_COLOR)

    def update(self, startx=None, starty=None, endx=None, endy=None):
        if startx is not None: self.startx = startx
        if starty is not None: self.starty = starty
        if endx is not None: self.endx = endx
        if endy is not None: self.endy = endy

        self.canvas.coords(self.rect, self.startx, self.starty, self.endx, self.endy)

    def get_coords(self):
        return self.startx, self.starty, self.endx, self.endy

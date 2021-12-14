from tkinter import *
from enums import *
from PIL import Image, ImageTk
from BoundingBox import BoundingBox

class ManualLabeler:
    def __init__(self, dispenser):
        self.dispenser = dispenser

        window = Tk()
        window.title("Main window")
        window.config(background='gray')

        # set up main canvas
        self.canvas = Canvas(window, height=1080/2, width=1920/2)
        self.canvas.grid(row=0, column=0, columnspan=5)

        # set up buttons
        self.prev_btn = Button(window, text="Prev", command=self.prev_btn_press)
        self.prev_btn.grid(row=1, column=0)
        self.next_btn = Button(window, text="Next", command=self.next_btn_press)
        self.next_btn.grid(row=1, column=4)

        # set up classify buttons
        self.deer_btn = Button(window, text="Deer", command=self.deer_btn_press)
        self.pig_btn = Button(window, text="Pig", command=self.pig_btn_press)
        self.man_btn = Button(window, text="Man", command=self.man_btn_press)
        self.coyote_btn = Button(window, text="Coyote", command=self.coyote_btn_press)
        self.squirrel_btn = Button(window, text="Squirrel", command=self.squirrel_btn_press)

        self.deer_btn.grid(row=2, column=0)
        self.pig_btn.grid(row=2, column=1)
        self.man_btn.grid(row=2, column=2)
        self.coyote_btn.grid(row=2, column=3)
        self.squirrel_btn.grid(row=2, column=4)

        # set initial image
        self.set_image(dispenser.dispense())

        # bound mouse movement to the canvas
        self.canvas.bind("<ButtonPress-1>", self.canvas_press)
        self.canvas.bind("<B1-Motion>", self.canvas_press_move)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_press_release)
        self.startx, self.starty = None, None
        self.rects = []                                 # (rect num, start x, start y, end x, end y )
        self.rect_id = None
        self.drag_mode = None
        self.drag_side = None

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

    def between(self, X, a, b):
        lo = min(a,b)
        hi = max(a,b)

        if lo <= X and X <= hi: return True
        else: return False

    def find_nearest_rectangle(self, x, y):
        """
        Given an x/y coordinate pair - find the nearest rectangle in the current frame.
        :param x: x coordinate
        :param y: y coordinate
        :return: (rectangle_id, SIDE)
        """

        selection_width = 25

        for i in range(len(self.rects)):
            startx, starty, endx, endy = self.rects[i].get_coords()

            if abs(startx - x) < selection_width and self.between(y, starty, endy): return (i, LEFT)
            elif abs(endx - x) < selection_width and self.between(y, starty, endy): return (i, RIGHT)
            elif abs(starty - y) < selection_width and self.between(x, startx, endx): return (i, TOP)
            elif abs(endy - y) < selection_width and self.between(x, startx, endx): return (i, BOTTOM)

        return (None, None)

    def reset_rectangles(self):
        for i in range(len(self.rects)): self.rects[i].unselect()

    def canvas_press(self, event):
        self.reset_rectangles()

        print("Click event at coordinates {}, {}".format(event.x, event.y))

        nearest_rect_id, side = self.find_nearest_rectangle(event.x, event.y)
        print("Found neighbor {}".format(nearest_rect_id))

        # Case 1: No rectangle found, create new one
        if nearest_rect_id == None:
            self.drag_mode = DRAG_MODE_CREATE_RECT

            self.rects.append(BoundingBox(self.canvas, event.x, event.y, event.x, event.y))
            self.rect_id = len(self.rects) - 1

        else:
            self.drag_mode = DRAG_MODE_MODIFY_RECT

            self.rect_id = nearest_rect_id
            self.drag_side = side

            self.rects[self.rect_id].select()

    def canvas_press_move(self, event):
        startx, starty, endx, endy = None, None, None, None

        if self.drag_mode == DRAG_MODE_CREATE_RECT:
            endx, endy = event.x, event.y
        elif self.drag_mode == DRAG_MODE_MODIFY_RECT:
            if self.drag_side == TOP: starty = event.y
            elif self.drag_side == BOTTOM: endy = event.y
            elif self.drag_side == LEFT: startx = event.x
            elif self.drag_side == RIGHT: endx = event.x

        self.rects[self.rect_id].update(startx, starty, endx, endy)

    def canvas_press_release(self, event):
        print("Release event at coordinates {}, {}".format(event.x, event.y))

        self.canvas_press_move(event)

    def deer_btn_press(self):
        self.rects[self.rect_id].label(TEXT_DEER)

    def pig_btn_press(self):
        self.rects[self.rect_id].label(TEXT_PIG)

    def man_btn_press(self):
        self.rects[self.rect_id].label(TEXT_MAN)

    def coyote_btn_press(self):
        self.rects[self.rect_id].label(TEXT_COYOTE)

    def squirrel_btn_press(self):
        self.rects[self.rect_id].label(TEXT_SQUIRREL)
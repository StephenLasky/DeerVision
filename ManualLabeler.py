from tkinter import *
from enums import *
from PIL import Image, ImageTk
from BoundingBox import BoundingBox
from DatasetManager import DatasetManager
from VideoPlayer import VideoPlayer

class ManualLabeler:
    def __init__(self, dispenser):
        self.dispenser = dispenser
        self.dataset_manager = DatasetManager(TEST_DB_NAME)

        window = Tk()
        window.title("Main window")
        window.config(background='gray')

        # set up main canvas
        self.canvas = Canvas(window, height=1080/2, width=1920/2)
        self.canvas.grid(row=0, column=0, columnspan=5)

        # set up buttons
        self.prev_btn = Button(window, text="Prev", command=self.prev_btn_press)
        self.prev_btn.grid(row=1, column=0)
        self.confirm_btn = Checkbutton(window, text="Confirm", command=self.confirm_btn_press)
        self.confirm_btn.grid(row=1, column=3)
        self.confirm_btn_state = LABEL_STATUS_UNLABELED
        self.play_btn = Button(window, text="Play", command=self.play_btn_press)
        self.play_btn.grid(row=1, column=2)
        self.next_btn = Button(window, text="Next", command=self.next_btn_press)
        self.next_btn.grid(row=1, column=4)

        # video stuff
        self.vid_lbl = Label(window)
        self.vid_lbl.grid(row=0, column=5)
        self.vid_player = VideoPlayer(self.dispenser.video_path(), self.vid_lbl)

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
        self.load_frame()

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

    def load_frame(self):
        # build the new frame
        location, date, cam, vid, frame = self.dispenser.frame_info()
        self.rects = []         # todo: delete them literally instead of passively "forgetting"
        self.rect_id = None
        raw_label_data = self.dataset_manager.retrieve_labels(location, date, cam, vid, frame)  # pull raw SQL data

        # go through every row of saved data - turned them into bounding boxes.
        for row in raw_label_data:
            num_class, start_x, start_y, end_x, end_y = row
            self.rects.append(BoundingBox(self.canvas, start_x, start_y, end_x, end_y))
            self.rect_id = len(self.rects) - 1
            self.rects[self.rect_id].label(CLASS_NUM_TO_TEXT[num_class])
            self.rects[self.rect_id].unselect()

        if len(self.rects) > 0: self.rects[0].select()    # ensure *something* is selected

        # load checkmark state
        self.confirm_btn_state = self.dataset_manager.retrieve_frame_state(location, date, cam, vid, frame)
        if self.confirm_btn_state == LABEL_STATUS_UNLABELED: self.confirm_btn.deselect()
        elif self.confirm_btn_state == LABEL_STATUS_LABELED: self.confirm_btn.select()

        # load video
        self.vid_player = VideoPlayer(self.dispenser.video_path(), self.vid_lbl)

    def next_btn_press(self):
        self.dispenser.next()
        self.set_image(self.dispenser.dispense())
        self.load_frame()

    def prev_btn_press(self):
        self.dispenser.prev()
        self.set_image(self.dispenser.dispense())
        self.load_frame()

    def confirm_btn_press(self):
        new_state = None

        if self.confirm_btn_state == LABEL_STATUS_UNLABELED: new_state = LABEL_STATUS_LABELED
        elif self.confirm_btn_state == LABEL_STATUS_LABELED: new_state = LABEL_STATUS_UNLABELED

        location, date, cam, vid, frame = self.dispenser.frame_info()
        self.dataset_manager.update_frame_state(location, date, cam, vid, frame, new_state)

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

            if abs(startx - x) < selection_width and abs(starty - y) < selection_width: return (i, TOP_LEFT)
            elif abs(startx - x) < selection_width and abs(endy - y) < selection_width: return (i, BOT_LEFT)
            elif abs(endx - x) < selection_width and abs(starty - y) < selection_width: return (i, TOP_RIGHT)
            elif abs(endx - x) < selection_width and abs(endy - y) < selection_width: return (i, BOT_RIGHT)

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
            # Corner dragging - takes priority
            if self.drag_side == TOP_LEFT: startx, starty = event.x, event.y
            elif self.drag_side == TOP_RIGHT: endx, starty = event.x, event.y
            elif self.drag_side == BOT_RIGHT: endx, endy = event.x, event.y
            elif self.drag_side == BOT_LEFT: startx, endy = event.x, event.y

            # Side dragging
            elif self.drag_side == TOP: starty = event.y
            elif self.drag_side == BOTTOM: endy = event.y
            elif self.drag_side == LEFT: startx = event.x
            elif self.drag_side == RIGHT: endx = event.x

        self.rects[self.rect_id].update(startx, starty, endx, endy)

    def canvas_press_release(self, event):
        print("Release event at coordinates {}, {}".format(event.x, event.y))

        self.canvas_press_move(event)

    def deer_btn_press(self):
        self.rects[self.rect_id].label(TEXT_DEER)
        location, date, cam, vid, frame = self.dispenser.frame_info()
        start_x, start_y, end_x, end_y = self.rects[self.rect_id].get_coords()

        self.dataset_manager.create_label(
            location, date, cam, vid, frame, NUM_DEER, start_x, start_y, end_x, end_y
        )

    def pig_btn_press(self):
        self.rects[self.rect_id].label(TEXT_PIG)
        location, date, cam, vid, frame = self.dispenser.frame_info()
        start_x, start_y, end_x, end_y = self.rects[self.rect_id].get_coords()

        self.dataset_manager.create_label(
            location, date, cam, vid, frame, NUM_PIG, start_x, start_y, end_x, end_y
        )

    def man_btn_press(self):
        self.rects[self.rect_id].label(TEXT_MAN)
        location, date, cam, vid, frame = self.dispenser.frame_info()
        start_x, start_y, end_x, end_y = self.rects[self.rect_id].get_coords()

        self.dataset_manager.create_label(
            location, date, cam, vid, frame, NUM_MAN, start_x, start_y, end_x, end_y
        )

    def coyote_btn_press(self):
        self.rects[self.rect_id].label(TEXT_COYOTE)
        location, date, cam, vid, frame = self.dispenser.frame_info()
        start_x, start_y, end_x, end_y = self.rects[self.rect_id].get_coords()

        self.dataset_manager.create_label(
            location, date, cam, vid, frame, NUM_COYOTE, start_x, start_y, end_x, end_y
        )

    def squirrel_btn_press(self):
        self.rects[self.rect_id].label(TEXT_SQUIRREL)
        location, date, cam, vid, frame = self.dispenser.frame_info()
        start_x, start_y, end_x, end_y = self.rects[self.rect_id].get_coords()

        self.dataset_manager.create_label(
            location, date, cam, vid, frame, NUM_SQUIRREL, start_x, start_y, end_x, end_y
        )

    def play_btn_press(self):
        print("Play button pressed.")
        self.vid_player.play()
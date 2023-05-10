import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from settings import *


class Paint(ttk.Frame):
    def __init__(self, frame):
        # some consts
        super().__init__(master=frame)
        self.x = 0
        self.y = 0
        self.brush_size = 3

        # init
        self.color = 'black'
        self.local_master = frame

        # components
        s = ttk.Style(self)
        s.configure('Paint.TFrame', background=ROOM_FRAME)
        self['style'] = 'Paint.TFrame'
        self.place(relx=0.05, rely=0.18, relwidth=0.95, relheight=0.85)

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.place(relheight=0.9, relwidth=0.83, relx=0, rely=0)
        self.canvas.bind('<B1-Motion>', self.draw)

        self.menu = tk.Menu(self, tearoff=0)
        self.brush_1px = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_1px.png').
                                            resize((BRUSH_ICO_SIZE*3, BRUSH_ICO_SIZE)), master=self)
        self.brush_4px = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_4px.png').
                                            resize((BRUSH_ICO_SIZE * 3, BRUSH_ICO_SIZE)), master=self)
        self.brush_7px = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_7px.png').
                                            resize((BRUSH_ICO_SIZE * 3, BRUSH_ICO_SIZE)), master=self)
        self.brush_13px = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_13px.png').
                                             resize((BRUSH_ICO_SIZE * 3, BRUSH_ICO_SIZE)), master=self)
        self.brush_17px = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_17px.png').
                                             resize((BRUSH_ICO_SIZE * 3, BRUSH_ICO_SIZE)), master=self)
        self.menu.add_command(image=self.brush_1px, command=lambda size=1: self.brush_change(size))
        self.menu.add_command(image=self.brush_4px, command=lambda size=3: self.brush_change(size))
        self.menu.add_command(image=self.brush_7px, command=lambda size=6: self.brush_change(size))
        self.menu.add_command(image=self.brush_13px, command=lambda size=10: self.brush_change(size))
        self.menu.add_command(image=self.brush_17px, command=lambda size=15: self.brush_change(size))

        self.canvas_img = Image.new('RGB', GAME_CANVAS_SIZE, 'white')
        self.image_draw = ImageDraw.Draw(self.canvas_img)
        self.colors = ['black', 'red', 'green', 'yellow', 'white', 'gray', 'brown', 'pink', 'maroon', 'aqua',
                       'violet', 'CadetBlue', 'burlywood', 'indigo', 'purple']
        self.labels = []
        base_x = 0.84
        base_y = 0
        offset_x = 0.05
        offset_y = 0.09
        last_value = (0, 0)
        for i in range(len(self.colors)):
            label = tk.Button(self, bg=self.colors[i], text='', command=lambda index=i: self.on_label_click(index))
            label.place(relx=base_x + (i % 3) * offset_x, rely=base_y + int(i / 3) * offset_y, width=35, height=35)
            last_value = (base_x + (i % 3) * offset_x, base_y + int(i / 3) * offset_y)
            self.labels.append(label)
        self.color_indicator_lbl = tk.Label(self, bg=self.color, width=10)
        self.color_indicator_lbl.place(relx=base_x, rely=last_value[1] + offset_y, relwidth=0.15, relheight=0.08)
        base_y = last_value[1] + offset_y*2
        self.pour_img = ImageTk.PhotoImage(Image.open('../graphics/utility/fill.png').
                                           resize((FILL_ICO_SIZE, FILL_ICO_SIZE)), master=self)
        self.pour_btn = tk.Button(self, image=self.pour_img, command=self.pour)
        self.pour_btn.place(relx=base_x, rely=base_y)
        self.clear_img = ImageTk.PhotoImage(Image.open('../graphics/utility/clear.png').
                                            resize((FILL_ICO_SIZE, FILL_ICO_SIZE)), master=self)
        self.clear_canvas_btn = tk.Button(self, image=self.clear_img, command=self.clear_canvas)
        self.clear_canvas_btn.place(relx=base_x + offset_x, rely=base_y)
        self.eraser_img = ImageTk.PhotoImage(Image.open('../graphics/utility/eraser.png').
                                             resize((FILL_ICO_SIZE, FILL_ICO_SIZE)), master=self)
        self.eraser_btn = tk.Button(self, image=self.eraser_img, command=self.erase)
        self.eraser_btn.place(relx=base_x + 2*offset_x, rely=base_y)
        self.brush_img = ImageTk.PhotoImage(Image.open('../graphics/utility/brush_size.png').
                                            resize((FILL_ICO_SIZE, FILL_ICO_SIZE)), master=self)
        self.brush_btn = tk.Button(self, image=self.brush_img)
        self.brush_btn.bind("<Button-1>", self.popup)
        self.brush_btn.place(relx=base_x, rely=base_y + offset_y)
        self.canvas_bg = None

        self.is_sleep = False

    def brush_change(self, size):
        self.brush_size = size

    def on_label_click(self, index):
        self.color = self.labels[index]['bg']
        self.color_indicator_lbl['bg'] = self.color

    def erase(self):
        self.color = 'white'

    def draw(self, event):
        if not self.is_sleep:
            x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
            x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
            self.canvas.create_oval(x1, y1, x2, y2, fill=self.color, width=0)
            self.image_draw.ellipse((x1, y1, x2, y2), fill=self.color, width=0)

    def select_brush_size(self, value):
        self.brush_size = int(value)

    def unsleep_canvas(self):
        self.is_sleep = False

    def sleep_canvas(self):
        self.is_sleep = True

    def pour(self):
        if not self.is_sleep:
            self.canvas.delete('all')
            self.canvas['bg'] = self.color
            self.image_draw.rectangle(CANVAS_RECT, width=0, fill=self.color)

    def clear_canvas(self):
        if not self.is_sleep:
            self.canvas.delete('all')
            self.canvas['bg'] = 'white'
            self.image_draw.rectangle(CANVAS_RECT, width=0, fill='white')

    def save_img(self):
        pass

    def popup(self, event):
        self.menu.post(event.widget.winfo_rootx(), event.widget.winfo_rooty())

    def place_paint(self):
        self.clear_canvas()
        self.place(relx=0.05, rely=0.18, relwidth=0.95, relheight=0.85)

    def place_forget_paint(self):
        self.place_forget()

    def set_canvas_image(self, image):
        self.canvas_bg = ImageTk.PhotoImage(image)
        self.clear_canvas()
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_bg)

    def capture_img(self):
        return self.canvas_img

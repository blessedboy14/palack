import tkinter as tk
import tkinter.ttk as ttk
from settings import *
from support import center, is_pin_valid, is_description_valid
from PIL import ImageTk, Image
from game_room import GameRoom
from tkinter import messagebox


class CreateWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        # window
        self.title("Palack Paradise")
        self.geometry(f'{CREATE_WIDTH}x{CREATE_HEIGHT}')
        self.resizable(width=False, height=False)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        center(self)
        self.configure(background=CREATE_BG_COLOR, padx=PADDING, pady=PADDING)
        self.half_height = CREATE_HEIGHT / 2
        self.half_width = CREATE_WIDTH / 2
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.created_room = None

        def return_pressed(ev):
            self.create()
        self.bind("<Return>", return_pressed)

        """
        Frame 
        """
        s = ttk.Style(self)
        s.configure('MyCreate.TFrame', background=FRAME_COLOR)
        # s.configure('Test.TFrame', background="black")
        self.bg_frame = ttk.Frame(self, borderwidth=BORDER, style="MyCreate.TFrame")
        self.lbl_frame = ttk.Frame(self.bg_frame, borderwidth=BORDER, style="MyCreate.TFrame")
        self.entry_frame = ttk.Frame(self.bg_frame, borderwidth=BORDER, style="MyCreate.TFrame")
        """
        Text Entries
        """
        self.check_description = (self.register(is_description_valid), "%P")
        self.room_description_input = ttk.Entry(self.entry_frame, font=(FONT_NAME, NAME_INPUT_FONT_SIZE),
                                                validate="key",
                                                validatecommand=self.check_description)
        self.check = (self.register(is_pin_valid), "%P")
        self.pin_input = ttk.Entry(self.entry_frame, font=(FONT_NAME, NAME_INPUT_FONT_SIZE), validate="key",
                                   validatecommand=self.check)
        """
        Combo boxes
        """
        self.room_size_input = ttk.Combobox(self.entry_frame, values=("2", "3", "4", "5", "6"),
                                            font=(FONT_NAME, SIZE_INPUT_FONT_SIZE), state="readonly")
        self.room_size_input.current(0)
        self.room_private_cfg = ttk.Combobox(self.entry_frame, values=("private", "public"),
                                             font=(FONT_NAME, SIZE_INPUT_FONT_SIZE), state="readonly")
        self.room_private_cfg.current(1)
        self.room_private_cfg.bind("<<ComboboxSelected>>", self.change_is_private)
        self.mode_chooser = ttk.Combobox(self.entry_frame, values=["обычный"], font=(FONT_NAME, SIZE_INPUT_FONT_SIZE),
                                         state="readonly")
        self.mode_chooser.current(0)
        """
        Labels
        """
        self.lbl_font = (FONT_NAME, LBL_FONT_SIZE)
        self.room_name_lbl = ttk.Label(self.lbl_frame, text="Введите описание комнаты: ", font=self.lbl_font,
                                       background=FRAME_COLOR)
        self.room_size_lbl = ttk.Label(self.lbl_frame, text="Выберите размер: ", font=self.lbl_font,
                                       background=FRAME_COLOR)
        self.room_private_lbl = ttk.Label(self.lbl_frame, text="Выберите режим комнаты: ", font=self.lbl_font,
                                          background=FRAME_COLOR)
        self.pin_lbl = ttk.Label(self.lbl_frame, text="Введите пароль: ", font=self.lbl_font, background=FRAME_COLOR)
        self.mode_chooser_lbl = ttk.Label(self.lbl_frame, text="Выберите режим: ",
                                          font=self.lbl_font, background=FRAME_COLOR)
        """
        Other
        """
        eye_width = int(EYE_ICO_SIZE * 5 / 4)
        self.opened_eye = ImageTk.PhotoImage(Image.open('../graphics/utility/opened_eye.png').
                                             resize((eye_width, EYE_ICO_SIZE)), master=self)
        self.closed_eye = ImageTk.PhotoImage(Image.open('../graphics/utility/closed_eye.png').
                                             resize((eye_width, EYE_ICO_SIZE)), master=self)
        val = tk.IntVar(value=1)
        self.visible_password_checkbox = tk.Checkbutton(self.entry_frame, image=self.closed_eye, variable=val,
                                                        bg=FRAME_COLOR, command=self.check_visibility,
                                                        selectcolor=FRAME_COLOR, activebackground=FRAME_COLOR)
        self.confirm_button = tk.Button(self.bg_frame, text="Создать", font=self.lbl_font, command=self.create)
        self.is_private = False
        self.is_password_visible = False
        self.change_is_private(None)
        self.check_visibility()

    def get_created_room(self):
        return self.created_room

    def is_fields_fulfill(self):
        is_fulfill = True
        is_fulfill = is_fulfill and (len(self.room_description_input.get()) > 0) and \
                                    (self.is_private and (len(self.pin_input.get()) > 0)
                                     or (not self.is_private and True))
        return is_fulfill

    def create(self):
        if self.is_fields_fulfill():
            self.created_room = GameRoom(None, None, self.room_description_input.get(), self.room_size_input.get(),
                                         self.is_private, pin=self.pin_input.get() if self.is_private else None)
            self.destroy()
        else:
            messagebox.showwarning("Ошибка ввода", "Заполните все поля")

    def check_visibility(self):
        self.is_password_visible = not self.is_password_visible
        if self.is_password_visible:
            self.pin_input.config(show="")
            self.visible_password_checkbox.configure(image=self.opened_eye)
        else:
            self.pin_input.config(show="*")
            self.visible_password_checkbox.configure(image=self.closed_eye)

    def change_is_private(self, ev):
        value = self.room_private_cfg.get()
        relheight = ALL_FIELDS_HEIGHT / FRAME_HEIGHT + 0.05
        self.is_private = True if value == "private" else False
        if self.is_private:
            self.pin_input.place(relx=0, rely=0.15 + relheight * 4, height=ALL_FIELDS_HEIGHT, relwidth=0.6, anchor="w")
            self.pin_lbl.place(relx=.5, rely=0.15 + relheight * 4, height=ALL_FIELDS_HEIGHT, anchor="center")
            self.visible_password_checkbox.place(relx=0.65, rely=0.11 + relheight * 4)
        else:
            self.pin_input.place_forget()
            self.pin_input.delete(0, 'end')
            self.pin_lbl.place_forget()
            self.visible_password_checkbox.place_forget()

    def start(self):
        relheight = ALL_FIELDS_HEIGHT / FRAME_HEIGHT + 0.05
        self.bg_frame.place(relx=.5, rely=.5, relwidth=0.75, relheight=0.75, anchor="center")
        # labels
        self.lbl_frame.place(relx=0, rely=.5, relwidth=0.5, relheight=1, anchor="w")
        self.room_name_lbl.place(relx=.5, rely=0.15, height=ALL_FIELDS_HEIGHT, anchor="center")
        self.room_size_lbl.place(relx=.5, rely=0.15 + relheight * 3, height=ALL_FIELDS_HEIGHT, anchor="center")
        self.room_private_lbl.place(relx=.5, rely=0.15 + relheight * 2, height=ALL_FIELDS_HEIGHT, anchor="center")
        self.mode_chooser_lbl.place(relx=.5, rely=0.15 + relheight, height=ALL_FIELDS_HEIGHT, anchor="center")

        # entries
        self.entry_frame.place(relx=1, rely=.5, relwidth=0.5, relheight=1, anchor="e")
        self.room_description_input.place(relx=0, rely=0.15, height=ALL_FIELDS_HEIGHT, relwidth=0.95, anchor="w")
        self.room_size_input.place(relx=0, rely=0.15 + relheight * 3, relwidth=0.25, height=ALL_FIELDS_HEIGHT,
                                   anchor="w")
        self.room_private_cfg.place(relx=0, rely=0.15 + relheight * 2, height=ALL_FIELDS_HEIGHT, relwidth=0.5,
                                    anchor="w")
        self.mode_chooser.place(relx=0, rely=0.15 + relheight, height=ALL_FIELDS_HEIGHT, relwidth=0.5, anchor="w")

        # confirm btn
        self.confirm_button.place(relx=.5, rely=0.85, height=35, anchor="center", relwidth=0.25)

    def on_closing(self):
        self.destroy()

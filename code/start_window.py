import os.path
import re
from PIL import Image, ImageTk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from tkinter import messagebox
from settings import *
from support import center, get_images_from_dir, is_valid
from random import shuffle
from player import Player
import socket
import pickle


class StartWindow(tk.Tk):
    def __init__(self, addr, player=None):
        super().__init__()
        # window
        self.title("Palack Paradise")
        self.geometry(f'{START_WIDTH}x{START_HEIGHT}')
        center(self)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        self.configure(background="#F47983", padx=0, pady=0)
        self.resizable(width=False, height=False)
        self.half_height = START_HEIGHT / 2
        self.half_width = START_WIDTH / 2
        self.player = player
        self.check_server_addr = addr
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        def return_pressed(ev):
            self.start_game()
        self.bind("<Return>", return_pressed)

        """
        Pre-load
        """
        self.avatars = list(get_images_from_dir('../graphics/avatars').items())
        self.current_avatar_index = 0
        self.next_img = ImageTk.PhotoImage(Image.open('../graphics/utility/next.png').
                                           resize((NEXT_ICO_SIZE, NEXT_ICO_SIZE)), master=self)
        shuffle(self.avatars)

        """
        Avatar stuff
        """
        # avatar picture
        self.current_PIL_avatar = self.avatars[0]
        self.current_avatar_image = ImageTk.PhotoImage(self.current_PIL_avatar[1], master=self)
        self.current_avatar = ttk.Label(self, image=self.current_avatar_image,
                                        borderwidth=BORDER, padding=(PADDING, PADDING))
        self.next_avatar = ttk.Button(self, image=self.next_img, command=self.change_avatar)

        """
        Other
        """
        # buttons
        # self.file_button = tk.Button(self, text="Выбрать файл", command=self.choose_image, font=(FONT_NAME, 10),
        #                              state="disabled")
        self.file_button = tk.Button(self, text="Выбрать файл", command=self.choose_image, font=(FONT_NAME, 10))
        # start game btn
        self.create_person_btn = tk.Button(self, font=(FONT_NAME, 12), text="Начать игру", command=self.start_game)

        """
        Nickname stuff
        """
        # nickname entry
        self.check = (self.register(is_valid), "%P")
        self.nickname_field = ttk.Entry(self, font=(FONT_NAME, 15), validate="key", validatecommand=self.check)
        self.nickname_lbl = ttk.Label(self, text="Введите ник", font=("Skellyman", 17), background="#F47983")

    """
    Binding
    """
    # image choosing
    def choose_image(self):
        image_file = filedialog.Open(filetypes=[('Image formats', '.jpg .png')]).show()
        if image_file:
            if os.path.getsize(image_file) < AVATAR_MAX_SIZE:
                image = Image.open(image_file).resize(PREFERRED_SIZE)
                real_name = os.path.basename(image_file)
                dest_dir = "../graphics/avatars/"
                dest_path = dest_dir + real_name
                if os.path.exists(dest_path):
                    ext = os.path.splitext(real_name)[1]
                    name = os.path.splitext(real_name)[0]
                    i = 1
                    while os.path.exists(dest_dir + real_name):
                        real_name = f"{name} ({i}){ext}"
                        i += 1
                dest_path = dest_dir + real_name
                self.current_PIL_avatar = (dest_path, image)
                self.current_PIL_avatar[1].save(dest_path)
                self.current_avatar_image = ImageTk.PhotoImage(self.current_PIL_avatar[1], master=self)
                self.current_avatar.configure(image=self.current_avatar_image)
            else:
                messagebox.showwarning("Некорректный файл", "Выбранный файл имеет слишком\n большой размер(> 4MB)")

    # taking next photo
    def change_avatar(self):
        if self.current_PIL_avatar not in self.avatars:
            os.remove(self.current_PIL_avatar[0])
        i = self.current_avatar_index + 1 if self.current_avatar_index + 1 < len(self.avatars) else 0
        self.current_avatar_index = i
        self.current_PIL_avatar = self.avatars[i]
        self.current_avatar_image = ImageTk.PhotoImage(self.current_PIL_avatar[1], master=self)
        self.current_avatar.configure(image=self.current_avatar_image)

    """
    Placing
    """
    # placing
    def placing_components(self):
        # avatar stuff
        self.current_avatar.place(x=self.half_width - 84, y=self.half_height - 250)
        self.file_button.place(x=self.half_width - 60, y=self.half_height - 68, width=125, height=25)
        self.next_avatar.place(x=self.half_width + 66, y=self.half_height - 100)

        # nickname stuff
        self.nickname_lbl.place(x=self.half_width - 69, y=self.half_height - 22)
        self.nickname_field.place(x=self.half_width - 90, y=self.half_height + 14, width=195, height=30)

        # create person btn
        self.create_person_btn.place(x=self.half_width - 75, y=self.half_height + 60, width=165, height=30)

    """
    Other stuff
    """
    def check_field_fill(self):
        if len(self.nickname_field.get()) > 3 and not re.match("[ \-_()*]+$", self.nickname_field.get()):
            if self.current_avatar:
                return True
        return False

    def get_created_player(self):
        return self.player

    def check_nickname_availability(self, nickname):
        check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            check_socket.connect(self.check_server_addr)
            check_socket.send(pickle.dumps(f"CHECKING_NICK\r\n{nickname}"))
            response = pickle.loads(check_socket.recv(1024))
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Server not started")
            return "error"
        except TimeoutError:
            messagebox.showerror("Error", "Wrong IP")
        finally:
            check_socket.close()

        if response:
            if response == "AVAILABLE":
                return "available"
            else:
                return "unavailable"

    """
    Start
    """
    # after clicking start btn
    def start_game(self):
        if self.check_field_fill():
            result = self.check_nickname_availability(self.nickname_field.get())
            if result == "available":
                # self.player = Player(self.nickname_field.get(), self.current_PIL_avatar[0])
                self.player = Player(self.nickname_field.get(), self.current_PIL_avatar)
                self.destroy()
            elif result == "unavailable":
                messagebox.showwarning("Nick warning", "Nickname is unavailable!")
        else:
            messagebox.showerror("Input error", "Nick should be 4-15 symbols")

    # start of this window
    def start(self):
        self.placing_components()

    def on_closing(self):
        if self.current_PIL_avatar not in self.avatars:
            os.remove(self.current_PIL_avatar[0])
        self.destroy()

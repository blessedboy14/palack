import tkinter as tk
import tkinter.ttk as ttk
from PIL import ImageTk
from settings import *
from tkinter import messagebox
from support import center
# from pygame import mixer
from create_window import CreateWindow
from room_window import RoomWindow
import pickle
from pin_input import PinInput


class HubWindow(tk.Tk):
    def __init__(self, player, window_conn):
        super().__init__()

        # window
        self.title("Palack Paradise")
        self.geometry(f'{WIDTH_HUB}x{HEIGHT_HUB}')
        center(self)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        self.resizable(width=False, height=False)
        self.configure(background=BG_COLOR, padx=PADDING, pady=PADDING)
        self.half_height = HEIGHT_HUB / 2
        self.half_width = WIDTH_HUB / 2
        self.player = player
        self.window_conn = window_conn
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        """
        Main Frame
        """
        s = ttk.Style()
        s.configure('My.TFrame', background=BG_FRAME_COLOR)
        self.frame = ttk.Frame(self, borderwidth=BORDER, style="My.TFrame", padding=(0, 0), border=0,
                               width=HUB_FRAME_WIDTH, height=HUB_FRAME_HEIGHT)
        self.table = ttk.Treeview(master=self.frame, selectmode="browse")
        self.table_init()

        """
        Player mini-profile
        """
        self.player_avatar_img = ImageTk.PhotoImage(self.player.get_avatar_image()[1], master=self.frame)
        self.player_avatar = ttk.Label(self.frame, image=self.player_avatar_img, borderwidth=BORDER,
                                       padding=(PADDING, PADDING))
        self.player_nick_lbl = ttk.Label(self.frame, text=self.player.get_nickname(), background=BG_FRAME_COLOR,
                                         font=(FONT_NAME, NICK_FONT_SIZE), justify="center")

        """
        Control buttons
        """
        self.refresh_list_btn = ttk.Button(self.frame, text="Обновить")
        self.join_room_btn = ttk.Button(self.frame, text="Присоединиться")
        self.create_room_btn = ttk.Button(self.frame, text="Создать комнату")

        """
        Table variables
        """
        self.is_empty = False
        self.room_list = []
        self.empty_room_notification = ttk.Label(self.table, text="Пока нет ни одной комнаты",
                                                 font=(FONT_NAME, NOTIFICATION_FONT_SIZE))

        """
        Refresh button personal
        """
        self.can_refresh = True
        # mixer.init()
        # self.forbid_btn_sound = mixer.Sound("../sounds/btn_forbid.mp3")
        # self.forbid_btn_sound.set_volume(0.2)

        """
        Some stuff
        """
        self.create_room_window = None
        self.in_new_window = False
        self.check_is_empty()
        self.binding()
        self.refresh_table_items(tk.Event())

    def table_init(self):
        self.table['columns'] = ('id', 'host', 'name', 'players', 'privacy')
        self.table.column("#0", width=0, stretch=tk.NO)
        self.table.column("id", anchor=tk.CENTER, width=int(TABLE_WIDTH / 10 / 2))
        self.table.column("host", anchor=tk.CENTER, width=int(2.3 * TABLE_WIDTH / 10))
        self.table.column("name", anchor=tk.CENTER, width=int(4.5 * TABLE_WIDTH / 10))
        self.table.column("players", anchor=tk.CENTER, width=int(1.3 * TABLE_WIDTH / 10))
        self.table.column("privacy", anchor=tk.CENTER, width=int(1.3 * TABLE_WIDTH / 10))
        self.table.heading("#0", text="", anchor=tk.CENTER)
        self.table.heading("id", text="Id", anchor=tk.CENTER)
        self.table.heading("host", text="Host", anchor=tk.CENTER)
        self.table.heading("name", text="Name", anchor=tk.CENTER)
        self.table.heading("players", text="Players", anchor=tk.CENTER)
        self.table.heading("privacy", text="Privacy", anchor=tk.CENTER)

    def inverse_refresh(self):
        self.can_refresh = not self.can_refresh

    def clean_table(self):
        for i in self.table.get_children():
            self.table.delete(i)

    def ask_server_list(self):
        self.window_conn.send(pickle.dumps(f"REFRESH\r\n{self.player.get_nickname()}"))
        data = b''
        while True:
            part = self.window_conn.recv(4096)
            data += part
            if len(part) < 4096:
                break
        room_list = pickle.loads(data)
        self.room_list = room_list

    def add_items(self):
        i = 1
        for room in self.room_list:
            self.table.insert(parent='', index='end', text='',
                              values=(i, room.get_host_name(), room.get_description(),
                                      f"{room.get_current()}/{room.get_size()}", "🔑" if room.is_private() else ""))
            i += 1

    def refresh_table_items(self, ev):
        if not self.in_new_window:
            if self.can_refresh or ev == "important":
                self.clean_table()
                self.ask_server_list()
                self.add_items()
                self.check_is_empty()
                self.can_refresh = False
                self.after(4000, self.inverse_refresh)
            else:
                pass# self.forbid_btn_sound.play()


    def send_server_verification(self, room):
        if room.is_private():
            pinWindow = PinInput()
            pinWindow.start()
            self.wait_window(pinWindow)
            input_pin = pinWindow.get_input_pin()
            if input_pin:
                message = f"CHECK_PIN\r\n{room.get_host_name()}"
                self.window_conn.send(pickle.dumps(message))
                self.window_conn.send(pickle.dumps(input_pin))
                response = pickle.loads(self.window_conn.recv(1024))
                if response == "INVALID":
                    messagebox.showerror("Ошибка пароля", "Введен неверный пароль")
                    return
            else:
                return
        message = "JOIN_ROOM\r\n"
        self.window_conn.send(pickle.dumps(message))
        self.window_conn.send(pickle.dumps(room.get_host_name()))
        self.window_conn.send(pickle.dumps(self.player))
        response = self.window_conn.recv(1024)
        if response == "ERROR":
            return False
        return True

    def join_to_room(self, ev):
        if not self.in_new_window:
            if self.table.selection():
                curItem = self.table.focus()
                index = int(self.table.item(curItem)['values'][0]) - 1
                room_to_join = self.room_list[index]
                if room_to_join.is_room_started():
                    messagebox.showwarning("Ошибка доступа", "Игра в комнате уже начата")
                    return
                if room_to_join.get_current() >= int(room_to_join.get_size()):
                    messagebox.showwarning("Ошибка доступа", "В комнату больше не влезет")
                    return
                if not self.send_server_verification(room_to_join):
                    return
                self.withdraw()
                room = RoomWindow(room_to_join, self.player, self.window_conn)
                room.start()
                self.wait_window(room)
                self.deiconify()
                self.refresh_table_items("important")

    def launching_room(self, created_room):
        created_room.set_host_player(self.player)
        created_room.add_player(self.player)
        self.window_conn.send(pickle.dumps(f"CREATE_ROOM\r\n"))
        self.window_conn.recv(1024)
        pickled = pickle.dumps(created_room)
        self.window_conn.sendall(len(pickled).to_bytes(4, byteorder='big'))
        self.window_conn.sendall(pickled)
        server_response = pickle.loads(self.window_conn.recv(1024))
        message, addr = server_response.split("\r\n")
        self.refresh_table_items("important")
        if message == "CREATED":
            self.withdraw()
            room = RoomWindow(created_room, self.player, self.window_conn)
            room.start()
            self.wait_window(room)
            self.deiconify()
            self.check_is_empty()
            self.refresh_table_items("important")

    def create_a_room(self, ev):
        if not self.in_new_window:
            if len(self.room_list) > 5:
                messagebox.showwarning("Can't create", "There is maximum of rooms already(6/6)")
                return
            self.create_room_window = CreateWindow()
            self.in_new_window = True
            self.create_room_window.start()
            self.wait_window(self.create_room_window)
            self.in_new_window = False
            created_room = self.create_room_window.get_created_room()
            if not created_room:
                return
            self.launching_room(created_room)

    def binding(self):
        self.refresh_list_btn.bind("<Button-1>", self.refresh_table_items)
        self.join_room_btn.bind("<Button-1>", self.join_to_room)
        self.table.bind('<Button-1>', self.handle_click)
        self.create_room_btn.bind("<Button-1>", self.create_a_room)

    # placing tkinter widgets
    def placing_components(self):
        self.frame.place(relx=.5, rely=.5, anchor="center")
        self.table.place(x=TABLE_LEFT, y=TABLE_TOP, width=TABLE_WIDTH, height=TABLE_HEIGHT)
        self.player_avatar.place(relx=0.04, rely=0.075)
        self.player_nick_lbl.configure(anchor="center")
        self.player_nick_lbl.place(relx=0.04, rely=0.53, width=PREFERRED_SIZE[0])
        self.join_room_btn.place(x=TABLE_LEFT, rely=0.075, width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.create_room_btn.place(x=TABLE_LEFT + BUTTON_WIDTH + OFFSET, rely=0.075,
                                   width=BUTTON_WIDTH, height=BUTTON_HEIGHT)
        self.refresh_list_btn.place(x=TABLE_LEFT + 2 * (BUTTON_WIDTH + OFFSET), rely=0.075, width=REFRESH_WIDTH,
                                    height=BUTTON_HEIGHT)

    def check_is_empty(self):
        if len(self.room_list) == 0:
            self.is_empty = True
            self.empty_room_notification.place(x=TABLE_WIDTH / 2 - 140, y=TABLE_HEIGHT / 2 - 20)
        else:
            self.is_empty = False
            self.empty_room_notification.place_forget()

    # binding
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.window_conn.send(pickle.dumps(f"DISCONNECT\r\n{self.player.get_nickname()}"))
            server_response = pickle.loads(self.window_conn.recv(1024))
            if server_response == "DELETED":
                self.window_conn.close()
                self.destroy()

    def handle_click(self, event):
        if self.table.identify_region(event.x, event.y) == "separator":
            return "break"

    # starting of window
    def start(self):
        self.placing_components()

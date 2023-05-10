import pickle
import tkinter as tk
from tkinter import ttk
from support import center
from settings import *
from PIL import ImageTk
from game_window import GameWindow


class RoomWindow(tk.Toplevel):
    def __init__(self, room, player, conn):
        super().__init__()

        # window
        self.title("Palack Paradise")
        self.geometry(f'{ROOM_WIDTH}x{ROOM_HEIGHT}')
        center(self)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        self.resizable(width=False, height=False)
        self.configure(background=ROOM_BG, padx=PADDING, pady=PADDING)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.half_height = HEIGHT_HUB / 2
        self.half_width = WIDTH_HUB / 2
        self.room = room
        self.player = player
        self.room_conn = conn
        self.is_started = False

        def return_pressed(ev):
            self.start_room_click()
        self.bind("<Return>", return_pressed)

        """
        GUI
        """
        s = ttk.Style(self)
        s.configure('Room.TFrame', background=ROOM_FRAME)
        s.configure('My.Treeview', rowheight=65, font=(FONT_NAME, 18), )
        s.map('My.Treeview', background=[('selected', '#B682A5')])
        self.frame = ttk.Frame(self, borderwidth=BORDER, padding=(PADDING, PADDING), style="Room.TFrame")
        self.players_view = ttk.Treeview(self.frame, selectmode="browse", show='tree', style="My.Treeview")
        self.current_players_lbl = ttk.Label(self.frame, font=(FONT_NAME, 15), background=ROOM_FRAME,
                                             text=f"Players {self.room.get_current()}/{self.room.get_size()}", )
        self.start_game_btn = tk.Button(self.frame, text="Начать игру", font=(FONT_NAME, 14),
                                        command=self.start_room_click)
        """
        Pre-start
        """
        self.players_avatars = {}
        self.table_init()
        self.refresh_player_list()
        self.check_room_status()

    def check_room_status(self):
        if not self.is_started and self.player.get_nickname() != self.room.get_host_name():
            message = f"CHECK_STATUS\r\n{self.room.get_host_player().get_nickname()}"
            self.room_conn.send(pickle.dumps(message))
            response = pickle.loads(self.room_conn.recv(1024))
            if response == "STARTED":
                self.is_started = True
                self.start_room()
            elif response == "DELETED":
                self.destroy()
        self.after(300, self.check_room_status)

    def clean_table(self):
        for i in self.players_view.get_children():
            self.players_view.delete(i)

    def notify_server_about_start(self):
        message = f"START_ROOM\r\n{self.room.get_host_player().get_nickname()}"
        self.room_conn.send(pickle.dumps(message))
        response = pickle.loads(self.room_conn.recv(1024))
        if response == "SUCCESS":
            print("Room started")

    def start_room(self):
        self.withdraw()
        game = GameWindow(self.room, self.player, self.room_conn)
        game.start()
        self.wait_window(game)
        self.is_started = False
        self.deiconify()

    def start_room_click(self):
        if self.player.get_nickname() == self.room.get_host_player().get_nickname():
            self.notify_server_about_start()
            self.is_started = True
            self.start_room()

    def table_init(self):
        self.players_view['columns'] = ('nickname', 'host')
        table_width = ROOM_WIDTH * 0.8 * 0.35
        self.players_view.column("#0", anchor=tk.CENTER, width=int(2 * table_width / 10))
        self.players_view.column("nickname", anchor=tk.CENTER, width=int(3.7 * table_width / 10))
        self.players_view.column("host", anchor=tk.CENTER, width=int(1 * table_width / 10))

    def add_items(self, player_list):
        for i, player in enumerate(player_list):
            self.players_avatars[player.get_nickname()] = ImageTk.PhotoImage(player.get_avatar_image()[1].
                                                                             resize(MINI_AVATAR_SIZE),
                                                                             master=self.frame)
            self.players_view.insert('', "end", text='', image=self.players_avatars[player.get_nickname()],
                                     values=(player_list[i].get_nickname(),
                                             ("👑" if self.room.get_host_player().get_nickname() ==
                                             player_list[i].get_nickname() else "")))
        self.current_players_lbl["text"] = f"Players {self.room.get_current()}/{self.room.get_size()}"

    def refresh(self):
        self.clean_table()
        self.add_items(self.room.get_player_list())

    def refresh_player_list(self):
        if not self.is_started:
            self.room_conn.send(pickle.dumps(f"REFRESH_ROOM\r\n{self.room.get_host_player().get_nickname()}"))
            data = b''
            while True:
                part = self.room_conn.recv(4096)
                data += part
                if len(part) < 4096:
                    break
            players = pickle.loads(data)
            if players != "NOT_FOUND":
                self.room.set_player_list(players)
                self.refresh()
        self.after(2000, self.refresh_player_list)

    def get_room(self):
        return self.room

    def placing(self):
        self.frame.place(relx=.5, rely=.5, relwidth=0.8, relheight=0.8, anchor="center")
        self.players_view.place(relx=0.05, rely=0.1, relwidth=0.30, relheight=0.80)
        self.current_players_lbl.place(relx=0.2, rely=0.07, anchor="center")
        if self.player.get_nickname() == self.room.get_host_name():
            self.start_game_btn.place(relx=0.6, rely=0.15, relheight=0.1, relwidth=0.15, anchor="center")

    def start(self):
        self.placing()

    def on_closing(self):
        if self.player.get_nickname() == self.room.get_host_name():
            self.room_conn.send(pickle.dumps(f"DELETE_ROOM\r\n{self.player.get_nickname()}"))
            self.destroy()

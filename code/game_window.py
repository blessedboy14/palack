import pickle

from PIL import ImageTk, Image

from support import is_prompt_valid
import tkinter as tk
from tkinter import ttk, messagebox
from support import center
from settings import *
from Timer import Timer
from Paint import Paint


class GameWindow(tk.Toplevel):
    def __init__(self, room, player, conn):
        super().__init__()

        # window
        self.player = player
        self.title(f"Palack Paradise({self.player.get_nickname()})")
        self.geometry(f'{ROOM_WIDTH}x{ROOM_HEIGHT}')
        center(self)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        self.resizable(width=False, height=False)
        self.configure(background=ROOM_BG, padx=PADDING, pady=PADDING)
        self.half_height = HEIGHT_HUB / 2
        self.half_width = WIDTH_HUB / 2
        self.room = room
        self.room_conn = conn
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        """GUI"""
        s = ttk.Style(self)
        s.configure('Game.TFrame', background=ROOM_FRAME)
        self.frame = ttk.Frame(self, borderwidth=BORDER, padding=(PADDING, PADDING), style="Game.TFrame")
        self.check = (self.register(is_prompt_valid), "%P")
        self.prompt_input = ttk.Entry(self.frame, font=(FONT_NAME, 18), validate="key", validatecommand=self.check)
        self.prompt_lbl = ttk.Label(self.frame, text="Напиши предложение", background=ROOM_FRAME, font=(FONT_NAME, 18))
        self.ready_btn = tk.Button(self.frame, text="Готово", font=(FONT_NAME, 14), command=self.on_ready_click)
        self.is_ready = False
        self.timer = None
        self.paint = Paint(self.frame)
        self.paint.place_forget_paint()
        self.room_stages = 0
        self.current_stage = 0
        self.prompt_time = START_PROMPT_TIME
        self.canvas_time = START_CANVAS_TIME

        self.result_canvas = tk.Canvas(self.frame, bg='#f2bcef', width=200, height=300)
        self.canvas_scroll = ttk.Scrollbar(self.frame, orient=tk.VERTICAL)
        self.players = {}
        self.temp_photos = []

        self.left_swipe_img = ImageTk.PhotoImage(Image.open('../graphics/utility/left_swipe.png').
                                                 resize((NEXT_ICO_SIZE, NEXT_ICO_SIZE)), master=self)
        self.right_swipe_img = ImageTk.PhotoImage(Image.open('../graphics/utility/right_swipe.png').
                                                  resize((NEXT_ICO_SIZE, NEXT_ICO_SIZE)), master=self)
        self.left_swipe_btn = tk.Button(self.frame, image=self.left_swipe_img, command=self.left_swipe)
        self.right_swipe_btn = tk.Button(self.frame, image=self.right_swipe_img, command=self.right_swipe)

        self.curr_page = 0
        self.result_game_data = None
        self.mode = None
        """
        Pre-start
        """
        self.check_room_status()

    def left_swipe(self):
        if self.curr_page > 0:
            self.curr_page -= 1
            self.generate_result(self.result_game_data, self.curr_page)

    def right_swipe(self):
        if self.curr_page < self.room.get_current() - 1:
            self.curr_page += 1
            self.generate_result(self.result_game_data, self.curr_page)

    def _generate_avatars_dict(self):
        for player in self.room.get_player_list():
            self.players[player.get_nickname()] = ImageTk.PhotoImage(player.get_avatar_image()[1].
                                                                     resize(AVATAR_SIZE),
                                                                     master=self.frame)

    def on_ready_click(self):
        if self.mode == "prompt":
            if self.is_ready:
                self.prompt_input.state(['!disabled'])
                self.ready_btn['text'] = "Готово"
                self.is_ready = False
            else:
                self.is_ready = True
                self.prompt_input.state(['disabled'])
                self.ready_btn['text'] = "Изменить"
        else:
            if self.is_ready:
                self.paint.unsleep_canvas()
                self.ready_btn['text'] = "Готово"
                self.is_ready = False
            else:
                self.is_ready = True
                self.paint.sleep_canvas()
                self.prompt_input.state(['disabled'])
                self.ready_btn['text'] = "Изменить"

    def on_closing(self):
        if self.player.get_nickname() == self.room.get_host_name():
            if messagebox.askokcancel("Quit", "Do you want to quit?"):
                self.room_conn.send(pickle.dumps(f"STOP_GAME\r\n{self.player.get_nickname()}"))
                server_response = pickle.loads(self.room_conn.recv(1024))
                if server_response == "CLOSED":
                    self.destroy()

    def check_room_status(self):
        if self.player.get_nickname() != self.room.get_host_name():
            message = f"CHECK_STATUS\r\n{self.room.get_host_name()}"
            self.room_conn.send(pickle.dumps(message))
            response = pickle.loads(self.room_conn.recv(1024))
            if response == "CLOSED":
                self.destroy()
        self.after(200, self.check_room_status)

    def after_timer(self, message, mode):
        self.ready_btn['text'] = "Готово"
        self.prompt_input.state(['!disabled'])
        if mode == "prompt":
            self.prompt_call(message)
        elif mode == "canvas":
            self.paint_call(message)

    def ask_next_part(self, mode):
        message = f"ASK_NEXT\r\n{self.room.get_host_name()},{self.player.get_nickname()},{self.current_stage}"
        self.room_conn.send(pickle.dumps(message))
        data = b''
        while True:
            part = self.room_conn.recv(4096)
            data += part
            if len(part) < 4096:
                break
        data = pickle.loads(data)
        if mode == "prompt":
            self.prompt_input.state(['!disabled'])
            self.prompt_input.delete("0", tk.END)
            self.prompt_input.insert("0", data)
            self.prompt_input.state(['disabled'])
        elif mode == "canvas":
            self.prompt_input.delete("0", tk.END)
            self.paint.set_canvas_image(data)

    def receive_game_results(self):
        message = f"SEND_GAME_RESULT\r\n{self.room.get_host_name()}"
        self.room_conn.send(pickle.dumps(message))
        data = b''
        while True:
            part = self.room_conn.recv(4096)
            data += part
            if len(part) < 4096:
                break
        data = pickle.loads(data)
        return data

    def is_solo_player(self, data):
        for key in data.keys():
            return len(data[key][0]) < 2

    def _result_canvas_config(self, scrollregion):
        self.canvas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_scroll.config(command=self.result_canvas.yview)
        self.result_canvas.config(width=300, height=300)
        self.result_canvas.config(scrollregion=scrollregion)
        self.result_canvas.config(yscrollcommand=self.canvas_scroll.set)
        self.result_canvas.place(relx=0.05, rely=0.15, relheight=0.8, relwidth=0.9)

    def _clear_result_canvas(self):
        self.result_canvas.delete('all')
        self.result_canvas['bg'] = '#f2bcef'

    def _place_mini_avatar(self, side, offset_y, nick):
        nick = nick
        if side == tk.RIGHT:
            self.result_canvas.create_image(LEFT_AVATAR_X, offset_y, image=self.players[nick])
            self.result_canvas.create_text(LEFT_AVATAR_X, offset_y + MINI_AVATAR_SIZE[0] - 5, anchor="center",
                                           text=nick, font=BASE_FONT)
        elif side == tk.LEFT:
            self.result_canvas.create_image(RIGHT_AVATAR_X, offset_y, image=self.players[nick])
            self.result_canvas.create_text(RIGHT_AVATAR_X, offset_y + MINI_AVATAR_SIZE[0] - 5, anchor="center",
                                           text=nick, font=BASE_FONT)

    def _find_nick_by_stage(self, stage, game_data, nick):
        for key in game_data.keys():
            if game_data[key][0][stage] == nick:
                return key

    def generate_result(self, game_data, index):
        key = list(game_data.keys())[index]
        mini_storage = game_data[key]
        self._clear_result_canvas()
        sides = [tk.RIGHT, tk.LEFT]
        offset = BASE_OFFSET_Y
        i = 0
        length = len(mini_storage[0])
        data_index = index + 1
        data_key = list(game_data.keys())[data_index % length]
        data_storage = game_data[data_key]
        while i < length:
            nick = mini_storage[0][i]
            self._place_mini_avatar(sides[i % 2], offset, nick)
            data = data_storage[1][i]
            if i % 2 == 0:
                self.text_item = self.result_canvas.create_text(0, 0, text=data, font=(FONT_NAME, 12))
                bounds = self.result_canvas.bbox(self.text_item)
                text_width = bounds[2] - bounds[0]
                x = (LEFT_AVATAR_X - text_width - 20)
                self.result_canvas.create_text(x, offset + MINI_AVATAR_SIZE[0]/4 - 15,
                                               text=data, font=(FONT_NAME, 12))
                self.result_canvas.delete(self.text_item)
                offset += AVATAR_SIZE[0] + 25
            else:
                self.temp_photos.append(ImageTk.PhotoImage(data.resize(CANVAS_IMG_SIZE), master=self.result_canvas))
                self.result_canvas.create_image(RIGHT_AVATAR_X + MINI_AVATAR_SIZE[0], offset, anchor="nw",
                                                image=self.temp_photos[-1])
                offset += AVATAR_SIZE[0] + 200
            i += 1
            data_index += 2
            data_key = list(game_data.keys())[data_index % length]
            data_storage = game_data[data_key]

    def print_data_on_screen(self, game_data):
        self._generate_avatars_dict()
        self.left_swipe_btn.place(relx=0.9, rely=0.957)
        self.right_swipe_btn.place(relx=0.935, rely=0.957)
        keys = list(game_data.keys())
        scroll_x, scroll_y = len(game_data[keys[0]][1])*240, len(game_data[keys[0]][1])*240
        self._result_canvas_config((0, 0, scroll_x, scroll_y))
        self.generate_result(game_data, self.curr_page)

    def call_end(self):
        self.prompt_lbl['text'] = 'Результаты'
        self.paint.place_forget_paint()
        self.prompt_input.place_forget()
        self.ready_btn.place_forget()
        game_data = self.receive_game_results()
        self.result_game_data = game_data
        if not self.is_solo_player(game_data):
            self.print_data_on_screen(game_data)

    def _find_next_in_list(self, player_list):
        for player in player_list:
            if player.get_nickname() == self.player.get_nickname():
                return player_list.index(player) + self.current_stage

    def prompt_call(self, message):
        player_list = self.room.get_player_list()
        name = player_list[self._find_next_in_list(player_list) % len(player_list)].get_nickname()
        message = message if len(message) > 0 else "no prompt input"
        self.room_conn.send(pickle.dumps(f"PROMPT\r\n{self.room.get_host_name()},{name}"))
        response = pickle.loads(self.room_conn.recv(1024))
        if response == "FOUND":
            self.room_conn.send(pickle.dumps(f"{message}"))
            pickle.loads(self.room_conn.recv(1024))
            self.prompt_lbl['text'] = "Зарисуй предложение"
            if self.current_stage >= self.room_stages:
                self.after(200)
                self.call_end()
            else:
                self.after(300)
                self.is_ready = False
                self.mode = "canvas"
                self.ask_next_part("prompt")
                self.paint.place_paint()
                self.paint.unsleep_canvas()
                self.timer = Timer(self, self.canvas_time-3.2*self.current_stage, "canvas")
                self.timer.start_timer()
                self.current_stage += 1

    def paint_call(self, message):
        player_list = self.room.get_player_list()
        name = player_list[self._find_next_in_list(player_list) % len(player_list)].get_nickname()
        self.room_conn.send(pickle.dumps(f"CANVAS\r\n{self.room.get_host_name()},{name}"))
        response = pickle.loads(self.room_conn.recv(1024))
        if response == "FOUND":
            message_pickled = pickle.dumps(message)
            self.room_conn.send(message_pickled)
            pickle.loads(self.room_conn.recv(1024))
            self.prompt_lbl['text'] = "Опиши картинку"
            if self.current_stage >= self.room_stages:
                self.after(200)
                self.call_end()
            else:
                self.after(300)
                self.is_ready = False
                self.mode = "prompt"
                self.ask_next_part("canvas")
                self.paint.sleep_canvas()
                self.timer = Timer(self, self.prompt_time-2.5*self.current_stage, "prompt")
                self.timer.start_timer()
                self.current_stage += 1

    def start_game(self):
        self.timer = Timer(self, self.prompt_time, "prompt")
        self.timer.start_timer()
        self.mode = "prompt"
        self.current_stage += 1

    def placing(self):
        self.frame.place(relx=.5, rely=.5, relwidth=0.8, relheight=0.8, anchor="center")
        self.prompt_lbl.place(relx=.5, rely=0.05, anchor="center")
        self.prompt_input.place(relx=0.05, rely=0.10, relwidth=0.79, height=30)
        self.ready_btn.place(relx=0.915, rely=0.128, height=30, relwidth=0.135, anchor="center")

    def wait_for_start(self):
        message = f"ASK_START\r\n{self.room.get_host_name()}"
        self.room_conn.send(pickle.dumps(message))
        response = pickle.loads(self.room_conn.recv(1024))
        if response == "START":
            self.start_game()

    def start(self):
        self.placing()
        self.room_stages = self.room.get_current()
        self.current_stage = 0
        self.wait_for_start()

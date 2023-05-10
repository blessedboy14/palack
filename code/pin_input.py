from tkinter import ttk
import tkinter as tk
from support import is_pin_valid, center
from settings import *


class PinInput(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.title("Palack Paradise")
        self.geometry(f'{PIN_WIDTH}x{PIN_HEIGHT}')
        self.resizable(width=False, height=False)
        self.iconbitmap('../graphics/icons/main_ico.ico')
        self.attributes("-toolwindow", True)
        center(self)

        self.check = (self.register(is_pin_valid), "%P")
        self.pin_input = ttk.Entry(self, validate="key", validatecommand=self.check, font=BASE_FONT)
        self.confirm_btn = tk.Button(self, text="Подтвердить", command=self.submit_password, font=BASE_FONT)
        self.password = None

    def submit_password(self):
        if len(self.pin_input.get()) > 0:
            self.password = self.pin_input.get()
            self.destroy()

    def start(self):
        self.pin_input.pack(pady=5)
        self.confirm_btn.pack(pady=10)

    def get_input_pin(self):
        return self.password

from tkinter import ttk
from threading import Thread


class Timer:
    def __init__(self, master, time_ms, mode):
        self.master = master
        self.time = 0
        self.time_ms = time_ms
        self.mode = mode
        if mode == "prompt":
            master.prompt_input.state(['!disabled'])
        else:
            master.paint.canvas.configure(state="normal")
        self.is_timer_end = False
        self.progressbar = ttk.Progressbar(self.master, orient="horizontal", length=200, mode="determinate")
        self.progressbar.pack(pady=10)

    def start_timer(self):
        self.progressbar["maximum"] = self.time_ms * 10
        self.time += 1
        self.progressbar["value"] = self.time * 2
        if self.time < self.time_ms * 2 * 2.5:
            self.master.after(200, self.start_timer)
        elif self.time == self.time_ms * 2 * 2.5:
            self.is_timer_end = True
            self.callback(self.master)

    def callback(self, master):
        result = None
        self.progressbar.pack_forget()
        if self.mode == "prompt":
            master.prompt_input.state(['disabled'])
            result = master.prompt_input.get()
        elif self.mode == "canvas":
            master.paint.canvas.configure(state="disabled")
            result = master.paint.capture_img()
        master.after_timer(result, self.mode)

    # def wait_for_end(self):
    #     t = Thread(target=self.await_func)
    #     t.start()
    #
    # def await_func(self):
    #     while not self.is_timer_end:
    #         pass

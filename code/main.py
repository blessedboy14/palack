from start_window import StartWindow
from hub_window import HubWindow


class Application:
    def __init__(self):
        self.start_window = StartWindow()
        self.hub_window = None
        self.curr_player = None

    def start_program(self):
        self.start_window.start()
        self.start_window.mainloop()
        self.curr_player = self.start_window.get_created_player()
        self.handle_hub()

    def handle_hub(self):
        self.hub_window = HubWindow(self.curr_player)
        self.hub_window.start()
        self.hub_window.mainloop()


if __name__ == "__main__":
    my_application = Application()
    my_application.start_program()

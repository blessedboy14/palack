from start_window import StartWindow
from hub_window import HubWindow
import socket
import pickle


class Client:
    def __init__(self):
        self.server_ip = '192.168.1.101'
        self.server_port = 5050
        self.server_addr = (self.server_ip, self.server_port)
        self.start_window = StartWindow(self.server_addr)
        self.hub_window = None
        self.curr_player = None
        self.socket = None
        self.encoding_format = 'utf-8'

    def start_program(self):
        self.start_window.start()
        self.start_window.mainloop()
        self.curr_player = self.start_window.get_created_player()
        if self.curr_player:
            self.handle_hub()

    def handle_hub(self):
        self.connection_to_server()
        self.hub_window = HubWindow(self.curr_player, self.socket)
        self.hub_window.start()
        self.hub_window.mainloop()

    def send_welcome_message(self, conn):
        message = "HELLO\r\n" + self.curr_player.get_nickname()
        conn.send(pickle.dumps(message))

    def connection_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_ip, self.server_port))
        self.send_welcome_message(self.socket)


myClient = Client()
myClient.start_program()

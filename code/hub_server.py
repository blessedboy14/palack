import random
import time
import socket
from support import get_ip
import threading
import pickle


class HubServer:
    def __init__(self):
        # net data
        PORT = 5050
        self.IP = get_ip()
        self.header = 64
        self.encode_format = "utf-8"
        self.ADDR = (self.IP, PORT)

        self.used_ports = []
        self.room_port_range = [50000, 60000]

        # server binding
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)

        self.active_rooms = []
        self.local_storage = {}
        self.player_nicks = []

    def _make_player_structure(self, room):
        room_size = room.get_current()
        player_list = room.get_player_list()
        info_list = {player.get_nickname(): [] for player in player_list}
        for j in range(room_size):
            nicks = []
            info = []
            for i in range(room_size):
                nicks.append(player_list[(i + j) % room_size].get_nickname())
                info.append(None)
            info_list[player_list[j].get_nickname()].append(nicks)
            info_list[player_list[j].get_nickname()].append(info)
        self.local_storage[room.get_host_name()] = info_list

    def _calculate_game_stage(self, host):
        room_storage = self.local_storage[host]
        keys = list(room_storage.keys())
        stages = []
        for key in keys:
            mini_storage = room_storage[key][1]
            stage = 0
            for i in range(len(mini_storage)):
                if mini_storage[i] is not None:
                    stage += 1
                else:
                    stages.append(stage)
        return min(stages) if len(stages) > 0 else 0

    def _check_stage_complete(self, room, stage):
        storage = self.local_storage[room.get_host_name()]
        for key in storage.keys():
            if storage[key][1][stage] is None:
                return False
        return True

    def _insert_into_storage(self, room, player_name, prompt):
        stage = self._calculate_game_stage(room.get_host_name())
        print(stage, "  ", player_name)
        room_storage = self.local_storage[room.get_host_name()]
        try:
            room_storage[player_name][1][stage] = prompt
        except IndexError:
            pass
        finally:
            return stage

    def handle_client(self, conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        connected = True
        while connected:
            msg = pickle.loads(conn.recv(1024))
            if "\r\n" in msg:
                command, message = msg.split("\r\n")
                if command != "CHECK_STATUS":
                    print(f"[{addr}] {command} {message}")
                connected = self.manage_messages(command, message, conn)
            else:
                conn.send(pickle.dumps("WRONG_COMMAND"))
        conn.close()

    def manage_messages(self, command, message, conn):
        match command:
            case "CHECKING_NICK":
                self.find_nick_in_base(message, conn)
                return False
            case "HELLO":
                self.adding_a_new_player(message)
                return True
            case "DISCONNECT":
                self.delete_a_player(message, conn)
                return False
            case "REFRESH":
                self.send_current_list(conn)
                return True
            case "CREATE_ROOM":
                self.create_a_room(conn)
                return True
            case "DELETE_ROOM":
                self.delete_a_room(message)
                return True
            case "REFRESH_ROOM":
                self.send_players_room(message, conn)
                return True
            case "JOIN_ROOM":
                self.join_player_to_room(conn)
                return True
            case "CHECK_STATUS":
                self.send_room_status(message, conn)
                return True
            case "START_ROOM":
                self.start_a_room(message, conn)
                return True
            case "ASK_START":
                self.synchronize_all_room(message, conn)
                return True
            case "STOP_GAME":
                self.close_a_game(message, conn)
                return True
            case "PROMPT":
                self.receive_prompt(message, conn)
                return True
            case "CANVAS":
                self.receive_canvas(message, conn)
                return True
            case "ASK_NEXT":
                self.send_next_game_data(message, conn)
                return True
            case "CHECK_PIN":
                self.check_room_pin(message, conn)
                return True
            case "SEND_GAME_RESULT":
                self.send_local_storage(message, conn)
                return True

    def send_local_storage(self, message, conn):
        for room in self.active_rooms:
            if room.get_host_name() == message:
                conn.send(pickle.dumps(self.local_storage[message]))

    def check_room_pin(self, message, conn):
        pin = pickle.loads(conn.recv(1024))
        for room in self.active_rooms:
            if message == room.get_host_name():
                if room.check_pin(pin):
                    conn.send(pickle.dumps("VALID"))
                else:
                    conn.send(pickle.dumps("INVALID"))

    def _find_data_in_storage(self, host, player, stage):
        room_storage = self.local_storage[host]
        keys = list(room_storage.keys())
        player = keys[(keys.index(player) + stage) % len(keys)]
        return room_storage[player][1][stage]

    def send_next_game_data(self, message, conn):
        message = message.split(",")
        data = self._find_data_in_storage(message[0], message[1], int(message[2])-1)
        conn.send(pickle.dumps(data))

    def receive_canvas(self, message, conn):
        message, name = message.split(",")
        for room in self.active_rooms:
            if message == room.get_host_name():
                conn.send(pickle.dumps("FOUND"))
                data = b''
                while True:
                    part = conn.recv(4096)
                    data += part
                    if len(part) < 4096:
                        break
                canvas = pickle.loads(data)
                self._insert_into_storage(room, name, canvas)
                conn.send(pickle.dumps("ADDED"))

    def receive_prompt(self, message, conn):
        message, name = message.split(",")
        for room in self.active_rooms:
            if message == room.get_host_name():
                conn.send(pickle.dumps("FOUND"))
                prompt = pickle.loads(conn.recv(1024))
                self._insert_into_storage(room, name, prompt)
                conn.send(pickle.dumps("ADDED"))

    def close_a_game(self, message, conn):
        for room in self.active_rooms:
            if message == room.get_host_name():
                room.stop_room()
                self.local_storage[room.get_host_name()] = None
                conn.send(pickle.dumps("CLOSED"))

    def synchronize_all_room(self, message, conn):
        for room in self.active_rooms:
            if message == room.get_host_name():
                start_time = room.get_start_time()
                time.sleep(start_time + 0.75 - time.time())
                conn.send(pickle.dumps("START"))

    def start_a_room(self, message, conn):
        for room in self.active_rooms:
            if message == room.get_host_name():
                room.start_room()
                room.set_start_time(time.time())
                self._make_player_structure(room)
                conn.send(pickle.dumps(f"SUCCESS\r\n{room.get_current()}"))

    def send_room_status(self, message, conn):
        isFound = False
        for room in self.active_rooms:
            if message == room.get_host_name():
                isFound = True
                result = "STARTED" if room.is_room_started() else "CLOSED"
                conn.send(pickle.dumps(result))
        if not isFound:
            conn.send(pickle.dumps("DELETED"))

    def join_player_to_room(self, conn):
        host = pickle.loads(conn.recv(1024))
        data = b''
        while True:
            part = conn.recv(4096)
            data += part
            if len(part) < 4096:
                break
        player = pickle.loads(data)
        for room in self.active_rooms:
            if host == room.get_host_name():
                room.add_player(player)
                conn.send(pickle.dumps("SUCCESS"))
                return
        conn.send(pickle.dumps("ERROR"))

    def delete_a_room(self, message):
        if len(self.active_rooms) == 0:
            print("ERROR IT CANNOT BE")
        removed = False
        for room in self.active_rooms:
            if room.host_player.get_nickname() == message:
                self.active_rooms.remove(room)
                removed = True
        if not removed:
            print("ERROR IT CANNOT BE")

    def send_players_room(self, message, conn):
        for room in self.active_rooms:
            if message == room.get_host_player().get_nickname():
                conn.send(pickle.dumps(room.get_player_list()))
                return
        conn.send(pickle.dumps("NOT_FOUND"))

    def _check_uniqueness(self, message):
        return not (message in self.active_rooms)

    def create_a_room(self, conn):
        conn.send(pickle.dumps("ACCEPTED"))
        size = int.from_bytes(conn.recv(2048), byteorder="big")
        data = b''
        while len(data) < size:
            data += conn.recv(4096)
        room = pickle.loads(data)
        if self._check_uniqueness(room):
            room_port = random.randint(self.room_port_range[0], self.room_port_range[1])
            while room_port in self.used_ports:
                room_port = random.randint(self.room_port_range[0], self.room_port_range[1])
            self.used_ports.append(room_port)
            room_address = (self.IP, room_port)
            room.set_address(room_address)
            self.active_rooms.append(room)
            conn.send(pickle.dumps(f"CREATED\r\n{room_address}"))
        else:
            conn.send(pickle.dumps("EXISTS"))

    def send_current_list(self, conn):
        conn.send(pickle.dumps(self.active_rooms))

    def adding_a_new_player(self, message):
        self.player_nicks.append(message)

    def delete_a_player(self, message, conn):
        if message in self.player_nicks:
            self.player_nicks.remove(message)
            conn.send(pickle.dumps("DELETED"))
        else:
            conn.send(pickle.dumps("NOT_FOUND"))

    def find_nick_in_base(self, nick, conn):
        if nick in self.player_nicks:
            response = "UNAVAILABLE"
        else:
            response = "AVAILABLE"
        conn.send(pickle.dumps(response))

    def start(self):
        self.server.listen()
        print(f'curr_ip={self.IP}')
        print("[LISTENING]")
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


hubServer = HubServer()
hubServer.start()

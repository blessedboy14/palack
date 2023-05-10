class GameRoom:
    def __init__(self, host, address, description, capacity, is_private=False, mode="default", pin=None):
        self.host_player = host
        self.capacity = capacity
        self.address = address
        self.room_description = description
        self.room_mode = mode
        self.room_pin = pin
        self.is_room_private = is_private
        self.player_list = []
        self.is_started = False
        self.start_time = None

    def start_room(self):
        self.is_started = True

    def set_start_time(self, start_time):
        self.start_time = start_time

    def get_start_time(self):
        return self.start_time

    def stop_room(self):
        self.is_started = False

    def is_room_started(self):
        return self.is_started

    def get_player_list(self):
        return self.player_list

    def set_player_list(self, player_list):
        self.player_list = player_list

    def get_address(self):
        return self.address

    def set_address(self, addr):
        self.address = addr

    def set_host_player(self, player):
        self.host_player = player

    def get_host_player(self):
        return self.host_player

    def get_description(self):
        return self.room_description

    def get_size(self):
        return self.capacity

    def get_current(self):
        return len(self.player_list)

    def get_host_name(self):
        return self.host_player.get_nickname()

    def add_player(self, player):
        if player not in self.player_list:
            self.player_list.append(player)

    def is_private(self):
        return self.is_room_private

    def check_pin(self, pin):
        return pin == self.room_pin

    def __repr__(self):
        return f"[ROOM] {self.room_description}; [HOST] {self.host_player.get_nickname()}; size: {self.capacity};" \
               f"privacy: " + ("private;" if self.is_room_private else "public;") + "\n"

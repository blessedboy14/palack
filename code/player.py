class Player:
    def __init__(self, nickname, avatar_image):
        self.nickname = nickname
        self.avatar_image = avatar_image

    def get_nickname(self):
        return self.nickname

    def get_avatar_image(self):
        return self.avatar_image

    def __repr__(self):
        return f"[PLAYER]{self.nickname}[PHOTO]{self.avatar_image[0]}, {self.avatar_image[1]}\n"

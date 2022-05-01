import uuid
from chess.game.enums import ColorEnum

class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.id = str(uuid.uuid4())

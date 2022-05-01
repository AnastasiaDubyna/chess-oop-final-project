from chess.game.enums import PieceEnum, ColorEnum

class Spot:

    def __init__(self, x, y, piece = None):
        self.x = x
        self.y = y
        self.piece = piece
    
    def is_empty(self):
        if self.piece:
            return False
        return True

    def get_piece(self):
        return self.piece 
    
    def set_piece(self, piece):
        self.piece = piece
    
    def remove_piece(self):
        self.piece = None

    def get_piece_name(self):
        if self.is_empty():
            return None
        return self.piece.name

    def get_piece_color(self):
        if self.is_empty():
            return None
        elif self.get_piece().is_white():
            return ColorEnum.WHITE
        else: return ColorEnum.BLACK




    
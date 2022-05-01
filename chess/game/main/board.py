from chess.game.main.spot import Spot
from chess.game.main.piece import King, Queen, Rook, Pawn, Bishop, Knight

class Board:
    boxes = [[Spot(j, i) for i in range(8)] for j in range(8)]
    version = 0
    patch = None

    def __init__(self):
        self.reset_board()

    def get_box(self, x, y):
        if x < 0 or x > 7 or y < 0 or y > 7:
            raise ValueError("invalid spot")
        patch_key = '{x}{y}'.format(x = x, y = y)
        if (self.patch != None and patch_key in self.patch):
            return self.patch[patch_key];
        return self.boxes[x][y]


    def add_patch(self, start, end, piece):
        start_key = '{x}{y}'.format(x = start['x'], y = start['y'])
        end_key = '{x}{y}'.format(x = end['x'], y = end['y'])
        self.patch = {
            start_key: Spot(start['x'], start['y']),
            end_key: Spot(end['x'], end['y'], piece)
        }

    def clear_patch(self):
        self.patch = None

    def reset_board(self):
        self.boxes[0][0] = Spot(0, 0, Rook(True))
        self.boxes[0][1] = Spot(0, 1, Knight(True))
        self.boxes[0][2] = Spot(0, 2, Bishop(True))
        self.boxes[0][3] = Spot(0, 3, Queen(True))
        self.boxes[0][4] = Spot(0, 4, King(True))
        self.boxes[0][5] = Spot(0, 5, Bishop(True))
        self.boxes[0][6] = Spot(0, 6, Knight(True))
        self.boxes[0][7] = Spot(0, 7, Rook(True))

        self.boxes[1][0] = Spot(1, 0, Pawn(True))
        self.boxes[1][1] = Spot(1, 1, Pawn(True))
        self.boxes[1][2] = Spot(1, 2, Pawn(True))
        self.boxes[1][3] = Spot(1, 3, Pawn(True))
        self.boxes[1][4] = Spot(1, 4, Pawn(True))
        self.boxes[1][5] = Spot(1, 5, Pawn(True))
        self.boxes[1][6] = Spot(1, 6, Pawn(True))
        self.boxes[1][7] = Spot(1, 7, Pawn(True))

        self.boxes[7][0] = Spot(7, 0, Rook(False))
        self.boxes[7][1] = Spot(7, 1, Knight(False))
        self.boxes[7][2] = Spot(7, 2, Bishop(False))
        self.boxes[7][3] = Spot(7, 3, Queen(False))
        self.boxes[7][4] = Spot(7, 4, King(False))
        self.boxes[7][5] = Spot(7, 5, Bishop(False))
        self.boxes[7][6] = Spot(7, 6, Knight(False))
        self.boxes[7][7] = Spot(7, 7, Rook(False))

        self.boxes[6][0] = Spot(6, 0, Pawn(False))
        self.boxes[6][1] = Spot(6, 1, Pawn(False))
        self.boxes[6][2] = Spot(6, 2, Pawn(False))
        self.boxes[6][3] = Spot(6, 3, Pawn(False))
        self.boxes[6][4] = Spot(6, 4, Pawn(False))
        self.boxes[6][5] = Spot(6, 5, Pawn(False))
        self.boxes[6][6] = Spot(6, 6, Pawn(False))
        self.boxes[6][7] = Spot(6, 7, Pawn(False))

    def increment_version(self):
        self.version += 1

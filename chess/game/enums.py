from enum import Enum

class PieceEnum(str, Enum):
     QUEEN = 'I',
     KING = 'H',
     PAWN = 'G',
     ROOK = 'K',
     BISHOP = 'J',
     KNIGHT = 'L'

class ColorEnum(str, Enum):
     WHITE = 'white', 
     BLACK = 'black'
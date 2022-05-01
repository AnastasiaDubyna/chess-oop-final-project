from abc import ABC, abstractmethod
from math import fabs
from chess.game.enums import PieceEnum

class Piece(ABC):
    killed = False
    white = False

    def __init__(self, is_white):
        self.white = is_white
    
    def is_white(self):
        return self.white 
    
    def is_killed(self):
        return self.killed
    
    @abstractmethod
    def is_move_correct(self):
        pass

class King(Piece):
    name = PieceEnum.KING

    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        king = self
        king_color = king.is_white()
        end_spot = move.curr_board.get_box(end_x, end_y)

        if not self.is_king_safe(end_x, end_y, move):
            return False
        
        if (start_x + start_y == end_x + end_y or start_x - start_y == end_x - end_y or start_y == end_y or start_x == end_x) and fabs(start_x - end_x) <= 1 and fabs(start_y - end_y) <= 1:
            if not end_spot.is_empty():
                return king_color != end_spot.get_piece().is_white()
            return True
        if move.is_valid_castling(start_x, start_y, end_x, end_y):
            move.is_castling_move = True
            return True
        return False

    def get_king_threat(self, x, y, move):
        king_color = self.is_white()

        attacking_pawn = move.is_attacked_by_pawn(x, y, king_color)
        attacking_king = move.is_attacked_by_another_king(x, y, king_color)

        if attacking_pawn : return attacking_pawn
        if attacking_king : return attacking_king

        pieces_on_diagonals = move.get_pieces_on_diagonals(x, y)

        for spot in pieces_on_diagonals:
            p = spot.get_piece()
            if isinstance(p, Queen) or isinstance(p, Bishop):
                if p.is_white() != king_color:
                    return spot

        pieces_on_straight_path = move.get_pieces_on_straight_path(x, y)

        for spot in pieces_on_straight_path:
            p = spot.get_piece()
            if isinstance(p, Queen) or isinstance(p, Rook):
                if p.is_white() != king_color:
                    return spot

        pieces_on_L_path = move.remove_empty_spots(move.spots_on_L_path(x, y))
            
        for spot in pieces_on_L_path:
            if not spot.is_empty():
                p = spot.get_piece()
                if p.is_white() != king_color and isinstance(p, Knight):
                    return spot

        return False

    def is_king_safe(self, x, y, move):
        if self.get_king_threat(x, y, move):
            return False
        return True

    def can_king_move(self, x, y, move):
        possible_spots = [[x + 1, y - 1], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x - 1, y + 1], [x - 1, y], [x - 1, y - 1], [x, y - 1]]
        king_color = self.is_white()
        for spot in possible_spots:
            if 0 <= spot[0] <= 7 and 0 <= spot[1] <= 7:
                new_spot = move.curr_board.get_box(spot[0], spot[1])
                if (new_spot.is_empty() or new_spot.get_piece().is_white() != king_color) and self.is_king_safe(spot[0], spot[1], move):
                    return True
        return False

    def can_king_be_saved(self, king_spot, threat_spot, move):
        king_color = self.is_white()
        start_x = king_spot.x
        start_y = king_spot.y
        end_x = threat_spot.x
        end_y = threat_spot.y

        if start_x + start_y == end_x + end_y:
            if end_x > start_x:
                spots_between = move.spots_on_diagonal(start_x + 1, start_y - 1, end_x, end_y, "top_left")
            elif end_x < start_x:
                spots_between = move.spots_on_diagonal(start_x - 1, start_y + 1, end_x, end_y, "bottom_right")

        elif start_x - start_y == end_x - end_y:
            if end_x < start_x:
                spots_between = move.spots_on_diagonal(start_x - 1, start_y - 1, end_x, end_y, "bottom_left")
            elif end_x > start_x:
                spots_between = move.spots_on_diagonal(start_x + 1, start_y + 1, end_x, end_y, "top_right")
        elif start_y == end_y: 
            if end_x > start_x:
                spots_between = move.spots_on_vertical(start_y, start_x + 1, end_x, "up")
            elif end_x < start_x:
                spots_between = move.spots_on_vertical(start_y, start_x - 1, end_x, "down")
        elif start_x == end_x:
            if end_y > start_y:
                spots_between = move.spots_on_horizontal(start_x, start_y + 1, end_y, "right")
            elif end_y < start_y: 
                spots_between = move.spots_on_horizontal(start_x, start_y - 1, end_y, "left")
        else: spots_between = move.spots_on_L_path(start_x, start_y, end_x, end_y)

        for spot in spots_between:
            if move.can_be_covered(spot, king_color):
                return True
        return False




    def is_king_in_stalemate(self, x, y, move):
        possible_spots = [[x + 1, y - 1], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x - 1, y + 1], [x - 1, y], [x - 1, y - 1], [x, y - 1]]
        surrounded_by_alies = True
        king_color = self.is_white()
        for spot in possible_spots:
            if 0 <= spot[0] <= 7 and 0 <= spot[1] <= 7:
                new_spot = move.curr_board.get_box(spot[0], spot[1])
                if (new_spot.is_empty() or new_spot.get_piece().is_white() != king_color):
                    surrounded_by_alies = False
                if (new_spot.is_empty() or new_spot.get_piece().is_white() != king_color) and self.is_king_safe(spot[0], spot[1], move):
                    return False
        return not surrounded_by_alies

class Pawn(Piece):
    name = PieceEnum.PAWN

    def __init__(self, is_white):
        self.white = is_white
        self.first_move = True
    
    def is_first_move(self):
        return self.first_move

    def set_first_move(self, val):
        self.first_move = val

    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        pawn = self
        pawn_color = pawn.is_white()
        end_spot = move.curr_board.get_box(end_x, end_y)
        if pawn_color == True:
            if end_x > start_x:
                if end_spot.is_empty() and start_y == end_y:
                    if self.is_first_move() and end_x - start_x == 2 and move.curr_board.get_box(start_x + 1, start_y).is_empty():
                        return True
                    else:
                        return end_x - start_x == 1
                elif not(end_spot.is_empty()) and (start_x + start_y == end_x + end_y or start_x - start_y == end_x - end_y) and end_spot.get_piece().is_white() != pawn_color:
                    return end_x - start_x == 1 and fabs(end_y - start_y) == 1
            return False
        elif pawn_color == False:
            if end_x < start_x:
                if end_spot.is_empty() and start_y == end_y:
                    if self.is_first_move()and start_x - end_x == 2 and move.curr_board.get_box(start_x - 1, start_y).is_empty():
                        return True
                    else:
                        return start_x - end_x == 1
                elif not(end_spot.is_empty()) and (start_x + start_y == end_x + end_y or start_x - start_y == end_x - end_y) and end_spot.get_piece().is_white() != pawn_color:
                    return start_x - end_x == 1 and fabs(end_y - start_y) == 1
            return False

class Queen(Piece):
    name = PieceEnum.QUEEN

    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        end_spot = move.curr_board.get_box(end_x, end_y)
        piece_moved_color = self.is_white()
        if (not end_spot.is_empty() and piece_moved_color != end_spot.get_piece().is_white()) or end_spot.is_empty():
            if start_x + start_y == end_x + end_y:
                if end_x > start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x + 1, start_y - 1, end_x - 1, end_y + 1, "top_left")):
                    return False
                elif end_x < start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x - 1, start_y + 1, end_x + 1, end_y - 1, "bottom_right")):
                    return False
                return True
            elif start_x - start_y == end_x - end_y:
                if end_x < start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x - 1, start_y - 1, end_x + 1, end_y + 1, "bottom_left")):
                    return False
                elif end_x > start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x + 1, start_y + 1, end_x - 1, end_y - 1, "top_right")):
                    return False
                return True
            elif start_y == end_y: 
                if end_x > start_x and move.remove_empty_spots(move.spots_on_vertical(start_y, start_x + 1, end_x - 1, "up")):
                    return False
                elif end_x < start_x and move.remove_empty_spots(move.spots_on_vertical(start_y, start_x - 1, end_x + 1, "down")):
                    return False
                return True
            elif start_x == end_x:
                if end_y > start_y and move.remove_empty_spots(move.spots_on_horizontal(start_x, start_y + 1, end_y - 1, "right")):
                    return False
                elif end_y < start_y and move.remove_empty_spots(move.spots_on_horizontal(start_x, start_y - 1, end_y + 1, "left")):
                    return False
                return True
        return False

class Rook(Piece):
    name = PieceEnum.ROOK
    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        end_spot = move.curr_board.get_box(end_x, end_y)
        piece_moved_color = self.is_white()
        if (not end_spot.is_empty() and piece_moved_color != end_spot.get_piece().is_white()) or end_spot.is_empty():
            if start_y == end_y: 
                if end_x > start_x and move.remove_empty_spots(move.spots_on_vertical(start_y, start_x + 1, end_x - 1, "up")):
                    return False
                elif end_x < start_x and move.remove_empty_spots(move.spots_on_vertical(start_y, start_x - 1, end_x + 1, "down")):
                    return False
                return True
            elif start_x == end_x:
                if end_y > start_y and move.remove_empty_spots(move.spots_on_horizontal(start_x, start_y + 1, end_y - 1, "right")):
                    return False
                elif end_y < start_y and move.remove_empty_spots(move.spots_on_horizontal(start_x, start_y - 1, end_y + 1, "left")):
                    return False
                return True
        return False


class Knight(Piece):
    name = PieceEnum.KNIGHT

    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        end_spot = move.curr_board.get_box(end_x, end_y)
        piece_moved_color = self.is_white()
        if (not(end_spot.is_empty()) and piece_moved_color != end_spot.get_piece().is_white()) or end_spot.is_empty():
            if fabs(start_x - end_x) == 2:
                return fabs(start_y - end_y) == 1
            elif fabs(start_y - end_y) == 2:
                return fabs(start_x - end_x) == 1
        return False

class Bishop(Piece):
    name = PieceEnum.BISHOP

    def is_move_correct(self, start_x, start_y, end_x, end_y, move):
        end_spot = move.curr_board.get_box(end_x, end_y)
        piece_moved_color = self.is_white()
        if (not end_spot.is_empty() and piece_moved_color != end_spot.get_piece().is_white()) or end_spot.is_empty():
            if start_x + start_y == end_x + end_y:
                if end_x > start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x + 1, start_y - 1, end_x - 1, end_y + 1, "top_left")):
                    return False
                elif end_x < start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x - 1, start_y + 1, end_x + 1, end_y - 1, "bottom_right")):
                    return False
                return True
            elif start_x - start_y == end_x - end_y:
                if end_x < start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x - 1, start_y - 1, end_x + 1, end_y + 1, "bottom_left")):
                    return False
                elif end_x > start_x and move.remove_empty_spots(move.spots_on_diagonal(start_x + 1, start_y + 1, end_x - 1, end_y - 1, "top_right")):
                    return False
                return True
        return False


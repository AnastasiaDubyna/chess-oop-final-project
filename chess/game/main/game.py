from chess.game.main.piece import King
from chess.game.main.board import Board 
from chess.game.main.move import Move
from chess.helpers import singleton

@singleton
class Game:

    def __init__(self):
        self.players = []
        self.board = Board()
        self.moves_played = []
        self.castling_played = {
            "white" : False,
            "black" : False
        }
        self.white_king_spot = self.board.get_box(0, 4)
        self.black_king_spot = self.board.get_box(7, 4)
        self.is_checkmate_value = False
        self.is_stalemate_value = False
        self.is_check_value = False

    
    def add_player(self, player):
        self.players.append(player)

    def find_player_by(self, key, comparator):
        for i in self.players:
            if (comparator == i.__dict__[key]):
                return i
        return None

    def find_oposite_player_by(self, key, comparator):
        for i in range(len(self.players)):
            player = self.players[i]
            if (comparator == player.__dict__[key]):
                return self.players[i - 1]
        return None

    def get_board_status(self):
        board_status = []
        board = self.board
        board_len = len(board.boxes)
        for row_index in range(board_len):
            row = board.boxes[board_len - row_index - 1]
            board_st_row = []
            for el in row:
                board_st_row.append({'piece': el.get_piece_name(), 'color': el.get_piece_color()})
            board_status.append(board_st_row)
        return board_status

    def add_move(self, move):
        self.moves_played.append(move)

    def create_move(self, player_id, s_x, s_y, e_x, e_y): 
        if self.is_stalemate_value or self.is_checkmate_value:
            raise ValueError("Game over")

        player = self.find_player_by('id', player_id)

        if not self.is_player_turn(player):
            raise ValueError("Not your turn")

        curr_move = Move(player_id, s_x, s_y, e_x, e_y, self.board, self.moves_played, self.castling_played[player.color])

        convert = {
            "white" : True,
            "black" : False
        }

        if curr_move.piece_moved_color != convert[player.color]:
            raise ValueError("Play with your own pieces!")

        king_colors = {
            "white" : self.white_king_spot,
            "black" : self.black_king_spot
        }

        moving_piece = self.board.get_box(s_x, s_y).get_piece()
        king_spot = king_colors[player.color]

        if self.moves_played and self.is_check_value and not isinstance(moving_piece, King):
            self.board.add_patch(start={'x': s_x, 'y': s_y}, end={ 'x': e_x, 'y': e_y }, piece=moving_piece)
            if (not king_spot.get_piece().is_king_safe(king_spot.x, king_spot.y, curr_move)):
                self.board.clear_patch()
                raise ValueError("You can't leave king without protection")
            self.board.clear_patch()

        if curr_move.is_valid_move():
            curr_move.make_move()
            self.add_move(curr_move)

            if isinstance(curr_move.piece_moved, King):
                if player.color == "white":
                    self.white_king_spot = curr_move.end_spot
                else: self.black_king_spot = curr_move.end_spot
            self.board.increment_version()

            if curr_move.is_castling_move:
                self.castling_played[player.color] = True

            oponent_king_spot = king_colors["white" if player.color == "black" else "black"]

            if self.is_checkmate(oponent_king_spot, curr_move):
                self.raise_checkmate()
            elif self.is_check(oponent_king_spot, curr_move):
                self.set_check(True)
            else:
                self.set_check(False)
        else:
            raise ValueError("invalid move")

    def is_player_turn(self, player):
        if player.color == "white" and self.board.version % 2 == 0:
            return True
        elif player.color == "black" and self.board.version % 2 == 1:
            return True
        return False

    def is_check(self, king_spot, move):
        if not king_spot.get_piece().is_king_safe(king_spot.x, king_spot.y, move):
            return True
        return False

    def is_checkmate(self, king_spot, move):
        king_piece = king_spot.get_piece()
        king_threat_spot = king_piece.get_king_threat(king_spot.x, king_spot.y, move)
        
        if self.is_check(king_spot, move) and not king_piece.can_king_be_saved(king_spot, king_threat_spot, move):
            return True
        return False

    def raise_checkmate(self):
        self.is_checkmate_value = True

    def set_check(self, value):
        self.is_check_value = value


    

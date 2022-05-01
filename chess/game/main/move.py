from chess.game.main.piece import King, Piece, Queen, Rook, Pawn, Bishop, Knight

class Move:

    def __init__(self, player_id, s_x, s_y, e_x, e_y, curr_board, moves_played, castling_played):
        self.player = player_id
        self.curr_board = curr_board

        self.start_spot = curr_board.get_box(s_x, s_y)
        self.end_spot = curr_board.get_box(e_x, e_y)

        if  self.start_spot.is_empty():
            raise ValueError("choose not-empty spot")

        self.piece_moved = self.start_spot.get_piece()
        self.piece_moved_color = self.piece_moved.is_white()

        
        self.is_castling_move = False 
        self.moves_played = moves_played
        self.castling_played = castling_played

    def make_move(self):
        if self.is_castling_move:
            self.make_castling_move()
        else:
            if not self.end_spot.is_empty():
                self.piece_killed = self.end_spot.get_piece()
            self.end_spot.set_piece(self.piece_moved)
            self.start_spot.remove_piece()

            if isinstance(self.piece_moved, Pawn) and self.piece_moved.is_first_move():
                self.piece_moved.set_first_move(False)
                
    def make_castling_move(self):
        king_start = self.king_spot
        king_end = self.king_end_spot
        rook_start = self.rook_spot
        castling_type = self.typeof_castling
        king = king_start.get_piece()
        rook = rook_start.get_piece()
        king_color = king.is_white()

        end_spots = {
            "long": {
                True: [0, 3],
                False: [7, 3]
            },
            "short": {
                True: [0, 5],
                False: [7, 5]
            }
        }

        rook_end_coord = end_spots[castling_type][king_color]
        rook_end = self.curr_board.get_box(rook_end_coord[0], rook_end_coord[1])

        king_end.set_piece(king)
        rook_end.set_piece(rook)
        king_start.remove_piece()
        rook_start.remove_piece()

    def is_valid_move(self):
        curr_piece = self.piece_moved
        start_x = self.start_spot.x
        start_y = self.start_spot.y
        end_x = self.end_spot.x
        end_y = self.end_spot.y

        return curr_piece.is_move_correct(start_x, start_y, end_x, end_y, self)
    
    def is_valid_castling(self, king_start_x, king_start_y, king_end_x, king_end_y):
        if self.castling_played:
            return False
        king_spot = self.curr_board.get_box(king_start_x, king_start_y)
        king_end_spot = self.curr_board.get_box(king_end_x, king_end_y)

        if king_spot.is_empty():
            return False

        king = king_spot.get_piece()
        king_color = king.is_white()
        
        if king_end_spot == self.curr_board.get_box(0, 2) or king_end_spot == self.curr_board.get_box(7, 2):
            typeof_castling = "long"
            if king_color == True:
                rook_spot = self.curr_board.get_box(0, 0)
            elif king_color == False:
                rook_spot = self.curr_board.get_box(7, 0)
        elif king_end_spot == self.curr_board.get_box(0, 6) or king_end_spot == self.curr_board.get_box(7, 6):
            typeof_castling = "short"
            if king_color == True:
                rook_spot = self.curr_board.get_box(0, 7)
            elif king_color == False:
                rook_spot = self.curr_board.get_box(7, 7)
        else: 
            return False

        if rook_spot.is_empty():
            return False

        rook = rook_spot.get_piece()

        if not(isinstance(king, King)) or not(isinstance(rook, Rook)):
            return False

        cant_be_attacked = {
            "long": {
                True: [[0, 2], [0, 3], [0, 4]],
                False: [[7, 2], [7, 3], [7, 4]]
            },
            "short": {
                True: [[0, 6], [0, 5], [0, 4]],
                False: [[7, 6], [7, 5], [7, 4]]
            }
        }


        for pair in cant_be_attacked[typeof_castling][king_color]:
            if not king.is_king_safe(pair[0], pair[1], self):
                return False

        check_pieces_between = {
            "long": {
                True: [0, 1, 3, "left"],
                False: [7, 1, 3, "left"]
            },
            "short": {
                True: [0, 5, 6, "right"],
                False: [7, 5, 6, "right"]
            }
        }

        row = check_pieces_between[typeof_castling][king_color][0]
        start_col = check_pieces_between[typeof_castling][king_color][1]
        end_col = check_pieces_between[typeof_castling][king_color][2]
        direction = check_pieces_between[typeof_castling][king_color][3]

        spots_on_horizontal = self.spots_on_horizontal(row, start_col, end_col, direction)
        for spot in spots_on_horizontal:
            if not spot.is_empty():
                return False

        for move in self.moves_played:
            if move.piece_moved == king or move.piece_moved == rook:
                return False
        
        self.is_castling_move = True
        self.king_spot = king_spot
        self.king_end_spot = king_end_spot
        self.rook_spot = rook_spot
        self.typeof_castling = typeof_castling
        return True

    def is_attacked_by_pawn(self, x, y, king_color):
        if king_color == True:
            possible_spots = [[x + 1, y + 1], [x + 1, y - 1]]
        elif king_color == False:
            possible_spots = [[x - 1, y + 1], [x - 1, y - 1]]

        for pair in possible_spots:
            if 0 <= pair[0] <= 7 and 0 <= pair[1] <= 7 and not(self.curr_board.get_box(pair[0], pair[1]).is_empty()):
                piece_spot = self.curr_board.get_box(pair[0], pair[1])
                piece = piece_spot.get_piece()
                if isinstance(piece, Pawn) and piece.is_white() != king_color:
                    return piece_spot
        return False
    
    def is_attacked_by_another_king(self, x, y, king_color):
        possible_spots = [[x + 1, y - 1], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x - 1, y + 1], [x - 1, y], [x - 1, y - 1], [x, y - 1]]
        for pair in possible_spots:
            if 0 <= pair[0] <= 7 and 0 <= pair[1] <= 7:
                new_spot = self.curr_board.get_box(pair[0], pair[1])
                if not(new_spot.is_empty()) and isinstance(new_spot.get_piece(), King) and new_spot.get_piece().is_white() != king_color:
                    return new_spot
        return False

    def spots_on_diagonal(self, start_x, start_y, end_x, end_y, diagonal):
        if diagonal == "top_right":
            beg_x = start_x
            beg_y = start_y
            fin_x = end_x + 1
            fin_y = end_y
            step = 1
            inc = 1
        elif diagonal == "top_left":
            beg_x = start_x
            beg_y = start_y
            fin_x = end_x + 1
            fin_y = end_y
            step = 1
            inc = -1
        elif diagonal == "bottom_right":
            beg_x = start_x
            beg_y = start_y
            fin_x = end_x - 1
            fin_y = end_y
            step = -1
            inc = 1
        elif diagonal == "bottom_left":
            beg_x = start_x
            beg_y = start_y
            fin_x = end_x - 1
            fin_y = end_y
            step = -1
            inc = -1

        pieces_on_line = []
        for new_x in range(beg_x, fin_x, step):
            curr_spot = self.curr_board.get_box(new_x, beg_y)
            pieces_on_line.append(curr_spot)
            if beg_y == fin_y: 
                return pieces_on_line
            beg_y += inc
        return pieces_on_line

    def spots_on_vertical(self, y, start_x, end_x, direction): 
        if direction == "up":
            step = 1
            end_x += 1
        elif direction == "down":
            step = -1
            end_x -= 1
        pieces_on_line = []
        for new_x in range(start_x, end_x, step):
            curr_spot = self.curr_board.get_box(new_x, y)
            pieces_on_line.append(curr_spot)
        return pieces_on_line

    def spots_on_horizontal(self, x, start_y, end_y, direction):
        if direction == "right":
            step = 1
            end_y += 1
        elif direction == "left":
            step = -1
            end_y -= 1
        pieces_on_line = []
        for new_y in range(start_y, end_y, step):
            curr_spot = self.curr_board.get_box(x, new_y)
            pieces_on_line.append(curr_spot)
        return pieces_on_line

    def spots_on_L_path(self, x, y, end_x = None, end_y = None):
        possible_spots = [[x + 2, y + 1], [x + 2, y - 1], [x - 2, y + 1], [x - 2, y - 1]]
        pieces_on_line = []

        if end_x and end_y:
            if end_x - x == 2:
                if end_y - y == 1:
                    possible_spots = [[x, y + 1], [x + 1, y + 1], [x + 2, y + 1]]
                elif end_y - y == -1:
                    possible_spots = [[x, y - 1], [x + 1, y - 1], [x + 2, y - 1]]
            elif end_x - x == 1:
                if end_y - y == 2:
                    possible_spots = [[x, y + 1], [x, y + 2], [x + 1, y + 2]]
                elif end_y - y == -2:
                    possible_spots = [[x, y - 1], [x, y - 2], [x + 1, y - 2]]
            elif end_x - x == -2:
                if end_y - y == 1:
                    possible_spots = [[x, y + 1], [x - 1, y + 1], [x - 2, y + 1]]
                elif end_y - y == -1:
                    possible_spots = [[x, y - 1], [x - 1, y - 1], [x - 2, y - 1]]
            elif end_x - x == -1:
                if end_y - y == 2:
                    possible_spots = [[x, y + 1], [x, y + 2], [x - 1, y + 2]]
                elif end_y - y == -2:
                    possible_spots = [[x, y - 1], [x, y - 2], [x - 1, y - 2]]

        for pair in possible_spots:
            if 0 <= pair[0] <= 7 and 0 <= pair[1] <= 7:
                pieces_on_line.append(self.curr_board.get_box(pair[0], pair[1]))
        return pieces_on_line

    def remove_empty_spots(self, spots_list):
        result = []
        for spot in spots_list:
            if not spot.is_empty():
                result.append(spot)
        return result


    def get_pieces_on_diagonals(self, x, y):
        pieces_on_diagonals = []

        top_right_diagonal = self.remove_empty_spots(self.spots_on_diagonal(x + 1, y + 1, 7, 7, "top_right"))
        top_left_diagonal = self.remove_empty_spots(self.spots_on_diagonal(x + 1, y - 1, 7, 0, "top_left"))
        bottom_right_diagonal = self.remove_empty_spots(self.spots_on_diagonal(x - 1, y + 1, 0, 7, "bottom_right"))
        bottom_left_diagonal = self.remove_empty_spots(self.spots_on_diagonal(x - 1, y - 1, 0, 0, "bottom_left"))

        if top_right_diagonal:
            pieces_on_diagonals.append(top_right_diagonal[0])
        if top_left_diagonal:
            pieces_on_diagonals.append(top_left_diagonal[0])
        if bottom_right_diagonal:
            pieces_on_diagonals.append(bottom_right_diagonal[0])
        if bottom_left_diagonal:
            pieces_on_diagonals.append(bottom_left_diagonal[0])
        return pieces_on_diagonals
    
    def get_pieces_on_straight_path(self, x, y):
        pieces_on_straight_path = []

        pieces_on_top = self.remove_empty_spots(self.spots_on_vertical(y, x + 1, 7, "up"))
        pieces_on_bottom = self.remove_empty_spots(self.spots_on_vertical(y, x - 1, 0, "down"))
        pieces_on_right = self.remove_empty_spots(self.spots_on_horizontal(x, y + 1, 7, "right"))
        pieces_on_left = self.remove_empty_spots(self.spots_on_horizontal(x, y - 1, 0, "left"))

        if pieces_on_top:
            pieces_on_straight_path.append(pieces_on_top[0])
        if pieces_on_bottom:
            pieces_on_straight_path.append(pieces_on_bottom[0])
        if pieces_on_right:
            pieces_on_straight_path.append(pieces_on_right[0])
        if pieces_on_left:
            pieces_on_straight_path.append(pieces_on_left[0])
        return pieces_on_straight_path
           

    def can_be_covered(self, spot, king_color):
        x = spot.x
        y = spot.y

        if self.can_be_covered_by_pawn(spot, king_color):
            return True

        pieces_on_diagonals = self.get_pieces_on_diagonals(x, y)

        for spot in pieces_on_diagonals:
            p = spot.get_piece()
            if isinstance(p, Queen) or isinstance(p, Bishop):
                if p.is_white() == king_color:
                    return True

        pieces_on_straight_path = self.get_pieces_on_straight_path(x, y)

        for spot in pieces_on_straight_path:
            p = spot.get_piece()
            if isinstance(p, Queen) or isinstance(p, Rook):
                if p.is_white() == king_color:
                    return True

        pieces_on_L_path = self.remove_empty_spots(self.spots_on_L_path(x, y))
            
        for spot in pieces_on_L_path:
            p = spot.get_piece()
            if p.is_white() == king_color and isinstance(p, Knight):
                return True
        return False
    
    def can_be_covered_by_pawn(self, spot, king_color):
        x = spot.x
        y = spot.y

        if king_color:
            possible_pawn_spot_1 = self.curr_board.get_box(x - 1, y)
            if 0 <= x - 1 <= 7:
                if not(possible_pawn_spot_1.is_empty()) and isinstance(possible_pawn_spot_1, Pawn) and possible_pawn_spot_1.get_piece().is_white() == king_color:
                    return True
            if 0 <= x - 2 <= 7:
                possible_pawn_spot_2 = self.curr_board.get_box(x - 2, y)
                if not(possible_pawn_spot_2.is_empty()) and isinstance(possible_pawn_spot_2, Pawn) and possible_pawn_spot_2.get_piece().is_white() == king_color and possible_pawn_spot_2.get_piece().is_first_move():
                    return True

        elif not king_color:
            if 0 <= x + 1 <= 7:
                possible_pawn_spot_1 = self.curr_board.get_box(x + 1, y)
                if not(possible_pawn_spot_1.is_empty()) and isinstance(possible_pawn_spot_1, Pawn) and possible_pawn_spot_1.get_piece().is_white() == king_color:
                    return True
            if 0 <= x + 2 <= 7:
                possible_pawn_spot_2 = self.curr_board.get_box(x + 2, y)
                if not(possible_pawn_spot_2.is_empty()) and isinstance(possible_pawn_spot_2, Pawn) and possible_pawn_spot_2.get_piece().is_white() == king_color and possible_pawn_spot_2.get_piece().is_first_move():
                    return True
        return False

            


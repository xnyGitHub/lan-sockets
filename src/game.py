"""Game object"""
from typing import Union, Tuple, List, Dict
import numpy as np

class GameEngine:
    """Holds the game state."""

    def __init__(self):
        """Create new gamestate"""

        self.player_turn = True

        self.move_log = []
        self.white_moves: list = []
        self.black_moves: list = []
        self.piece_moves: list = self.piece_movemovents()

        """Default board constructor"""
        self.board: np.array = np.array(
            [
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bB"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
            ]
        )

        self.generate_all_moves()

    def make_move(self, move):

        start_cords, end_cords = move.split(':')
        start_col, start_row = [int(x) for x in start_cords]
        end_col, end_row = [int(x) for x in end_cords]

        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = "--"
        self.player_turn = not self.player_turn

        move_data = f'{start_cords}:{end_cords}:{self.board[start_row][start_col]}:{self.board[end_row][end_col]}'
        self.move_log.append(move_data)
        self.generate_all_moves()

    def undo_move(self):
        move = self.move_log[-1]
        start_cords, end_cords, piece_captured, piece_moved = move.split(':')
        start_col, start_row = [int(x) for x in start_cords]
        end_col, end_row = [int(x) for x in end_cords]
        self.board[start_row][start_col] = piece_moved
        self.board[end_row][end_col] = piece_captured

        self.player_turn = not self.player_turn
        self.move_log.pop()
        self.generate_all_moves()

    def get_white_moves(self):
        return self.white_moves

    def get_black_moves(self):
        return self.black_moves

    def get_board(self):
        return self.board

    def get_move_log(self):
        return self.move_log

    def piece_movemovents(self):
        """Piece movements helper function"""
        map_dict = {
            "P": {"movements": [1, -1], "continous": False},
            "R": {"movements": [(1, 0), (0, 1), (-1, 0), (0, -1)], "continous": True},
            "N": {"movements": [(-2, -1),(-2, 1),(2, -1),(2, 1),(-1, -2),(1, -2),(-1, 2),(1, 2),],"continous": False,},
            "B": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1)], "continous": True},
            "Q": {"movements": [(1, 1),(-1, 1),(1, -1),(-1, -1),(1, 0),(0, 1),(-1, 0),(0, -1),],"continous": True,},
            "K": {"movements": [(1, 1),(-1, 1),(1, -1),(-1, -1),(1, 0),(0, 1),(-1, 0),(0, -1),],"continous": False,},
        }
        return map_dict


    def is_in_bounds(self,new_x: int, new_y: int) -> bool:
        """Check if a set of cords is in-bounds"""
        if 0 <= new_x <= 7 and 0 <= new_y <= 7:
            return True
        return False

    def has_pawn_moved(self,current_row: int, piece_color: str) -> bool:
        """Given a row and color return whether a pawn has moved"""
        if current_row == 6 and piece_color == "w":
            return False
        if current_row == 1 and piece_color == "b":
            return False
        return True

    def get_piece_moves_dict(self, piece_type: str) -> Union[list, bool]:
        """Return info: (dict) on ghow a particular piece moves"""
        movements = self.piece_moves[piece_type]["movements"]
        continuous = self.piece_moves[piece_type]["continous"]
        return movements, continuous

    def generate_all_moves(self) -> None:
        """Function that calls get moves"""
        # Clear each time otherwise we end up with duplicates
        self.white_moves.clear()
        self.black_moves.clear()

        # Loop board and get moves for each pieace
        for index, chess_square in np.ndenumerate(self.board): # Type: tuple(int,int) , str
            if chess_square != "--":

                array: list = []
                piece_color, piece_type = chess_square # Type: str, str
                array = self.white_moves if piece_color == "w" else self.black_moves

                if piece_type == "P":  # Pawn
                    self.get_pawn_moves(index, array, chess_square)
                else:
                    self.get_non_pawn_moves(index, array, chess_square)



    def get_non_pawn_moves(self, index: Tuple[int,int], array: List[Dict[list,bool]], chess_square: str) -> None:
        """Generate non-pawn moves here"""
        # ---------------
        row, col = index
        piece_color, piece_type = chess_square
        # -------------------------------------
        movements, is_continious = self.get_piece_moves_dict(piece_type)

        # Loop through piece movements list
        for add_x, add_y in movements:  # Grab movements
            new_row, new_col = row + add_x, col + add_y  # Get new pos
            while self.is_in_bounds(new_row, new_col):  #
                # Check if the square is empty
                if self.board[new_row][new_col] == "--":
                    array.append(f"{col}{row}:{new_col}{new_row}")
                    if not is_continious:
                        break
                    new_row += add_x
                    new_col += add_y
                else:
                    # Collides with team piece
                    if self.board[new_row][new_col][0] == piece_color:
                        break
                    # Collides with enemy piece
                    array.append(f"{col}{row}:{new_col}{new_row}")
                    break

    def get_pawn_moves(self, index: Tuple[int,int], array: List[Dict[list,bool]], chess_square: str) -> None:
        """Generate pawn moves"""
        # -------------------------------------
        row, col = index
        piece_color, piece_type = chess_square
        direction = -1 if piece_color == "w" else 1
        # -------------------------------------
        movements, _ = self.get_piece_moves_dict(piece_type)

        # Check if its inbounds
        if self.is_in_bounds(row + direction, col):

            # One square move
            if self.board[row + direction][col] == "--":  # If empty
                array.append(f"{col}{row}:{col}{row + direction}")

                # Two square move
                if (not self.has_pawn_moved(row, piece_color) and self.board[row + (direction * 2)][col] == "--"):
                    array.append(f"{col}{row}:{col}{row+(direction*2)}")

            # Captures
            for add_y in movements:
                if 0 <= (col + add_y) <= 7:
                    if self.board[row + direction][col + add_y][0] != "-":
                        if (self.board[row + direction][col + add_y][0] != piece_color):  # Move up left check
                            array.append(f"{col}{row}:{col+ add_y}{row+direction}")
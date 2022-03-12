"""Game object"""
from typing import Union
import numpy as np

class GameEngine:
    """Holds the game state."""

    def __init__(self):
        """Create new gamestate"""

        self.running: bool = False
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
        self.board[move.end_row][move.end_col] = self.board[move.start_row][move.start_col]
        self.board[move.start_row][move.start_col] = "--"

        self.player_turn = not self.player_turn
        self.move_log.append(move)
        self.generate_all_moves()

    def undoMove(self):
        move = self.move_log[-1]
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured

        self.player_turn = not self.player_turn
        self.moveLog.pop()

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

    def check_has_pawn_moved(self,current_row: int, piece_color: str) -> bool:
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
        for index, chess_square in np.ndenumerate(self.board):
            if chess_square != "--":

                array: list = []
                piece_color: str
                piece_type: str
                piece_color, piece_type = chess_square

                if piece_color == "w":
                    array = self.white_moves
                if piece_color == "b":
                    array = self.black_moves

                if piece_type == "P":  # Pawn
                    self.get_pawn_moves(index, array, chess_square)
                else:
                    self.get_non_pawn_moves(index, array, chess_square)

    def get_white_moves(self):
        return self.white_moves

    def get_black_moves(self):
        return self.black_moves

    def get_non_pawn_moves(self, index: tuple, array: list, chess_square: str) -> None:
        """Generate non-pawn moves here"""
        row: int
        col: int
        row, col = index
        # ---------------
        piece_color: str
        piece_type: str
        piece_color, piece_type = chess_square
        # -------------------------------------
        movements: list
        is_continious: bool
        movements, is_continious = self.get_piece_moves_dict(piece_type)

        # Loop through piece movements list
        for add_x, add_y in movements:  # Grab movements
            new_row, new_col = row + add_x, col + add_y  # Get new pos
            while self.is_in_bounds(new_row, new_col):  #
                # Check if the square is empty
                if self.board[new_row][new_col] == "--":
                    array.append((f"{col}{row}", f"{new_col}{new_row}"))
                    if not is_continious:
                        break
                    new_row += add_x
                    new_col += add_y
                else:
                    # Collides with team piece
                    if self.board[new_row][new_col][0] == piece_color:
                        break
                    # Collides with enemy piece
                    array.append((f"{col}{row}", f"{new_col}{new_row}"))
                    break

    def get_pawn_moves(self, index: tuple, array: list, chess_square: str) -> None:
        """Generate pawn moves"""

        # -------------------------------------
        row: int
        col: int
        row, col = index
        # -------------------------------------
        piece_color: str
        piece_type: str
        piece_color, piece_type = chess_square
        # -------------------------------------
        movements: list
        movements, _ = self.get_piece_moves_dict(piece_type)

        # -------------------------------------
        direction = 0
        if piece_color == "w":
            direction = -1
        if piece_color == "b":
            direction = 1

        # Check if its inbounds
        if self.is_in_bounds(row + direction, col):
            if self.board[row + direction][col] == "--":  # If empty
                array.append((f"{col}{row}", f"{col}{row + direction}"))

                # Two square move
                if (
                    not self.check_has_pawn_moved(row, piece_color)
                    and self.board[row + (direction * 2)][col] == "--"
                ):
                    array.append((f"{col}{row}", f"{col}{row+(direction*2)}"))
            # Capture
            for add_y in movements:
                if 0 <= (col + add_y) <= 7:
                    if self.board[row + direction][col + add_y][0] != "-":
                        if (
                            self.board[row + direction][col + add_y][0] != piece_color
                        ):  # Move up left check
                            array.append(
                                (f"{col}{row}", f"{col+ add_y}{row+direction}")
                            )


class Move:
    """Class that stores info about a move"""

    def __init__(self, start_square, end_square,board):
        """Each move has a move type Normal | Capture | Castle | EnPassant
        start_square: (tuple) -> (row,col)
        end_square: (tuple) -> (row,col)
        """
        self.start_square = start_square
        self.end_square = end_square
        self.start_row = int(start_square[1])
        self.start_col = int(start_square[0])
        self.end_row = int(end_square[1])
        self.end_col = int(end_square[0])
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
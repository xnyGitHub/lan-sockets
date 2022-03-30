"""Game object"""
from typing import Tuple, List
import numpy as np


class GameEngine:
    """Holds the game state."""

    def __init__(self) -> None:
        """Create new gamestate"""

        self.player_turn = True

        self.move_log: list = []
        self.white_moves: list = []
        self.black_moves: list = []
        self.piece_moves: dict = self.piece_movemovents()

        """Default board constructor"""
        self.board: np.ndarray = np.array(
            [
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
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

    def make_move(self, move: str) -> None:
        """
        Make a move
        Move param is a string in the format of "start:end" e.g 10:30
        """

        # Parsing
        start_cords, end_cords = move.split(":")
        start_col, start_row = [int(x) for x in start_cords]
        end_col, end_row = [int(x) for x in end_cords]

        # Make the move
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = "--"
        self.player_turn = not self.player_turn

        # Add the move log and regen the moves
        move_data = f"{start_cords}:{end_cords}:{self.board[start_row][start_col]}:{self.board[end_row][end_col]}"
        self.move_log.append(move_data)
        self.generate_all_moves()

    def undo_move(self) -> None:
        """
        Undo a move
        Moves is the move_log are in the same format as in make_move
        """

        # Get latest move and parse it
        move = self.move_log[-1]
        start_cords, end_cords, piece_captured, piece_moved = move.split(":")
        start_col, start_row = [int(x) for x in start_cords]
        end_col, end_row = [int(x) for x in end_cords]

        # Undo the move
        self.board[start_row][start_col] = piece_moved
        self.board[end_row][end_col] = piece_captured

        self.player_turn = not self.player_turn
        self.move_log.pop()  # Remove the undone move from list of moves
        self.generate_all_moves()  # Regen all the moves

    def get_white_moves(self) -> List[str]:
        """Return list of white moves"""
        return self.white_moves

    def get_black_moves(self) -> List[str]:
        """Return list of black moves"""
        return self.black_moves

    def get_board(self) -> np.ndarray:
        """Return the board"""
        return self.board

    def get_move_log(self) -> List[str]:
        """Return the move log"""
        return self.move_log

    def piece_movemovents(self) -> dict:
        """Piece movements helper function"""
        # pylint: disable=no-self-use
        # fmt: off
        map_dict = {
            "P": {"movements": (1, -1), "continous": False},
            "R": {"movements": [(1, 0), (0, 1), (-1, 0), (0, -1)], "continous": True},
            "N": {"movements": [(-2, -1),(-2, 1),(2, -1),(2, 1),(-1, -2),(1, -2),(-1, 2),(1, 2),],"continous": False},
            "B": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1)], "continous": True},
            "Q": {"movements": [(1, 1),(-1, 1),(1, -1),(-1, -1),(1, 0),(0, 1),(-1, 0),(0, -1),],"continous": True},
            "K": {"movements": [(1, 1),(-1, 1),(1, -1),(-1, -1),(1, 0),(0, 1),(-1, 0),(0, -1),],"continous": False}
        }
        # fmt: on
        return map_dict

    def is_in_bounds(self, new_x: int, new_y: int) -> bool:
        """Check if a set of cords is in-bounds"""
        # pylint: disable=no-self-use
        if 0 <= new_x <= 7 and 0 <= new_y <= 7:
            return True
        return False

    def has_pawn_moved(self, current_row: int, piece_color: str) -> bool:
        """Given a row and color return whether a pawn has moved"""
        # pylint: disable=no-self-use
        if current_row == 6 and piece_color == "w":
            return False
        if current_row == 1 and piece_color == "b":
            return False
        return True

    def get_piece_moves_dict(self, piece_type: str) -> Tuple[List[Tuple[int, int]], bool]:
        """Return info: (dict) on ghow a particular piece moves"""

        piece_move_info: dict = self.piece_moves[piece_type]
        movements: List[Tuple[int, int]] = piece_move_info["movements"]
        continuous: bool = piece_move_info["continous"]
        return movements, continuous

    def generate_all_moves(self) -> None:
        """Function that calls get moves"""
        # Clear each time otherwise we end up with duplicates
        self.white_moves.clear()
        self.black_moves.clear()
        index: Tuple[int, int]
        chess_square: str
        piece_color: str
        piece_type: str
        # Loop board and get moves for each pieace
        for index, chess_square in np.ndenumerate(self.board):  # type: ignore
            if chess_square != "--":

                array: list = []
                piece_color, piece_type = chess_square  # type: ignore
                array = self.white_moves if piece_color == "w" else self.black_moves

                if piece_type == "P":  # Pawn
                    self.get_pawn_moves(index, array, chess_square)
                else:
                    self.get_non_pawn_moves(index, array, chess_square)

    def get_non_pawn_moves(self, index: Tuple[int, int], array: list, chess_square: str) -> None:
        """Generate non-pawn moves here"""
        # ---------------
        row: int
        col: int
        piece_color: str
        piece_type: str
        row, col = index
        piece_color, piece_type = chess_square  # type: ignore
        # -------------------------------------
        movements, is_continious = self.get_piece_moves_dict(piece_type)

        for add_x, add_y in movements:  # Loop through piece movements list
            new_row, new_col = row + add_x, col + add_y  # Get new starting pos
            while self.is_in_bounds(new_row, new_col):

                # Check if the square is empty
                if self.board[new_row][new_col] == "--":
                    array.append(f"{col}{row}:{new_col}{new_row}")
                    if not is_continious:  # If piece type doesn't continuously move e.g Knight, Pawn, King etc..
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

    def get_pawn_moves(self, index: Tuple[int, int], array: list, chess_square: str) -> None:
        """Generate pawn moves"""
        # -------------------------------------
        row: int
        col: int
        direction: int
        piece_color: str
        piece_type: str
        row, col = index
        piece_color, piece_type = chess_square  # type: ignore
        direction = -1 if piece_color == "w" else 1
        # -------------------------------------
        movements, _ = self.get_piece_moves_dict(piece_type)

        # Check if its inbounds
        if self.is_in_bounds(row + direction, col):

            # One square move
            if self.board[row + direction][col] == "--":  # If empty
                array.append(f"{col}{row}:{col}{row + direction}")

                # Two square move
                if (
                    not self.has_pawn_moved(row, piece_color) and self.board[row + (direction * 2)][col] == "--"
                ):  # If its empty and pawn hasn't moved
                    array.append(f"{col}{row}:{col}{row+(direction*2)}")

            # Captures
            for add_y in movements:
                new_y = col + add_y  # type: ignore
                if 0 <= new_y <= 7:  # In-bounds
                    if self.board[row + direction][new_y][0] != "-":  # Not empty square
                        if self.board[row + direction][new_y][0] != piece_color:  # Collides with enemy
                            array.append(f"{col}{row}:{new_y}{row+direction}")

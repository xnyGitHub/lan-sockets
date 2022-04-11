"""Game object"""
from typing import Tuple, List
import numpy as np


class GameEngine:
    """Holds the game state."""

    SORT_ORDER = {"P": 0, "N": 1, "B": 2, "R": 3, "Q": 4}

    def __init__(self) -> None:
        """Create new gamestate"""

        self.player_turn = "white"
        self.move_log: list = []
        self.move_log_fen: list = []
        self.white_moves: list = []
        self.black_moves: list = []

        self.white_captured: list = []
        self.black_captured: list = []
        self.piece_moves: dict = self.piece_movemovents()

        self.check_status: dict = {}

        self.gamestate: dict = {"gamestate": "Running", "winner": "None"}

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

    def make_move(self, move: str, player_invoked: bool = False) -> None:
        """
        Make a move
        Move param is a string in the format of "start:end" e.g 10:30
        """

        # Parsing
        movetype = move[-1]
        if movetype in ("N", "T"):
            start_cords, end_cords, movetype = move.split(":")
            start_col, start_row = [int(x) for x in start_cords]
            end_col, end_row = [int(x) for x in end_cords]

            # Generate move data
            piece_moved = self.board[start_row][start_col]
            piece_captured = self.board[end_row][end_col]

            if player_invoked and piece_captured != "--":
                if piece_captured[0] == "w":
                    self.white_captured.append(piece_captured)
                else:
                    self.black_captured.append(piece_captured)

            # Add to move log
            move_data = f"{start_cords}:{end_cords}:{piece_moved}:{piece_captured}:{movetype}"
            self.move_log.append(move_data)

            # Make the move
            self.board[end_row][end_col] = self.board[start_row][start_col]
            self.board[start_row][start_col] = "--"

        # Switch turns

        elif movetype == "C":
            king_start, king_end, rook_start, rook_end, movetype = move.split(":")

            king_start_col, king_start_row = [int(x) for x in king_start]
            king_end_col, king_end_row = [int(x) for x in king_end]
            rook_start_col, rook_start_row = [int(x) for x in rook_start]
            rook_end_col, rook_end_row = [int(x) for x in rook_end]

            self.board[king_end_row][king_end_col] = self.board[king_start_row][king_start_col]
            self.board[king_start_row][king_start_col] = "--"

            self.board[rook_end_row][rook_end_col] = self.board[rook_start_row][rook_start_col]
            self.board[rook_start_row][rook_start_col] = "--"

            move_data = f"{king_start}:{king_end}:{rook_start}:{rook_end}:{movetype}"
            self.move_log.append(move_data)

        self.switch_turns()

    def undo_move(self, player_invoked: bool = False) -> None:
        """
        Undo a move
        Moves is the move_log are in the same format as in make_move
        """

        # Get latest move and parse it
        move = self.move_log[-1]

        movetype = move[-1]
        if movetype in ("N", "T"):
            start_cords, end_cords, piece_moved, piece_captured, movetype = move.split(":")
            start_col, start_row = [int(x) for x in start_cords]
            end_col, end_row = [int(x) for x in end_cords]

            # Undo the move
            self.board[start_row][start_col] = piece_moved
            self.board[end_row][end_col] = piece_captured

            if player_invoked and piece_captured != "--":
                if piece_captured[0] == "w":
                    self.white_captured.remove(piece_captured)
                else:
                    self.black_captured.remove(piece_captured)

        elif movetype == "C":
            king_start, king_end, rook_start, rook_end, movetype = move.split(":")

            king_start_col, king_start_row = [int(x) for x in king_start]
            king_end_col, king_end_row = [int(x) for x in king_end]
            rook_start_col, rook_start_row = [int(x) for x in rook_start]
            rook_end_col, rook_end_row = [int(x) for x in rook_end]

            self.board[king_start_row][king_start_col] = self.board[king_end_row][king_end_col]
            self.board[king_end_row][king_end_col] = "--"

            self.board[rook_start_row][rook_start_col] = self.board[rook_end_row][rook_end_col]
            self.board[rook_end_row][rook_end_col] = "--"

        # Remove move from move log
        self.move_log.pop()
        if player_invoked:
            self.move_log_fen.pop()
        self.switch_turns()

    def switch_turns(self) -> None:
        """Switch player turns"""
        if self.player_turn == "black":
            self.player_turn = "white"
        elif self.player_turn == "white":
            self.player_turn = "black"

    def get_board(self) -> np.ndarray:
        """Return the board"""
        return self.board

    def get_white_moves(self) -> List[str]:
        """Return list of white moves"""
        return self.white_moves

    def get_captured_pieces(self) -> dict:
        """Return captured pieces"""
        self.white_captured.sort(key=lambda val: GameEngine.SORT_ORDER[val[1]])
        self.black_captured.sort(key=lambda val: GameEngine.SORT_ORDER[val[1]])
        pieces: dict = {"white": self.white_captured, "black": self.black_captured}
        return pieces

    def get_move_log(self) -> List[str]:
        """Return the move log"""
        return self.move_log

    def get_fen_move_log(self) -> List[str]:
        """Return the fen move log"""
        return self.move_log_fen

    def get_black_moves(self) -> List[str]:
        """Return list of black moves"""
        return self.black_moves

    def get_check_status(self) -> dict:
        """Return the check status"""
        return self.check_status

    def get_gamestate(self) -> dict:
        """Return the current gamestate"""
        return self.gamestate

    def get_king_location(self, king_piece: str) -> str:
        """Return the kings location for the piece passed in"""
        row, col = np.where(self.board == king_piece)
        return f"{col[0]}{row[0]}"

    def is_king_under_attack(self, color: str) -> bool:
        """Check if a king is under attack"""
        king_piece: str = ""
        if color == "White":
            king_piece = "wK"
        else:
            king_piece = "bK"

        king_location = self.get_king_location(king_piece)
        enemy_moves: list = []

        if king_piece == "wK":
            enemy_moves = self.get_black_moves()
        else:
            enemy_moves = self.get_white_moves()

        for move in enemy_moves:
            if king_location in move:
                return True
        return False

    def is_in_bounds(self, new_x: int, new_y: int) -> bool:
        """Check if a set of cords is in-bounds"""
        # pylint: disable=no-self-use
        if 0 <= new_x <= 7 and 0 <= new_y <= 7:
            return True
        return False

    def convert_to_fen(self, move: str) -> str:
        """Function responsible for converting a move to fen"""
        move_type = move[-1]
        fen_string: str = ""
        if move_type in ("N", "T"):
            start, stop, piece, cap, _ = move.split(":")

            results = self.convert_index_to_fen(start, stop)
            start, stop = results
            piece_notation = piece[1]
            capture_notation = "x" if cap != "--" else ""

            fen_string = f"{piece_notation}{start}{capture_notation}{stop}"

        elif move_type == "C":
            rook_col: str
            _, _, rook_start, _, _ = move.split(":")
            rook_col, _ = rook_start  # type: ignore
            if rook_col == "0":
                fen_string = "0-0-0"
            else:
                fen_string = "0-0"
        elif move_type == "E":
            fen_string = "En-passant"

        return fen_string

    @staticmethod
    def convert_index_to_fen(*move: str) -> list:
        """Convert cords to fen notation"""
        col: str = ""
        row: str = ""
        col_to_file = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        row_to_rank = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}

        results: list = []
        for col, row in move:  # type: ignore
            results.append(f"{col_to_file[int(col)]}{row_to_rank[int(row)]}")

        return results

    def get_moves(self) -> None:
        """Call the functions that will generate all legal moves"""
        # self.check_for_pawn_promotion()
        self.generate_all_moves()
        self.filter_invalid_moves()

        self.check_castle_rights_for_white()
        self.check_castle_rights_for_black()

        self.check_en_passant()

        self.generate_fen_nation_move_log()
        self.check_gamestate()

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
                    array.append(f"{col}{row}:{new_col}{new_row}:N")
                    if not is_continious:  # If piece type doesn't continuously move e.g Knight, Pawn, King etc..
                        break
                    new_row += add_x
                    new_col += add_y
                else:
                    # Collides with team piece
                    if self.board[new_row][new_col][0] == piece_color:
                        break
                    # Collides with enemy piece
                    array.append(f"{col}{row}:{new_col}{new_row}:T")
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
                array.append(f"{col}{row}:{col}{row + direction}:N")

                # Two square move
                if (
                    not self.has_pawn_moved(row, piece_color) and self.board[row + (direction * 2)][col] == "--"
                ):  # If its empty and pawn hasn't moved
                    array.append(f"{col}{row}:{col}{row+(direction*2)}:N")

            # Captures
            for add_y in movements:
                new_y = col + add_y  # type: ignore
                if 0 <= new_y <= 7:  # In-bounds
                    if self.board[row + direction][new_y][0] != "-":  # Not empty square
                        if self.board[row + direction][new_y][0] != piece_color:  # Collides with enemy
                            array.append(f"{col}{row}:{new_y}{row+direction}:T")

    def has_pawn_moved(self, current_row: int, piece_color: str) -> bool:
        """Given a row and color return whether a pawn has moved"""
        # pylint: disable=no-self-use
        if current_row == 6 and piece_color == "w":
            return False
        if current_row == 1 and piece_color == "b":
            return False
        return True

    def filter_invalid_moves(self) -> None:
        """Remove illegal moves"""
        black_invalid = []  # This will hold in valid moves
        white_invalid = []

        if self.player_turn == "white":
            for white_move in self.white_moves:
                self.make_move(white_move)
                self.generate_all_moves()
                for opponent_move in self.black_moves:
                    white_king_location = self.get_king_location("wK")
                    if white_king_location in opponent_move:
                        white_invalid.append(white_move)
                        break
                self.undo_move()
                self.generate_all_moves()
        else:
            for black_move in self.black_moves:
                self.make_move(black_move)
                self.generate_all_moves()
                for opponent_move in self.white_moves:
                    black_king_location = self.get_king_location("bK")
                    if black_king_location in opponent_move:
                        black_invalid.append(black_move)
                        break
                self.undo_move()
                self.generate_all_moves()

        self.black_moves = list(set(self.black_moves) - set(black_invalid))
        self.white_moves = list(set(self.white_moves) - set(white_invalid))

    def check_castle_rights_for_white(self) -> None:
        """Check if white can castle"""

        white_king_location = self.get_king_location("wK")
        king_side_rook_location: str = "07"
        queen_right_rook_location: str = "77"
        king_side: bool = True
        queen_side: bool = True
        col: str
        row: str

        # ----------------- Check king is not in check and hasnt moved -----------------
        if any(white_king_location in moves for moves in self.black_moves) or any(
            white_king_location in moves for moves in self.move_log
        ):
            return

        # ---------------- Check the rook hasn't moved or been captured ----------------
        if any(king_side_rook_location in moves for moves in self.move_log):
            king_side = False

        if any(queen_right_rook_location in moves for moves in self.move_log):
            queen_side = False

        # ------------ Check the castle squares are EMPTY and NOT in check -------------
        # King-side
        free_square = ["37", "27", "17"]
        for row, col in free_square:  # type: ignore
            if self.board[int(col)][int(row)] != "--":
                king_side = False
                break

        check_squares = ["37", "27"]
        if any(square in move for move in self.black_moves for square in check_squares):
            king_side = False

        # Queen-side
        free_square = ["57", "67"]
        for row, col in free_square:  # type: ignore
            if self.board[int(col)][int(row)] != "--":
                queen_side = False
                break

        check_squares = ["57", "67"]
        if any(square in move for move in self.black_moves for square in check_squares):
            queen_side = False
        # ------------------------------------------------------------------------------

        if king_side:
            self.white_moves.append("47:27:07:37:C")
        if queen_side:
            self.white_moves.append("47:67:77:57:C")

    def check_castle_rights_for_black(self) -> None:
        """Check if black can castle"""

        black_king_location = self.get_king_location("bK")
        king_side_rook_location: str = "00"
        queen_right_rook_location: str = "70"
        king_side: bool = True
        queen_side: bool = True
        col: str
        row: str

        # ----------------- Check king is not in check and hasnt moved -----------------
        if any(black_king_location in moves for moves in self.white_moves) or any(
            black_king_location in moves for moves in self.move_log
        ):
            return

        # ---------------- Check the rook hasn't moved or been captured ----------------
        if any(king_side_rook_location in moves for moves in self.move_log):
            king_side = False

        if any(queen_right_rook_location in moves for moves in self.move_log):
            queen_side = False

        # ------------ Check the castle squares are EMPTY and NOT in check -------------
        # King-side
        free_square = ["10", "20", "30"]
        for row, col in free_square:  # type: ignore
            if self.board[int(col)][int(row)] != "--":
                king_side = False
                break

        check_squares = ["20", "30"]
        if any(square in move for move in self.white_moves for square in check_squares):
            king_side = False

        # Queen-side
        free_square = ["50", "60"]
        for row, col in free_square:  # type: ignore
            if self.board[int(col)][int(row)] != "--":
                queen_side = False
                break

        check_squares = ["50", "60"]
        if any(square in move for move in self.white_moves for square in check_squares):
            queen_side = False
        # ------------------------------------------------------------------------------

        if king_side:
            self.black_moves.append("40:20:00:30:C")
        if queen_side:
            self.black_moves.append("40:60:70:50:C")

    def check_en_passant(self):
        """Function to check for en_passant"""
        latest_move =  self.move_log[-1]
        start_cords, end_cords, piece_moved, piece_captured, movetype = latest_move.split(":")

        color, piece = piece_moved
        if piece != "P" or movetype == "C":
            return

        enemy_move_array = self.white_moves if color == "b" else self.black_moves
        direction = -1 if color == "w" else 1
        start_col, start_row = [int(x) for x in start_cords]
        end_col, end_row = [int(x) for x in end_cords]


        if start_col == start_cords and abs(start_row-end_row) == 2:
            if self.board[end_row][end_col-1][1] == "P":
                enemy_move_array.append(f"{end_col-1}{end_row}:{start_col}{start_row + direction}:E")

            if self.board[end_row][end_col+1][1] == "P":
                enemy_move_array.append(f"{end_col-1}{end_row}:{start_col}{start_row + direction}:E")

    def generate_fen_nation_move_log(self) -> None:
        """Convert move_log into long algebraic notation"""
        if not self.move_log:
            return

        latest_move = self.move_log[-1]
        fen_notation = self.convert_to_fen(latest_move)
        self.move_log_fen.append(fen_notation)

    def check_gamestate(self) -> None:
        """
        This function is responsible for the following;

        (1) Check if a player is in check
            If so -
                Update self.check_status with the king that is being attacked
                Update self.check_status with the pieces attcked in the king
                Update the latest move in self.move_log_fen with "+"

        (2) Check if a player is in checkmate
            If so -
                Update self.check_status with the king that is being attacked
                Update self.check_status with the pieces attcked in the king
                Update the latest move in self.move_log_fen with "#"

                Update self.gamestate to "Checkmate"

        (2) Check if the game is stalemate
            If so -
                Update self.gamestate to "Stalemate"
        """
        # ----------------(1) Check if a player is in check----------------"""
        if self.player_turn == "white":
            white_king_location = self.get_king_location("wK")
            results = [moves for moves in self.black_moves if white_king_location in moves]
            if results:
                self.check_status["king_location"] = white_king_location
                self.check_status["attacking_pieces"] = results

                latest_move = self.move_log_fen[-1]
                if not self.white_moves:
                    self.move_log_fen[-1] = latest_move + "#"
                else:
                    self.move_log_fen[-1] = latest_move + "+"

            else:
                self.check_status = {}

        if self.player_turn == "black":
            black_king_location = self.get_king_location("bK")
            results = [moves for moves in self.white_moves if black_king_location in moves]
            if results:
                self.check_status["king_location"] = black_king_location
                self.check_status["attacking_pieces"] = results

                latest_move = self.move_log_fen[-1]
                if not self.black_moves:
                    self.move_log_fen[-1] = latest_move + "#"
                else:
                    self.move_log_fen[-1] = latest_move + "+"
            else:
                self.check_status = {}

        # ----------(2) Check if the gamestate is checkmate or stalemate-----------

        if self.is_king_under_attack("Black") and not len(self.get_black_moves()):
            self.gamestate["gamestate"] = "Checkmate"
            self.gamestate["winner"] = "White"
        elif not self.is_king_under_attack("Black") and not len(self.get_black_moves()):
            self.gamestate["gamestate"] = "Stalemate"
            self.gamestate["winner"] = "None"
        elif self.is_king_under_attack("White") and not len(self.get_white_moves()):
            self.gamestate["gamestate"] = "Checkmate"
            self.gamestate["winner"] = "Black"
        elif not self.is_king_under_attack("White") and not len(self.get_white_moves()):
            self.gamestate["gamestate"] = "Stalemate"
            self.gamestate["winner"] = "None"

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

    def get_piece_moves_dict(self, piece_type: str) -> Tuple[List[Tuple[int, int]], bool]:
        """Return info: (dict) on ghow a particular piece moves"""

        piece_move_info: dict = self.piece_moves[piece_type]
        movements: List[Tuple[int, int]] = piece_move_info["movements"]
        continuous: bool = piece_move_info["continous"]
        return movements, continuous

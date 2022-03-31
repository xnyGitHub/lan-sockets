"""Model class for MVC"""
import typing
import numpy as np
from src.chess.engine.event import EventManager, QuitEvent, TickEvent, UpdateEvent, Event


class GameEngine:
    """Holds the game state."""

    def __init__(self, ev_manager: EventManager) -> None:
        """Create new gamestate"""
        self.ev_manager: EventManager = ev_manager
        ev_manager.register_listener(self)
        self.running: bool = False
        self.moves: list = []
        self.move_log: list = []
        self.color: str = "None"

        """Default board constructor"""
        self.board: list = [
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
        ]

    def notify(self, event: Event) -> None:
        """Notify"""
        if isinstance(event, QuitEvent):
            self.running = False

        if isinstance(event, UpdateEvent):
            self.update(event.board, event.moves, event.log)

        if isinstance(event, TickEvent):
            pass

    def set_color(self, color: str) -> None:
        """Set the player color"""
        self.color = color

    def get_color(self) -> str:
        """Return the player color"""
        return self.color

    def update(self, board: list, moves: list, move_log: list) -> None:
        """Update the client gamestate when socket sends new gamestate"""
        self.board = board
        self.move_log = move_log

        if self.color == "black":
            self.board = np.rot90(self.board, 2)  # type: ignore
            self.moves = list(map(self.invert_move, moves))
        else:
            self.moves = moves

    @typing.no_type_check
    def invert_move(self, move: str) -> str:
        """Invert black players click"""
        movetype = move[-1]
        if movetype in ("N", "T"):
            print(move)
            start_col, start_row, _, end_col, end_row, _, move_type = move

            start_col = str(abs(int(start_col) - 7))
            start_row = str(abs(int(start_row) - 7))
            end_col = str(abs(int(end_col) - 7))
            end_row = str(abs(int(end_row) - 7))

            return f"{start_col}{start_row}:{end_col}{end_row}:{move_type}"

        if movetype == "C":
            king_start, king_end, rook_start, rook_end, movetype = move.split(":")

            king_start_col, king_start_row = king_start
            king_end_col, king_end_row = king_end
            rook_start_col, rook_start_row = rook_start
            rook_end_col, rook_end_row = rook_end

            king_start_col = str(abs(int(king_start_col) - 7))
            king_start_row = str(abs(int(king_start_row) - 7))

            king_end_col = str(abs(int(king_end_col) - 7))
            king_end_row = str(abs(int(king_end_row) - 7))

            rook_start_col = str(abs(int(rook_start_col) - 7))
            rook_start_row = str(abs(int(rook_start_row) - 7))

            rook_end_col = str(abs(int(rook_end_col) - 7))
            rook_end_row = str(abs(int(rook_end_row) - 7))

            return f"{king_start_col}{king_start_row}:{king_end_col}{king_end_row}:{rook_start_col}{rook_start_row}:{rook_end_col}{rook_end_row}:{movetype}"

    def run(self) -> None:
        """Starts the game engine loop"""
        self.running = True
        while self.running:
            new_tick = TickEvent()
            self.ev_manager.post(new_tick)

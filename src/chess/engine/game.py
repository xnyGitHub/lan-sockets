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
        new_string: str = ""
        for letter in move:
            if letter.isdigit():
                inverse = str(abs(int(letter) - 7))
                new_string += inverse
            else:
                new_string += letter
        return new_string

    def run(self) -> None:
        """Starts the game engine loop"""
        self.running = True
        while self.running:
            new_tick = TickEvent()
            self.ev_manager.post(new_tick)

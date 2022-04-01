"""Controller class for Player MVC"""  # pylint: disable=no-member,unbalanced-tuple-unpacking
import os
from typing import Callable
import typing
import json
import pygame
from src.chess.engine.event import Event, EventManager, Highlight, QuitEvent, TickEvent
from src.chess.engine.game import GameEngine


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


class Controller:
    """Controller class"""

    def __init__(self, event_manager: EventManager, model: GameEngine, send_to_server: Callable) -> None:
        self.event_manager = event_manager
        event_manager.register_listener(self)
        self.model: GameEngine = model
        self.send_to_server: Callable = send_to_server
        self.square_selected: tuple = ()
        self.player_clicks: list = []

    def unregister(self) -> None:
        """Unregister the controller from the set of listeners"""
        self.event_manager.unregister_listener(self)

    def notify(self, event_type: Event) -> None:
        """Class listener"""
        if isinstance(event_type, TickEvent):
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.event_manager.post(QuitEvent())
                    self.leave_room()

                if event.type == pygame.USEREVENT + 1:
                    self.event_manager.post(QuitEvent())

                if event.type == pygame.MOUSEBUTTONDOWN:

                    col, row = pygame.mouse.get_pos()
                    col, row = int(col / 64), int(row / 64)

                    if self.square_selected == (col, row):
                        self.reset_click()
                        continue

                    self.square_selected = (col, row)
                    self.player_clicks.append(self.square_selected)
                    self.event_manager.post(Highlight((col, row)))

                    if len(self.player_clicks) == 2:
                        move = self.convert_click_to_str()

                        result = [valid_move for valid_move in self.model.moves if move in valid_move]
                        if result:
                            move = result[0]
                            if self.model.color == "black":
                                move = self.invert_move(move)
                            self.make_move(move)
                        self.reset_click()

    def make_move(self, move: str) -> None:
        """Make a move"""
        message = json.dumps(
            {"action": "game", "sub_action": "make_move", "payload": {"color": self.model.get_color(), "move": move}}
        )
        self.send_to_server(message)

    def leave_room(self) -> None:
        """Make a move"""
        message = json.dumps({"action": "leave_room", "sub_action": "leave"})
        self.send_to_server(message)

    def convert_click_to_str(self) -> str:
        """Convert player click tuple to xx:xx format"""
        (start_col, start_row), (end_col, end_row) = self.player_clicks
        move = f"{start_col}{start_row}:{end_col}{end_row}"
        return move

    @typing.no_type_check
    def invert_move(self, move: str) -> str:
        """Invert black players click"""
        movetype = move[-1]
        if movetype in ("N", "T"):
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

    def reset_click(self) -> None:
        """Reset the click variables"""
        self.square_selected = ()
        self.player_clicks = []
        self.event_manager.post(Highlight((None, None)))

"""Controller class for Player MVC"""  # pylint: disable=no-member,unbalanced-tuple-unpacking
import os
from typing import Callable
import pygame
from src.chess.engine.event import Event, EventManager, Highlight, QuitEvent, TickEvent
from src.chess.engine.game import GameEngine

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"


class Controller:
    """Controller class"""

    def __init__(self, event_manager: EventManager, model: GameEngine, callback_send: Callable):
        self.event_manager = event_manager
        event_manager.register_listener(self)
        self.model: GameEngine = model
        self.callback_send: Callable = callback_send
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

                        if move in self.model.moves:
                            self.callback_send(move)
                        self.reset_click()

    def convert_click_to_str(self) -> str:
        """Convert player click tuple to xx:xx format"""
        (start_col, start_row), (end_col, end_row) = self.player_clicks
        move = f"{start_col}{start_row}:{end_col}{end_row}"
        return move

    def reset_click(self) -> None:
        """Reset the click variables"""
        self.square_selected: tuple = ()
        self.player_clicks: list = []
        self.event_manager.post(Highlight((None, None)))

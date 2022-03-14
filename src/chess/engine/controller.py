import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from src.chess.engine.event import (Event, EventManager, QuitEvent, TickEvent)
from src.chess.engine.game import GameEngine


class Controller:

    def __init__(self, ev_manager: EventManager, model: GameEngine):
        self.ev_manager = ev_manager
        ev_manager.register_listener(self)
        self.model: GameEngine = model

    def unregister(self) -> None:
        """Unregister the controller from the set of listeners"""
        self.ev_manager.unregister_listener(self)

    def notify(self,event_type: Event):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ev_manager.post(QuitEvent())
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass

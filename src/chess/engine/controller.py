import os
import json
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from src.chess.engine.event import (Event, EventManager, QuitEvent, TickEvent, Highlight)
from src.chess.engine.game import GameEngine


class Controller:

    def __init__(self, ev_manager: EventManager, model: GameEngine, socket):
        self.ev_manager = ev_manager
        ev_manager.register_listener(self)
        self.model: GameEngine = model
        self.socket_send = socket
        self.square_selected: tuple = ()
        self.player_clicks: list = []

    def unregister(self) -> None:
        """Unregister the controller from the set of listeners"""
        self.ev_manager.unregister_listener(self)

    def notify(self,event:Event):
        if isinstance(event, TickEvent):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.ev_manager.post(QuitEvent())

                if event.type == pygame.MOUSEBUTTONDOWN:

                    col, row = pygame.mouse.get_pos()
                    col, row = int(col/64), int(row/64)

                    if self.square_selected == (col,row):
                        self.reset_click()
                        continue

                    self.square_selected = (col,row)
                    self.player_clicks.append(self.square_selected)
                    self.ev_manager.post(Highlight((col,row)))

                    if len(self.player_clicks) == 2:
                        (sc, sr),(ec, er) = self.player_clicks
                        move = f'{sc}{sr}:{ec}{er}'
                        if move in self.model.moves:
                            self.socket_send(move)
                        self.reset_click()

    def reset_click(self):
        self.square_selected: tuple = ()
        self.player_clicks: list = []
        self.ev_manager.post(Highlight((None,None)))


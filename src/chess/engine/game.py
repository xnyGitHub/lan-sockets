from src.chess.engine.event import EventManager, QuitEvent, TickEvent, UpdateEvent, Event
class GameEngine:
    """Holds the game state."""

    def __init__(self, ev_manager: EventManager):
        """Create new gamestate"""
        self.ev_manager: EventManager = ev_manager
        ev_manager.register_listener(self)
        self.running: bool = False

        """Default board constructor"""
        self.board: list =[
                ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
                ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["--", "--", "--", "--", "--", "--", "--", "--"],
                ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bB"],
            ]
    def notify(self, event: Event) -> None:
        """Notify"""
        if isinstance(event, QuitEvent):
            self.running = False
        if isinstance(event, UpdateEvent):
           pass
        if isinstance(event, TickEvent):
           pass

    def run(self) -> None:
        """Starts the game engine loop"""
        self.running = True
        while self.running:
            new_tick = TickEvent()
            self.ev_manager.post(new_tick)
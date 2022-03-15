from src.chess.engine.event import EventManager, QuitEvent, TickEvent, UpdateEvent, Event
class GameEngine:
    """Holds the game state."""

    def __init__(self, ev_manager: EventManager):
        """Create new gamestate"""
        self.ev_manager: EventManager = ev_manager
        ev_manager.register_listener(self)
        self.running: bool = False
        self.moves = []
        self.move_log = []

        """Default board constructor"""
        self.board: list =[
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
            board = event.board
            moves = event.moves
            log = event.log
            self.update(board,moves,log)
        if isinstance(event, TickEvent):
           pass

    def update(self,board,moves, move_log):
        self.board = board
        self.moves = moves
        self.move_log = move_log

    def run(self) -> None:
        """Starts the game engine loop"""
        self.running = True
        while self.running:
            new_tick = TickEvent()
            self.ev_manager.post(new_tick)
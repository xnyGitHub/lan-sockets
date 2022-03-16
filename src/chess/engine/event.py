"""Event manager class for MVC"""  # pylint: disable=too-few-public-methods


class Event:
    """Generic event"""


class TickEvent(Event):
    """Tick event"""


class UpdateEvent(Event):
    """Used to update client side board"""

    def __init__(self, board: list, moves: list, log: list):
        self.board: list = board
        self.moves: list = moves
        self.log: list = log


class Highlight(Event):
    """Highlight user square click"""

    def __init__(self, square: tuple):
        self.square: tuple = square


class QuitEvent(Event):
    """Quit Event"""


class EventManager:
    """The Coordinator"""

    def __init__(self):
        """Constructor"""

        from weakref import WeakKeyDictionary

        self.listeners: WeakKeyDictionary = WeakKeyDictionary()

    def register_listener(self, listener: object) -> None:
        """Register a listener to listen for events"""
        self.listeners[listener] = 1

    def unregister_listener(self, listener: object) -> None:
        """Remove a listener"""
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event: Event) -> None:
        """Function that notifies all listers of new event"""
        for listener in self.listeners.keys():
            # NOTE: If the weakref has died, it will be
            # automatically removed, so we don't have
            # to worry about it.
            listener.notify(event)

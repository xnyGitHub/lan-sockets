class Event:
    pass

class TickEvent(Event):
    pass

class UpdateEvent(Event):

    def __init__(self,board,moves,log):
        self.board = board
        self.moves = moves
        self.log = log

class Highlight(Event):
    def __init__(self,square):
        self.square = square

class QuitEvent(Event):
    pass


class EventManager:
    """The Coordinator"""

    def __init__(self):
        """Constructor"""

        from weakref import WeakKeyDictionary
        self.listeners: WeakKeyDictionary = WeakKeyDictionary()

    def register_listener(self, listener: object):
        """Register a listener to listen for events"""
        self.listeners[listener] = 1

    def unregister_listener(self, listener: object):
        """Remove a listener"""
        if listener in self.listeners.keys():
            del self.listeners[listener]

    def post(self, event: Event):
        """Function that notifies all listers of new event"""
        for listener in self.listeners.keys():
            # NOTE: If the weakref has died, it will be
            # automatically removed, so we don't have
            # to worry about it.
            listener.notify(event)
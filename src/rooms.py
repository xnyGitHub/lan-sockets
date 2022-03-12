from src.game import GameEngine
from src.utils import Singleton

# ---------------------------------------------
@Singleton
class Room:
    def __init__(self):
        self.game_rooms = {}

    def create_room(self, room_name):
        if room_name not in self.game_rooms:
            self.game_rooms[room_name] = GameEngine()
            return self.game_rooms[room_name]
        raise RoomNameExists()

    def get_room(self, room_id):
        if room_id in self.game_rooms:
            return self.game_rooms[room_id]
        raise RoomNotFound()

    def del_room(self, room_id):
        del self.game_rooms[room_id]

# ---------------------------------------------

class Rooms:

    CAPACITY = 2

    def __init__(self, room_name):
        self.room_name = room_name
        self.game = GameEngine()
        self.players = []
        self.spectators = []

    def join(self, player):
        if not self.is_full():
            self.players.append(player)
        raise RoomFull()

    def spectate(self, player):
        self.spectators.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

        if player in self.spectators:
            self.spectators.remove(player)

    def reset_game(self):
        self.game.reset

    def is_full(self):
        if len(self.players) == Rooms.CAPACITY:
            return True
        return False

class RoomFull(Exception):
    pass


class RoomNotFound(Exception):
    pass


class RoomNameExists(Exception):
    pass

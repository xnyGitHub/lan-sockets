from src.game import GameEngine
from src.utils import Singleton
import socket
import json
# ---------------------------------------------
@Singleton
class Room:
    def __init__(self):
        self.game_rooms = {}

    def create_room(self, room_name):
        if room_name in self.game_rooms:
            raise RoomNameAlreadyTaken()
        self.game_rooms[room_name] = Rooms(room_name)

    def join(self,room_name):
        if room_name not in self.game_rooms:
            raise RoomNotFound()

        if self.game_rooms[room_name].is_full():
            raise RoomFull()

        return self.game_rooms[room_name]

    def spectate(self,room_name):
        if room_name not in self.game_rooms:
            raise RoomNotFound()

        return self.game_rooms[room_name]

    def get_all_rooms(self):
        if not self.game_rooms:
            return "No Room created"
        return list(self.game_rooms.keys())

    def del_room(self, room_id):
        del self.game_rooms[room_id]

# ---------------------------------------------

class Rooms:

    CAPACITY = 2
    clients:dict= {
        "1": None,
        "2": None,
    }

    def __init__(self, room_name):
        self.room_name = room_name
        self.game = GameEngine()
        self.players = []
        self.spectators = []

    def join(self, player: socket.socket):
        message = ''
        if self.is_full():
            raise RoomFull()
        self.players.append(player)


        if Rooms.clients.get("1") is None:
            Rooms.clients['1'] = player
            message = json.dumps({"action": "id", "payload": '1'})
        else:
            Rooms.clients['2'] = player
            message = json.dumps({"action": "id", "payload": '2'})

        player.send((message+ '\0').encode())

    def spectate(self, player):
        self.spectators.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

        if player in self.spectators:
            self.spectators.remove(player)

    def service_data(self, data:dict):
        pass

    def is_full(self):
        if len(self.players) == Rooms.CAPACITY:
            return True
        return False

class RoomFull(Exception):
    pass


class RoomNotFound(Exception):
    pass


class RoomNameAlreadyTaken(Exception):
    pass

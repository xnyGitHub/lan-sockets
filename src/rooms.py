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

    MAX_SPECTATORS: int = 2


    def __init__(self, room_name: str, max_spectator:int = None):
        self.room_name:str = room_name
        self.clients:dict = {
            "white": None,
            "black": None
            }
        self.game = None
        self.players:list = []
        self.spectators:list = []
        self.player_turn: str = "white"

        if max_spectator is not None:
            self.MAX_SPECTATORS = max_spectator

    def join(self, player: socket.socket):

        if self.is_full():
            raise RoomFull()
        self.players.append(player)

        message = ''
        if self.clients.get("white") is None:
            self.clients['white'] = player
            message = json.dumps({"action": "id", "payload": 'white'})
        else:
            self.clients['black'] = player
            message = json.dumps({"action": "id", "payload": 'black'})

        player.send((message+ '\0').encode())


        if self.is_full():
            self.game = GameEngine()
            for player in self.clients.values():
                message = json.dumps({"action": "game", "sub_action": 'start'})
                player.send((message+ '\0').encode())
            self.send_players_gamestate()

    def send_players_gamestate(self):
        message = {
            "action": "game",
            "sub_action": "update",
            "payload": {"board": self.game.get_board().tolist(),"moves": '',"move_log": self.game.get_move_log()}
            }

        for color, socket in self.clients.items():
            if color == "black":
                message['payload']['moves'] = self.game.get_black_moves()
            if color == "white":
                message['payload']['moves'] = self.game.get_white_moves()

            dumped = json.dumps(message)
            socket.send((dumped + '\0').encode())

    def spectate(self, player):
        self.spectators.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

        if player in self.spectators:
            self.spectators.remove(player)

    def service_data(self, data: dict):
        if data['sub_action'] == 'make_move':
            color = data['payload']['color']
            move  = data['payload']['move']
            if color == self.player_turn:
                self.game.make_move(move)
                self.switch_turns()
            else:
                socket = self.clients.get(color)
                message = json.dumps({"action": "message", "payload": "'It's not your turn"})
                socket.send((message + '\0').encode())




        if data['sub_action'] == 'undo_move':
            self.game.undo_move()

        self.send_players_gamestate()

    def is_full(self):
        if len(self.players) == 2:
            return True
        return False

    def switch_turns(self):
        if self.player_turn == 'black':
            self.player_turn = 'white'
        elif self.player_turn == 'white':
            self.player_turn = 'black'

class RoomFull(Exception):
    pass


class RoomNotFound(Exception):
    pass


class RoomNameAlreadyTaken(Exception):
    pass

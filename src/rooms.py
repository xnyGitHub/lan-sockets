"""Server rooms and room module"""
import socket
import json
import time
from typing import Dict, Optional
from src.game import GameEngine
from src.utils import Singleton


@Singleton
class Room:
    """
    Room class, this object holds an array of rooms objects
    and acts as a bridge allowing the user to join these rooms
    """

    def __init__(self) -> None:
        self.game_rooms: Dict[str, "Rooms"] = {}

    def create_room(self, room_name: str, room_creator: str) -> None:
        """Creates a room"""
        if room_name in self.game_rooms:
            raise RoomNameAlreadyTaken()
        self.game_rooms[room_name] = Rooms(room_name, room_creator, Room.instance())  # type: ignore

    def join(self, room_name: str, player_address: socket.socket, username: str) -> "Rooms":
        """Join a room as a player"""
        if room_name not in self.game_rooms:
            raise RoomNotFound()

        if self.game_rooms[room_name].is_full():
            raise RoomFull()

        self.game_rooms[room_name].join(player_address, username)
        return self.game_rooms[room_name]

    def get_all_rooms(self) -> list:
        """Get a list of all the rooms created"""
        room_list: list = []
        if not self.game_rooms:
            return room_list


        for room_name, room_object in self.game_rooms.items():
            room_list.append((room_name, room_object.get_creator(), room_object.get_players()))
        return room_list

    def del_room(self, room_id: str) -> None:
        """Delete a room"""
        del self.game_rooms[room_id]


# ---------------------------------------------


class Rooms:
    """
    The actual room where the clients can player.
    This rooms holds the GameEngine object and services the data sent by the user
    """

    def __init__(self, room_name: str, room_creator: str, rooms: Room) -> None:
        self.room_name: str = room_name
        self.room_creator: str = room_creator
        self.server_rooms: Room = rooms
        self.clients: dict = {"white": None, "black": None}
        self.usernames: dict = {"white": None, "black": None}
        self.game: Optional[GameEngine] = None
        self.player_turn: str = "white"
        self.player_ready = 0

    def join(self, player_address: socket.socket, username: str) -> None:
        """Join the room"""

        # Assign player ID
        if self.clients.get("white") is None:
            self.clients["white"] = player_address
            self.usernames["white"] = username
        else:
            self.clients["black"] = player_address
            self.usernames["black"] = username

    def leave(self, player_address: socket.socket) -> None:
        """Remove a player from a room"""

        for color, client_address in dict(self.clients).items():

            # Remove player that wants to leave
            if player_address == client_address:
                self.clients[color] = None
                self.usernames[color] = None
                self.player_ready -= 1

            # Remove other player if game in progress
            if player_address != client_address and self.is_game_running():
                self.clients[color] = None
                self.usernames[color] = None
                message = json.dumps({"action": "message", "payload": "You win!"})
                client_address.send((message).encode())
                self.delete_room()

    def start_game(self) -> None:
        """Start the game with two players join"""
        self.game = GameEngine()

        # Send them a start payload which will be used to invoke pygame for the player
        for color, address in self.clients.items():
            message = json.dumps({"action": "start_game", "payload": color})
            address.send((message).encode())

    def is_game_running(self) -> bool:
        """Check if the game enigne object has been created"""
        if self.game is None:
            return False
        return True

    def send_players_gamestate(self) -> None:
        """Send the players the new gamestate when a move is made"""

        # JSON payload sent to play to update their board

        new_board = self.game.get_board().tolist()  # type: ignore
        message: dict = {
            "action": "update",
            "payload": {"board": new_board, "moves": "", "move_log": self.game.get_move_log()},
        }

        # Get the correct moves for the correct player
        for color, player in self.clients.items():
            if color == "black":
                message["payload"]["moves"] = self.game.get_black_moves()
            if color == "white":
                message["payload"]["moves"] = self.game.get_white_moves()

            dumped = json.dumps(message)
            player.send((dumped).encode())

    def service_data(self, data: dict) -> None:
        """Service the data sent by the players"""
        if data["sub_action"] == "make_move":

            color = data["payload"]["color"]
            move = data["payload"]["move"]

            if color == self.player_turn:
                self.game.make_move(move)
                self.game.get_moves()
                self.switch_turns()
            else:
                player_address = self.clients[color]
                message = json.dumps({"action": "message", "payload": "'It's not your turn"})
                player_address.send((message).encode())
                return

        elif data["sub_action"] == "undo_move":
            self.game.undo_move()

        elif data["sub_action"] == "waiting":
            self.player_ready += 1
            if self.player_ready == 2:
                self.start_game()
                time.sleep(1)
            else:
                return

        self.send_players_gamestate()

    def is_full(self) -> bool:
        """Check if room is full"""
        if None in self.clients.values():
            return False
        return True

    def get_creator(self) -> str:
        """Return creator of room username"""
        return self.room_creator

    def get_players(self) -> dict:
        """Return player usernames"""
        return self.usernames

    def switch_turns(self) -> None:
        """Switch the player turns after a move"""
        if self.player_turn == "black":
            self.player_turn = "white"
        elif self.player_turn == "white":
            self.player_turn = "black"

    def delete_room(self) -> None:
        """Delete the room"""
        self.server_rooms.del_room(self.room_name)


class RoomFull(Exception):
    """If room is full"""


class RoomNotFound(Exception):
    """If room is not found when joining"""


class RoomNameAlreadyTaken(Exception):
    """If room is already name is already taken when creating"""

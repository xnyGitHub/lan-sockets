"""Server rooms and room module"""
import socket
import json
from typing import Dict, List, Union
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

    def create_room(self, room_name: str) -> None:
        """Creates a room"""
        if room_name in self.game_rooms:
            raise RoomNameAlreadyTaken()
        self.game_rooms[room_name] = Rooms(room_name, Room.instance())  # type: ignore

    def join(self, room_name: str) -> "Rooms":
        """Join a room as a player"""
        if room_name not in self.game_rooms:
            raise RoomNotFound()

        if self.game_rooms[room_name].is_full():
            raise RoomFull()

        return self.game_rooms[room_name]

    def get_all_rooms(self) -> Union[List[str], str]:
        """Get a list of all the rooms created"""
        if not self.game_rooms:
            return "No Room created"
        return list(self.game_rooms.keys())

    def del_room(self, room_id: str) -> None:
        """Delete a room"""
        del self.game_rooms[room_id]


# ---------------------------------------------


class Rooms:
    """
    The actual room where the clients can player.
    This rooms holds the GameEngine object and services the data sent by the user
    """

    def __init__(self, room_name: str, rooms: Room) -> None:
        self.room_name: str = room_name
        self.server_rooms: Room = rooms
        self.clients: dict = {"white": None, "black": None}
        self.game: GameEngine
        self.game_in_progress: bool = False
        self.players: list = []
        self.player_turn: str = "white"

    def join(self, player_address: socket.socket) -> None:
        """Join the room"""

        # Check if room is full
        if self.is_full():
            raise RoomFull()

        # Add player if room is not full
        self.players.append(player_address)

        # Assign player ID and send it to them
        message = ""
        if self.clients.get("white") is None:
            self.clients["white"] = player_address
            message = json.dumps({"action": "id", "payload": "white"})
        else:
            self.clients["black"] = player_address
            message = json.dumps({"action": "id", "payload": "black"})

        player_address.send((message + "\0").encode())

        # Start game if two players have connected
        if self.is_full():
            self.start_game()
            self.send_players_gamestate()

    def start_game(self) -> None:
        """Start the game with two players join"""
        self.game_in_progress = True
        self.game = GameEngine()

        # Send them a start payload which will be used to invoke pygame for the player
        for address in self.clients.values():
            message = json.dumps({"action": "game", "sub_action": "start"})
            address.send((message + "\0").encode())

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
            "action": "game",
            "sub_action": "update",
            "payload": {"board": new_board, "moves": "", "move_log": self.game.get_move_log()},
        }

        # Get the correct moves for the correct player
        for color, player in self.clients.items():
            if color == "black":
                message["payload"]["moves"] = self.game.get_black_moves()
            if color == "white":
                message["payload"]["moves"] = self.game.get_white_moves()

            dumped = json.dumps(message)
            player.send((dumped + "\0").encode())

    def leave(self, player_address: socket.socket) -> None:
        """Remove a player from a room"""
        # Check if the play is in list of players
        if player_address in self.players:
            self.players.remove(player_address)

            # Remove both players from client dictionary
            for color, client_address in dict(self.clients).items():
                if player_address == client_address:
                    del self.clients[color]

                if player_address != client_address and self.game_in_progress:
                    self.game_in_progress = False
                    message = json.dumps({"action": "message", "payload": "You win!"})
                    client_address.send((message + "\0").encode())
                    self.delete_room()

    def service_data(self, data: dict) -> None:
        """Service the data sent by the players"""
        if data["sub_action"] == "make_move":
            color = data["payload"]["color"]
            move = data["payload"]["move"]
            if color == self.player_turn:
                self.game.make_move(move)
                self.switch_turns()
            else:
                player_address = self.clients[color]
                message = json.dumps({"action": "message", "payload": "'It's not your turn"})
                player_address.send((message + "\0").encode())

        if data["sub_action"] == "undo_move":
            self.game.undo_move()

        self.send_players_gamestate()

    def is_full(self) -> bool:
        """Check if room is full"""
        if len(self.players) == 2:
            return True
        return False

    def switch_turns(self) -> None:
        """Switch the player turns after a move"""
        if self.player_turn == "black":
            self.player_turn = "white"
        elif self.player_turn == "white":
            self.player_turn = "black"

    def delete_room(self) -> None:
        self.server_rooms.del_room(self.room_name)


class RoomFull(Exception):
    """If room is full"""


class RoomNotFound(Exception):
    """If room is not found when joining"""


class RoomNameAlreadyTaken(Exception):
    """If room is already name is already taken when creating"""

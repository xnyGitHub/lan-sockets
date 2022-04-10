"""Player module"""  # pylint: disable =no-self-use,redefined-builtin
import select
import signal
import socket
import sys
import threading
import time
from typing import Union
import json

from src.chess.engine.controller import Controller
from src.chess.engine.event import EventManager, ThreadQuitEvent, UpdateEvent, ViewUpdate
from src.chess.engine.game import GameEngine
from src.chess.engine.view import View
from src.utils import ctrlc_handler, flush_print_default, socket_recv_errors

print = flush_print_default(print)
# socket.socket.recv = socket_recv_errors(socket.socket.recv)


class Player:
    """Player class"""

    def __init__(self, host: str, port: int) -> None:
        # Connect to socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(host, port)
        self.exit: bool = False

        # Pygame related
        self.event: threading.Event
        self.event_manager: EventManager
        self.gamemodel: GameEngine
        self.controller: Controller
        self.graphics: View

    def connect(self, host: str, port: int) -> None:
        """Connect to socket"""
        try:
            self.socket.connect((host, port))

            user_input = input("Please enter your username: ")
            message = json.dumps({"action": "username", "payload": user_input})
            self.send(message)

            data = self.socket.recv(1024)
            if not data:
                sys.exit(0)

        except ConnectionRefusedError:
            print("Could not connect")
            sys.exit(0)
        except KeyboardInterrupt:
            print("Disconnecting")
            sys.exit(0)

    def initialise_pygame(self) -> None:
        """Initialise the MVC model for pygame and run it"""
        self.event_manager = EventManager()
        self.gamemodel = GameEngine(self.event_manager)
        self.controller = Controller(self.event_manager, self.gamemodel, self.send)
        self.graphics = View(self.event_manager, self.gamemodel)

    def send(self, message: str) -> None:
        """Send message to socket"""
        self.socket.sendall((message).encode())

    def sleep(self, sec: Union[int, float]) -> None:
        """Zzz"""
        time.sleep(sec)

    def recieve(self) -> None:
        """Socket listener function"""
        while not self.event.is_set():
            try:
                readable, _, _ = select.select([self.socket], [], [], 2)
            except OSError:
                pass
            for obj in readable:
                if obj is self.socket:

                    data = self.socket.recv(4096)
                    if not data:
                        self.exit = True
                        self.event_manager.post(ThreadQuitEvent())
                        self.event.set()
                        print("Server shutdown")
                        break

                    message = json.loads(data)
                    self.service_data(message)

    def service_data(self, data: dict) -> None:
        """Service the data sent from the server"""

        if "update" in data.values():
            board = data["payload"]["board"]
            move = data["payload"]["moves"]
            log = data["payload"]["move_log"]
            gamestate = data["payload"]["gamestate"]
            captured = data["payload"]["captured"]
            check_status = data["payload"]["check_status"]
            self.event_manager.post(UpdateEvent(board, move, log, captured, gamestate))
            self.event_manager.post(ViewUpdate(check_status))

        elif "message" in data.values():
            if data["payload"] == "You win!":
                self.event_manager.post(ThreadQuitEvent())
                print(data["payload"])
            else:
                print(data["payload"])

        elif "success" in data:
            pass

    def create_room(self, room_name: str) -> None:
        """Create a room with user input as name"""
        message = json.dumps({"action": "create", "payload": room_name})
        self.send(message)

        data = self.socket.recv(1024)
        if not data:
            print("Server no longer online, the client will now exit")
            self.exit = True
            return

        response = json.loads(data)
        response_message = response["payload"]
        print(response_message)

    def join_room(self, room_name: str) -> None:
        """Join a room"""
        message = json.dumps({"action": "join", "payload": room_name})
        self.send(message)

        # Response is handeled in main menu.
        # DO NOT HANDLE HERE. PROGRAM WILL HANG

    def leave_room(self) -> None:
        """Leave the room"""
        message = json.dumps({"action": "leave_room"})
        self.send(message)

        data = self.socket.recv(1024)
        if not data:
            print("Server no longer online, the client will now exit")
            self.exit = True
            return

        response = json.loads(data)
        response_message = response["payload"]
        print(response_message)

    def get_rooms(self) -> None:
        """Get a list of all room"""
        message = json.dumps({"action": "get_rooms"})
        self.send(message)

        data = self.socket.recv(1024)
        if not data:
            print("Server no longer online, the client will now exit")
            self.exit = True
            return

        response = json.loads(data)
        response_message = response["payload"]

        if not response_message:
            print("No rooms have been created yet")
            return

        for room_name, creator, players in response_message:
            print(
                f"""
Room name: {room_name}
Creator: {creator}
White - {players['white']} | vs | {players['black']} - Black
"""
            )

    def waiting_for_opponent(self) -> None:
        """Tell the server you are waiting in the room for an opponent"""
        message = json.dumps({"action": "game", "sub_action": "waiting"})
        self.send(message)

        # No reponse from server

    def start_game(self, color: str, usernames: dict) -> None:
        """Start the game"""

        print(f"The game has started. You will play as {color}")

        # While loop condition for threaded recieve
        self.event = threading.Event()
        game_thread = threading.Thread(target=self.recieve)
        game_thread.start()

        # Start pygame
        self.initialise_pygame()
        self.gamemodel.set_color(color)
        self.gamemodel.set_players(usernames)
        self.gamemodel.run()
        # Stop the thread
        if not self.event.is_set():
            self.event.set()
        print("Game has concluded.")

    def start(self) -> None:
        """Start the server"""
        print("Connected to server")
        while not self.exit:
            choice = input(
                """------------------
| A: Create Room |
| B: List Rooms  |
| C: Join Room   |
| Q: Logout      |
------------------
Please enter your choice: """
            )

            if choice.upper() == "A":
                choice = str(input("Enter room name: "))
                self.create_room(choice)

            elif choice.upper() == "B":
                self.get_rooms()

            elif choice.upper() == "C":
                # Send the input
                choice = str(input("Enter room name: "))
                self.join_room(choice)

                # Wait for response
                data = self.socket.recv(1024)
                if not data:
                    print("Server no longer online, the client will now exit")
                    self.exit = True
                    break

                response = json.loads(data)
                # Do something
                if response["success"] is False:
                    print(response["payload"])

                if response["success"] is True:
                    print(response["payload"])

                    try:

                        print("Waiting for an opponent...\nHit Ctrl-C to leave room")
                        self.waiting_for_opponent()
                        waiting_in_lobby: bool = True

                        while True:
                            readable, _, _ = select.select([self.socket], [], [], 1)
                            if self.socket in readable and waiting_in_lobby:

                                data = self.socket.recv(1024)
                                if not data:
                                    print("Server has shutdown")
                                    self.exit = True
                                    break

                                response = json.loads(data)
                                if response["action"] == "start_game":
                                    waiting_in_lobby = False
                                    color = response["payload"]["color"]
                                    usernames = response["payload"]["username"]
                                    self.start_game(color, usernames)
                                    break

                    except KeyboardInterrupt:
                        self.leave_room()
                        continue

            elif choice.upper() == "Q":
                break
            else:
                print("Invalid option")

        print("Shutting down client...")
        # Let threads finish before closing socket
        self.sleep(2.5)
        self.socket.close()
        print("Disconnected!")


if __name__ == "__main__":
    HOST = ""
    PORT = 5555

    if sys.platform == "darwin":
        HOST = "192.168.0.60"
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # type: ignore

    if sys.platform == "win32":
        HOST = "192.168.0.13"

    HOST = input("Enter the server IP: ")

    player = Player(HOST, PORT)
    player.start()

"""Player module"""  # pylint: disable =no-self-use
import select
import signal
import socket
import sys
import threading
import time
from typing import Union
import json

from src.chess.engine.controller import Controller
from src.chess.engine.event import EventManager, ThreadQuitEvent, UpdateEvent
from src.chess.engine.game import GameEngine
from src.chess.engine.view import View
from src.utils import ctrlc_handler, flush_print_default

print = flush_print_default(print)


class Player:
    """Player class"""

    def __init__(self, host: str, port: int) -> None:
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(host, port)
        self.running: bool = True
        self.color: str = "None"
        self.initialised: bool = False
        self.event_manager: EventManager
        self.gamemodel: GameEngine
        self.controller: Controller
        self.graphics: View

    def connect(self, host: str, port: int) -> None:
        """Connect to socket"""
        try:
            self.socket.connect((host, port))
        except ConnectionRefusedError:
            print("Could not connect")
            sys.exit(0)
        self.connected = True

    def initialise_pygame(self) -> None:
        """Initialise the MVC model for pygame and run it"""
        self.event_manager = EventManager()
        self.gamemodel = GameEngine(self.event_manager)
        self.controller = Controller(self.event_manager, self.gamemodel, self.send)
        self.graphics = View(self.event_manager, self.gamemodel)
        self.initialised = True

    def send(self, message: str) -> None:
        """Send message to socket"""
        self.socket.sendall((message + "\0").encode())

    def sleep(self, sec: Union[int, float]) -> None:
        """Zzz"""
        time.sleep(sec)

    def recieve(self) -> None:
        """Socket listener function"""
        while self.connected:
            try:
                readable, _, _ = select.select([self.socket], [], [], 2)
            except OSError:
                pass
            for obj in readable:
                if obj is self.socket:

                    data = self.socket.recv(4096)
                    if not data:
                        print("\n------------- \nMax connections or Server shutdown")
                        self.connected = False
                        break

                    message: dict
                    strings = data.split(b"\0")
                    for msg in strings:
                        if msg != b"":
                            message = json.loads(msg)
                            self.service_data(message)

    def create_room(self, room_name: str) -> None:
        """Create a room with user input as name"""
        message = json.dumps({"action": "create", "payload": room_name})
        self.send(message)

    def join_room(self, room_name: str) -> None:
        """Join a room"""
        message = json.dumps({"action": "join", "payload": room_name})
        self.send(message)

    def get_rooms(self) -> None:
        """Get a list of all room"""
        message = json.dumps({"action": "get_rooms"})
        self.send(message)

    def undo_move(self) -> None:
        """Undo a move"""
        message = json.dumps({"action": "game", "sub_action": "undo_move"})
        self.send(message)

    def service_data(self, data: dict) -> None:
        """Service the data sent from the server"""
        if data["action"] == "id":
            self.color = data["payload"]
            print(f"You are playing as : {self.color}")

        if data["action"] == "game":
            if data["sub_action"] == "start":
                self.initialised = True
                self.sleep(1)

            if data["sub_action"] == "update":
                board, move, log = data["payload"].values()
                self.event_manager.post(UpdateEvent(board, move, log))

        if data["action"] == "message":
            if data["payload"] == "You win!":
                self.event_manager.post(ThreadQuitEvent())
                print(data["payload"])
            else:
                print(data["payload"])

    def start(self) -> None:
        """Start the server"""
        print("Connecting to server...")

        threading.Thread(target=self.recieve).start()

        self.sleep(1)
        if not self.connected:
            return

        menu_runing = False
        while self.running:
            if not menu_runing:
                threading.Thread(target=self.menu).start()
                menu_runing = True

            if self.initialised:
                self.initialise_pygame()
                self.gamemodel.set_color(self.color)
                self.gamemodel.run()
                self.initialised = False
                menu_runing = False

        print("Shutting down client...")
        self.connected = False
        self.sleep(2.5)  # Let threads finish before closing socket
        self.socket.close()
        print("Disconnected!")

    def menu(self) -> None:
        """Main menu"""
        while True:
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
                choice = str(input("Enter room name: "))
                self.join_room(choice)
                break
            elif choice.upper() == "Q":
                self.running = False
                break
            else:
                print("Invalid option")


if __name__ == "__main__":
    HOST = ""
    PORT = 5555

    if sys.platform == "darwin":
        HOST = "192.168.0.60"
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # Detect if  Ctrl+Z was pressed

    if sys.platform == "win32":
        HOST = "192.168.0.13"

    player = Player(HOST, PORT)
    player.start()

"""Player module"""
import queue
import select
import signal
import socket
import sys
import threading
import time
import json

from src.chess.engine.controller import Controller
from src.chess.engine.event import EventManager
from src.chess.engine.game import GameEngine
from src.chess.engine.view import View
from src.utils import ctrlc_handler, flush_print_default

print = flush_print_default(print)


class Player:
    """Player class"""

    def __init__(self, HOST, PORT):
        self.connected = False
        self.queue = queue.Queue(maxsize=10)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(HOST, PORT)
        self.event_manager = EventManager()
        self.game_id = None
        # self.initialise_pygame()

    def connect(self, host, port):
        """Connect to socket"""
        try:
            self.socket.connect((host, port))
        except ConnectionRefusedError:
            print("Could not connect")
            sys.exit(0)
        self.connected = True

    def initialise_pygame(self):
        self.event_manager = EventManager()
        self.gamemodel = GameEngine(self.event_manager)
        self.controller = Controller(self.event_manager, self.gamemodel)
        self.graphics = View(self.event_manager, self.gamemodel)

    def add_message_buffer(self, message):
        """Add message to queue buffer"""
        self.queue.put(message)

    def get_message_buffer(self):
        """Get oldest message from queue buffer"""
        if self.queue.empty():
            return None
        return self.queue.get()

    def send(self):
        """Send message to socket"""
        while self.connected:
            if message := self.get_message_buffer():
                self.socket.sendall((message+ '\0').encode())
                # self.sleep(0.25) # So the player doesn't send info too fast

    def sleep(self, sec):
        """Zzz"""
        time.sleep(sec)

    def recieve(self):
        """Socket listener function"""
        while self.connected:
            try:
                readable, _, _ = select.select([self.socket], [], [], 2)
            except OSError:
                pass
            for obj in readable:
                if obj is self.socket:
                    message = ''
                    data = self.socket.recv(4096)
                    if not data:
                        print("\n------------- \nMax connections or Server shutdown")
                        self.connected = False
                        break

                    strings = data.split(b'\0')
                    for msg in strings:
                        if msg != b'':
                            message = json.loads(msg)
                            self.service_data(message)
                            # print(f"Received {message}")

    def create_room(self,room_name):
        message = json.dumps({"action": "create", "payload": room_name})
        self.add_message_buffer(message)

    def join_room(self,room_name):
        message = json.dumps({"action": "join", "payload": room_name})
        self.add_message_buffer(message)

    def get_rooms(self):
        message = json.dumps({"action": "get_rooms"})
        self.add_message_buffer(message)

    def service_data(self,data):
        if data['action'] == 'id':
            self.game_id = data['payload']
            print(f"Assigned id: {self.game_id}")

        if data['action'] == 'game':
            payload = data['payload']
            board = payload['board']
            moves = payload['moves']
            print(board)
            print(moves)

        if data['action'] == 'message':
            print(data['payload'])

    def start(self):
        """Start the server"""
        print("Connecting to server...")

        threading.Thread(target=self.send).start()
        threading.Thread(target=self.recieve).start()

        self.sleep(1)
        if not self.connected:
            return
        print("Connected!")

        self.get_rooms()
        self.create_room("Room1")
        self.get_rooms()
        self.join_room("Room")
        self.join_room("Room1")

        try:
            while True:
                pass
            # self.gamemodel.run()
        except KeyboardInterrupt:
            pass

        print("Shutting down client...")
        self.connected = False
        self.sleep(2.5)  # Let threads finish before closing socket
        self.socket.close()
        print("Disconnected!")


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

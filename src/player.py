"""Player module"""
import queue
import select
import signal
import socket
import sys
import threading
import time

from src.chess.engine.controller import Controller
from src.chess.engine.event import EventManager
from src.chess.engine.game import GameEngine
from src.chess.engine.view import View
from src.utils import ctrlc_handler, flush_print_default

print = flush_print_default(print)

HOST = ""
PORT = 5555

if sys.platform == "darwin":
    HOST = "192.168.0.60"
    signal.signal(signal.SIGTSTP, ctrlc_handler)  # Detect if  Ctrl+Z was pressed

if sys.platform == "win32":
    import win32api
    HOST = "192.168.0.13"


class Player:
    """Player class"""

    def __init__(self):
        self.connected = False
        self.queue = queue.Queue(maxsize=2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id = self.connect(HOST, PORT)
        self.event_manager = EventManager()
        self.gamemodel = GameEngine(self.event_manager)
        self.controller = Controller(self.event_manager, self.gamemodel)
        self.graphics = View(self.event_manager, self.gamemodel)


    def connect(self, host, port):
        """Connect to socket"""
        self.socket.connect((host, port))
        self.connected = True
        return self.socket.recv(1024).decode()

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
                byte_string = str.encode(f"{self.player_id}:{message}")
                self.socket.sendall(byte_string)

    def recieve(self):
        """Socket listener function"""
        while self.connected:
            try:
                readable, _, _ = select.select([self.socket], [], [], 2)
            except OSError:
                pass
            for obj in readable:
                if obj is self.socket:

                    data = self.socket.recv(1024)
                    if not data:
                        print("\n------------- \nMax connections or Server shutdown - Closing socket...")
                        self.connected = False
                        break

                    print(f"Received {data}")

    def user_input(self):
        """User input thread"""
        while self.connected:
            message = input("")
            self.add_message_buffer(message=message)

    def start(self):
        """Start the server"""
        print("Connecting to server...")

        threading.Thread(target=self.send).start()
        threading.Thread(target=self.recieve).start()

        time.sleep(2)

        if self.connected:
            print("Connected")
            input_thread = threading.Thread(target=self.user_input, daemon=True)
            input_thread.start()
            try:
                while self.connected:
                    pygame_thread = threading.Thread(target=self.gamemodel.run)
                    pygame_thread.run()
            except KeyboardInterrupt:

                self.connected = False
                print("Shutting down client...")
        else:
            print("Could not connect")

        time.sleep(1)
        self.socket.close()
        # if sys.platform == "win32":
        #     win32api.TerminateProcess(-1, 0)
        sys.exit(0)


if __name__ == "__main__":
    player = Player()
    player.start()

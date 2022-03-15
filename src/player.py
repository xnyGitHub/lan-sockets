"""Player module"""
import queue
import select
import signal
import socket
import sys
import threading
import time
import json
import pygame

from src.chess.engine.controller import Controller
from src.chess.engine.event import EventManager, UpdateEvent
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
        self.color = None

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
        self.controller = Controller(self.event_manager, self.gamemodel, self.make_move)
        self.graphics = View(self.event_manager, self.gamemodel)
        self.gamemodel.run()

    def send(self,message):
        """Send message to socket"""
        self.socket.sendall((message+ '\0').encode())

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

                    data = self.socket.recv(4096)
                    if not data:
                        print("\n------------- \nMax connections or Server shutdown")
                        self.connected = False
                        break

                    message = ''
                    strings = data.split(b'\0')
                    for msg in strings:
                        if msg != b'':
                            message = json.loads(msg)
                            self.service_data(message)

    def create_room(self,room_name):
        message = json.dumps({"action": "create", "payload": room_name})
        self.send(message)

    def join_room(self,room_name):
        message = json.dumps({"action": "join", "payload": room_name})
        self.send(message)

    def get_rooms(self):
        message = json.dumps({"action": "get_rooms"})
        self.send(message)

    def make_move(self, move):
        message = json.dumps({"action"    : "game",
                              "sub_action":"make_move",
                              "payload"   :
                                  {
                                  "color" : self.color,
                                  "move"  : move
                                  }
                              })
        self.send(message)

    def undo_move(self):
        message = json.dumps({"action": "game","sub_action":"undo_move"})
        self.send(message)

    def service_data(self,data):
        if data['action'] == 'id':
            self.color = data['payload']
            print(f"You are playing as : {self.color}")

        if data['action'] == 'game':
            # if data['sub_action'] == 'start':
            #     threading.Thread(target=self.initialise_pygame).start()

            if data['sub_action'] == 'update':
                board, move, log = data['payload'].values()
                self.event_manager.post(UpdateEvent(board,move,log))

        if data['action'] == 'message':
            print(data['payload'])

    def start(self):
        """Start the server"""
        print("Connecting to server...")

        threading.Thread(target=self.recieve).start()

        self.sleep(1)
        if not self.connected:
            return
        print("Connected!")

        self.create_room("Room1")
        self.join_room("Room1")

        try:
            self.initialise_pygame()
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

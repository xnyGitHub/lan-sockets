from re import L
import threading
import select
import json
from src.rooms import Room, RoomNotFound, RoomNameAlreadyTaken, RoomFull


class ThreadedClient(threading.Thread):
    """Threadclient class for each client that connects"""

    clients = {
        "1": None,
        "2": None,
    }

    def __init__(self, client, room):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.client = client
        self.client_id = self.get_id()
        self.server_room: Room = room
        self.game_room = None

        self.client.send(str.encode(self.client_id))
        ThreadedClient.clients[self.client_id] = self.client

    def run(self):
        print(f"{self.client_id}:{self.client.getsockname()[0]} has connected")
        while not self.event.is_set():
            readable, _, _ = select.select([self.client], [], [], 2)
            for obj in readable:
                if obj is self.client:
                    data = self.client.recv(1024)
                    if not data:
                        self.set_event()
                        break

                    try:
                        data = json.loads(data)
                        self.service_data(data)
                    except Exception as e:
                        raise(e)

        print(f"{self.client.getsockname()[0]} has disconnected")
        ThreadedClient.clients[self.client_id] = None

    def service_data(self, data):

        message = {}

        if data['action'] == 'create':
            payload = data['payload']
            try:
                self.server_room.create_room(payload)
                message['message']= f'{payload} created'
            except RoomNameAlreadyTaken:
                message['message'] = 'Error: Room name is already taken'

        if data['action'] == 'join':
            payload = data['payload']
            try:
                self.game_room = self.server_room.join(payload)
                message['message']= f'Joined {payload}'
            except RoomNotFound:
                message['message']= 'Error: Room not found'
            except RoomFull:
                message['message']= 'Error: Room is full'

        if data['action'] == 'get_rooms':
            message['message'] = self.server_room.get_all_rooms()
            print(message['message'])

        self.client.send(json.dumps(message).encode())

    def get_id(self):
        """Return an ID for the client"""
        if ThreadedClient.clients.get("1") is None:
            return "1"
        return "2"

    def set_event(self):
        """Stop the thread"""
        self.event.set()


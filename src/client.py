"""Threaded client module"""
import json
import select
import socket
import threading

from src.rooms import Room, RoomFull, RoomNameAlreadyTaken, RoomNotFound, Rooms


class ThreadedClient(threading.Thread):
    """Threadclient class for each client that connects"""

    def __init__(self, client: socket.socket, room: Room) -> None:
        threading.Thread.__init__(self)
        self.event: threading.Event = threading.Event()
        self.client: socket.socket = client
        self.server_room: Room = room
        self.game_room: Rooms

    def run(self) -> None:
        """Main function for threaded client"""
        print(f"{self.client.getsockname()[0]} has connected")
        while not self.event.is_set():
            readable, _, _ = select.select([self.client], [], [], 2)
            for obj in readable:
                if obj is self.client:
                    data = self.client.recv(4096)
                    if not data:
                        self.set_event()
                        break

                    strings = data.split(b"\0")
                    for msg in strings:
                        if msg != b"":
                            message = json.loads(msg)
                            self.service_data(message)

        print(f"{self.client.getsockname()[0]} has disconnected")

    def service_data(self, data: dict) -> None:
        """Parse the user data and service it accordingly"""
        message: dict = {"action": "message", "payload": ""}

        if data["action"] == "create":
            payload = data["payload"]
            try:
                self.server_room.create_room(payload)
                message["payload"] = f"{payload} created"
            except RoomNameAlreadyTaken:
                message["payload"] = "Error: Room name is already taken"

        if data["action"] == "join":
            payload = data["payload"]
            try:
                self.game_room = self.server_room.join(payload,self.client)
                message["payload"] = f"Joined {payload}"
            except RoomNotFound:
                message["payload"] = "Error: Room not found"
            except RoomFull:
                message["payload"] = "Error: Room is full"

        if data["action"] == "get_rooms":
            message["payload"] = self.server_room.get_all_rooms()

        if data["action"] == "leave_room":
            if self.game_room is None:
                message["payload"] = "You aren't in a room"
            else:
                self.game_room.leave(self.client)
                self.game_room = None  # type: ignore
                message["payload"] = "You left the room"

        if data["action"] == "game":
            self.game_room.service_data(data)
            return

        self.client.send((json.dumps(message) + "\0").encode())

    def set_event(self) -> None:
        """Stop the thread"""
        self.event.set()

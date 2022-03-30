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
        self.username: str = "None"

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

                message = json.loads(data)
                self.service_data(message)

        print(f"{self.client.getsockname()[0]} has disconnected")

    def service_data(self, data: dict) -> None:
        """Parse the user data and service it accordingly"""
        response: dict = {"success": None, "payload": {}}

        if data["action"] == "username":
            username = data["payload"]
            self.username = username

            response["success"] = True
            response["payload"] = "Username set"

        elif data["action"] == "create":
            payload = data["payload"]
            try:
                self.server_room.create_room(payload, self.username)
                response["success"] = True
                response["payload"] = "Room created"
            except RoomNameAlreadyTaken:
                response["success"] = False
                response["payload"] = "Room name is already taken"

        elif data["action"] == "join":
            payload = data["payload"]
            try:
                self.game_room = self.server_room.join(payload, self.client, self.username)
                response["success"] = True
                response["payload"] = f"Joined {payload}"
            except RoomNotFound:
                response["success"] = False
                response["payload"] = "Room not found"
            except RoomFull:
                response["success"] = False
                response["payload"] = "Room is full"

        elif data["action"] == "get_rooms":
            response["success"] = True
            response["payload"] = self.server_room.get_all_rooms()

        elif data["action"] == "leave_room":
            if self.game_room is not None:
                self.game_room.leave(self.client)
                self.game_room = None  # type: ignore
                response["success"] = True
                response["payload"] = "You left the room"
            else:
                response["success"] = False
                response["payload"] = "You aren't in a room"

        elif data["action"] == "game":
            self.game_room.service_data(data)
            return

        self.client.send((json.dumps(response)).encode())

    def set_event(self) -> None:
        """Stop the thread"""
        self.event.set()

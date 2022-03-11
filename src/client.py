import threading
import select


class ThreadedClient(threading.Thread):
    """Threadclient class for each client that connects"""

    clients = {
        "1": None,
        "2": None,
    }

    def __init__(self, client):
        threading.Thread.__init__(
            self,
        )
        self.event = threading.Event()
        self.client = client
        self.client_id = self.get_id()

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

                    sender_id, message = data.decode().split(":")
                    sender_id = int(sender_id)

                    reciever_id = None
                    if sender_id == 1:
                        reciever_id = ThreadedClient.clients.get("2")
                    if sender_id == 2:
                        reciever_id = ThreadedClient.clients.get("1")

                    if reciever_id is None:
                        self.client.send(str.encode("No end user is connected"))
                        continue
                    reciever_id.send(str.encode(message))

        print(f"{self.client.getsockname()[0]} has disconnected")
        ThreadedClient.clients[self.client_id] = None

    def get_id(self):
        """Return an ID for the client"""
        if ThreadedClient.clients.get("1") is None:
            return "1"
        return "2"

    def set_event(self):
        """Stop the thread"""
        self.event.set()

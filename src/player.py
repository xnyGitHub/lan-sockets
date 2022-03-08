"""Player module"""
import socket
import threading
import queue
import time
import select

from src.utils import flush_print_default

print = flush_print_default(print)
HOST = "192.168.0.13"
PORT =  5555

class Player:
    """Player class"""
    def __init__(self):
        self.connected = False
        self.queue = queue.Queue(maxsize=2)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        """Connect to socket"""
        self.socket.connect((host, port))
        self.connected = True

    def add_message_buffer(self, message):
        """Add message to queue buffer"""
        self.queue.put(message)

    def get_message_buffer(self):
        """Get oldest message from queue buffer"""
        if self.queue.empty():
            return None
        return self.queue.get()

    def shutdown(self):
        """
        Shutdown the server with socket.close()
        Kill threads safely by breaking while loop they are in
        """
        self.socket.close()
        self.connected = False

    def send(self):
        """Send message to socket"""
        while self.connected:
            if message := self.get_message_buffer():
                byte_string = str.encode(f"{message}")
                self.socket.sendall(byte_string)

    def recieve(self):
        """Socket listener function"""
        while self.connected:
            try:
                readable, _, _ = select.select([self.socket], [], [], 2)
            except ValueError:
                pass
            for obj in readable:
                if obj is self.socket:
                    if self.socket.fileno() == -1:
                        # If we close the socket
                        print("\n------------- \nClosing socket...")
                        break

                    data = self.socket.recv(1024)

                    if not data:
                        print("\n------------- \nMax connections or Server shutdown - Closing socket...")
                        self.shutdown()
                        break

                    print(f"Received {data}")

    def start(self):
        """Start the server"""
        print("Connecting to server...")

        self.connect(HOST,PORT)
        time.sleep(2)
        threading.Thread(target=self.send).start()
        threading.Thread(target=self.recieve).start()
        time.sleep(3)

        if self.connected:
            print("Connected")
        while self.connected:
            try:
                message = input("Enter: ")
                self.add_message_buffer(message=message)
            except KeyboardInterrupt:
                self.shutdown()
                break


if __name__ == "__main__":
    player = Player()
    player.start()

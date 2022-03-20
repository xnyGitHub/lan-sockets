""" Socket module"""  # pylint: disable =redefined-builtin
import select
import signal
import socket
import sys


from src.utils import ctrlc_handler, flush_print_default
from src.client import ThreadedClient
from src.rooms import Room

print = flush_print_default(print)


class Socket:
    """Server class"""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host: str, port: int) -> None:
        print("Initialising server...")
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.running_threads: list = []
        self.server_rooms: Room = Room.instance()  # type: ignore

    def run(self) -> None:
        """Entry to point to start server"""
        print("Server is running!")
        while True:
            try:  # So we can KeyBoard Interrupt
                readable, _, _ = select.select([self.sock], [], [], 2)
                for obj in readable:
                    if obj is self.sock:
                        client, _ = self.sock.accept()

                        # Start a new client thread
                        new_client = ThreadedClient(client, self.server_rooms)
                        new_client.start()
                        self.running_threads.append(new_client)

            except KeyboardInterrupt:
                for thr in self.running_threads:
                    thr.set_event()
                self.sock.close()
                break
        print("Shutting down server")


if __name__ == "__main__":
    HOST = ""
    PORT = 5555

    if sys.platform == "darwin":
        HOST = "192.168.0.60"
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # Detect if  Ctrl+Z was pressed

    if sys.platform == "win32":
        HOST = "192.168.0.13"
    new_server = Socket(HOST, PORT)
    new_server.run()

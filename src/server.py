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
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.running_threads: list = []
        self.server_rooms: Room = Room.instance()  # type: ignore

    def run(self) -> None:
        """Entry to point to start server"""
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
                self.shutdown()
                break
        print("Shutting down server")

    def shutdown(self) -> None:
        """Shutdown the server"""
        for thr in self.running_threads:
            thr.set_event()
        self.sock.close()


if __name__ == "__main__":
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 5555

    if sys.platform == "darwin":
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # type: ignore
    print("-----------------------------")
    print("Starting server...")
    new_server = Socket(HOST, PORT)
    print(
        f"""-----------------------------
The server is now running on;
HOST: {HOST}
PORT: {PORT}
-----------------------------
Hit CTRL+C to shutdown server
-----------------------------"""
    )
    new_server.run()

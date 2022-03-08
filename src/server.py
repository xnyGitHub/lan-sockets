""" Socket module"""
import select
import signal
import socket
import sys
import threading

from src.utils import ctrlc_handler, flush_print_default

print = flush_print_default(print)

HOST = ""
PORT = 5555

class Socket:
    """Server class"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host, port):
        print("Initialising server...")
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.connections = 0
        self.running = False

    def threaded_client(self, client):
        """Create a threaded client"""
        self.connections += 1
        print(f"{client.getsockname()} has connected")

        while self.running:
            readable, _, _ = select.select([client], [], [], 2)
            for obj in readable:
                if obj is client:
                    data = client.recv(1024)
                    if not data:
                        print(f"{client.getsockname()} has disconnected")
                        self.connections -= 1
                        client.close()
                        self.shutdown()
                        break
                    print(f"Received message from {data.decode()}")

    def shutdown(self):
        """Shut down the server"""
        self.running = False

    def run(self):
        """Entry to point to start server"""
        print("Server is running!")
        self.running = True
        while True:
            try:  # So we can KeyBoard Interrupt
                readable, _, _ = select.select([self.sock], [], [], 2)
                for obj in readable:
                    if obj is self.sock:
                        client, _ = self.sock.accept()  # Blocking
                        if self.connections == 1:  # Max connections
                            client.close()  # Close client instantly
                            continue

                        # Start a new client thread
                        new_client = threading.Thread(target=self.threaded_client, args=(client,))
                        new_client.start()

            except KeyboardInterrupt:
                self.shutdown()
                break
        print("Shutting down server")


if __name__ == "__main__":

    if sys.platform == "darwin":
        HOST = "192.168.0.60"
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # Detect if  Ctrl+Z was pressed

    if sys.platform ==   "win32":
        HOST = "192.168.0.13"
    new_server = Socket(HOST, PORT)
    new_server.run()

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


class ThreadedClient(threading.Thread):
    """Threadclient class for each client that connects"""
    def __init__(self, client):
        threading.Thread.__init__(
            self,
        )
        self.event = threading.Event()
        self.client = client

    def run(self):
        print(f"{self.client.getsockname()[0]} has connected")
        while not self.event.is_set():
            readable, _, _ = select.select([self.client], [], [], 2)
            for obj in readable:
                if obj is self.client:
                    data = self.client.recv(1024)
                    if not data:
                        print(f"{self.client.getsockname()[0]} has disconnected")
                        self.client.close()
                        self.event.set()
                        break
                    print(f"Received message from {data.decode()}")
    
    def set_event(self):
        self.event.set()


class Socket:
    """Server class"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, host, port):
        print("Initialising server...")
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.running_threads = []
        self.connections = 0
    
    def check_running_threads(self):
        """Check number of threaded clients"""
        self.connections =  threading.active_count() - 1
            
    def run(self):
        """Entry to point to start server"""
        print("Server is running!")
        while True:
            self.check_running_threads()
            try:  # So we can KeyBoard Interrupt
                readable, _, _ = select.select([self.sock], [], [], 2)
                for obj in readable:
                    if obj is self.sock:
                        client, _ = self.sock.accept()  # Blocking
                        if self.connections == 1:  # Max connections
                            client.close()  # Close client instantly
                            continue

                        # Start a new client thread
                        new_client = ThreadedClient(client)
                        new_client.start()
                        self.running_threads.append(new_client)

            except KeyboardInterrupt:
                for thr in self.running_threads:
                    thr.set_event()
                self.sock.close()
                break
        print("Shutting down server")


if __name__ == "__main__":

    if sys.platform == "darwin":
        HOST = "192.168.0.60"
        signal.signal(signal.SIGTSTP, ctrlc_handler)  # Detect if  Ctrl+Z was pressed

    if sys.platform == "win32":
        HOST = "192.168.0.13"
    new_server = Socket(HOST, PORT)
    new_server.run()

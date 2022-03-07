import socket
import threading
from threading import Lock
import queue
import time
import select
import sys

LOCK = Lock()

class Player:

    def __init__(self):
        self.connected = False
        self.queue = queue.Queue(maxsize = 2)
        self.print_queue = queue.Queue(maxsize=5)
        self.recv_thread = threading.Thread(target=self.recieve)
        self.send_thread = threading.Thread(target=self.send)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self,host,port):
        self.socket.connect((host, port))
        self.connected = True
    
    def add_message_buffer(self,message):
        self.print_queue.put(message)

    def get_message_buffer(self):
        if self.print_queue.empty():
            return None
        return self.print_queue.get()

    def add_message_buffer(self,message):
        self.queue.put(message)

    def get_message_buffer(self):
        if self.queue.empty():
            return None
        return self.queue.get()

    def shutdown(self):
        self.connected = False
        self.print_out("Shutting down")
    
    def print_out(self,message):
        with LOCK:
            print(message)

    def send(self):
        while self.connected:
            if message:= self.get_message_buffer():
                byte_string = str.encode(f"{message}")
                self.socket.sendall(byte_string)

    def recieve(self):
        while self.connected:
            timeout = 2
            readable, _, _ = select.select([self.socket], [], [], timeout)
            for s in readable:
                if s is self.socket:
                    try:
                        data = self.socket.recv(1024)
                    except:
                        self.socket.shutdown(socket.SHUT_RDWR)
                        self.socket.close()
                        break
                    
                    if not data or data == b'':
                        self.shutdown()
                        self.socket.close()
                        break
                    
                    self.print_out(f"Received {data}")         

    def start(self):
        self.recv_thread.start()
        self.send_thread.start()
        self.print_out("Connecting to server...")
        time.sleep(1)
        self.print_out("Connected")
        while self.connected:
            try:
                message = input("Enter: ")
                self.add_message_buffer(message=message)
            except KeyboardInterrupt:
                self.shutdown()

if __name__ == "__main__":
    player = Player()
    player.connect("192.168.0.60",5555)
    player.start()
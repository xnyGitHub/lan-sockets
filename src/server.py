# Server module
import socket
import signal
import threading
import select

class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self,host,port):
        self.sock.bind((host, port))
        self.sock.listen(2)
        self.connections = 0
        self.conn_client = None
        self.running = False
    
    @staticmethod
    def unsafe_exit(signum,frame):
        print("Ctrl+Z pressed, but ignored, use Ctrl+C instead")
        
    def threaded_client(self,client):
        self.connections += 1
        print(f"{client.getsockname()} has connected")
        while self.running:
            timeout = 2
            readable, _, _ = select.select([client], [], [], timeout)
            for s in readable:
                if s is client:
                    try:
                        data = client.recv(1024)
                        if not data:
                            print("Closing connection")
                            self.connections -=1
                            self.conn_client.close()
                            self.running = False
                            break
                        print(f"Received message from {data.decode()}")
                    except:
                        pass
        

                
    def run(self):
        self.running = True
        while True:
            try: # So we can KeyBoard Interrupt
                self.conn_client,_  = self.sock.accept() # Blocking
                if self.connections == 1: # Max connections
                    self.conn_client.send(b'')
                    self.conn_client.close() # Close client instantly
                    continue
                
                # Start a new client thread
                new_client = threading.Thread(target=self.threaded_client, args=(self.conn_client,))
                new_client.start()
            except OSError as err:
                print(err)
                continue
            except KeyboardInterrupt:
                self.running = False
                break
        self.sock.close()
        print("Closing socket")



if __name__ == "__main__":
    signal.signal(signal.SIGTSTP, Server.unsafe_exit)  # Detect if  Ctrl+Z was pressed
    new_server = Server("192.168.0.60",5555)
    new_server.run()

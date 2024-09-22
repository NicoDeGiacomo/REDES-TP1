import socket
import threading

class UDPServer:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind((self.host, self.port))
        self.running = True

    def start(self):
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        while self.running:
            data, addr = self.server.recvfrom(1024)
            print(f"Received message: {data.decode()} from {addr}")
            self.server.sendto(data, addr)  # Echo the message back

    def stop(self):
        self.running = False
        self.server.close()
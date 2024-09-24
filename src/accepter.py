import socket
import logging

from downloader import Downloader
from protocol import StopAndWait, TCPSAck
from uploader import Uploader

logger = logging.getLogger(__name__)

class Accepter:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        logger.info(f"Server accepter bounded to {self.host}:{self.port}")

    def receive_client(self):
        logger.info(f'Server waiting for client at {self.host}:{self.port}')
        header, addr = self.socket.recvfrom(100)
        action, protocol, file_name= self._parse_header(header)
        logger.info(f'Server received an {'Upload' if action == 1 else 'Download'} action using {'S&W' if action == 1 else 'TCP + SACK'} protocol for a file named {file_name} ')

        #TODO: check error cases (memory/ports/filename usage) depending on the action. In case of error, answer here to the respective client
        new_client_protocol = StopAndWait(self.host, addr[0], addr[1]) if action == 1 else TCPSAck(self.host, addr[0], addr[1])

        new_client_action = Uploader(file_name, new_client_protocol) if action == 1 else Downloader(file_name, new_client_protocol)
        return new_client_action

    @staticmethod
    def _parse_header(header):
        first_byte = header[0]

        action= (first_byte >> 7) & 0b00000001
        protocol = (first_byte >> 6) & 0b00000001
        file_name_length = first_byte & 0b00111111
        file_name = header[1:1 + file_name_length].decode()
        return action, protocol, file_name

    def close(self):
        self.socket.close()
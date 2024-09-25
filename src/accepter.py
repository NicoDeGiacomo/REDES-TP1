import socket
import logging
import os

import downloader 
import protocol
import uploader



logger = logging.getLogger(__name__)

class Accepter:
    def __init__(self, storage, host, port):
        self.storage_path = storage
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.host, self.port))
        logger.info(f"Server accepter bounded to {self.host}:{self.port}")

    def receive_client(self):
        logger.info(f'Server waiting for client at {self.host}:{self.port}')
        header, addr = self.socket.recvfrom(100)
        action, ptocol, file_name= self._parse_header(header)
        logger.info(f'Server received an {'Upload' if action == 1 else 'Download'} action using {'S&W' if action == 1 else 'TCP + SACK'} protocol for a file named {file_name} ')
        file_path=os.path.join(self.storage_path, file_name)

        #TODO: check error cases (memory/ports/filename usage) depending on the action. In case of error, answer here to the respective client
        new_client_protocol = protocol.StopAndWait(self.host, addr, file_path) if ptocol == 1 else protocol.TCPSAck(self.host, addr, file_path)

        new_client_action = uploader.Uploader(new_client_protocol) if action == 1 else downloader.Downloader(new_client_protocol)
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
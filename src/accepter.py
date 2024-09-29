import logging
import os

from udp_client import UDPClient
from uploader import Uploader
from downloader import Downloader
from tcp_sack_sender import TCPSAckSender
from tcp_sack_receiver import TCPSAckKReceiver
from stop_and_wait import StopAndWait

logger = logging.getLogger(__name__)


class Accepter:
    def __init__(self, storage, host, port):
        self.storage_path = storage
        self.socket = UDPClient(host, port)
        self.socket.set_retry(1)
        self.socket.set_timeout(None)
        logger.info(f"Server accepter bounded to {self.socket.host}:{self.socket.port}")

    def receive_client(self):
        logger.info(f'Server waiting for client at {self.socket.host}:{self.socket.port}')
        header, addr = self.socket.receive_message(100)
        action, ptocol, file_name = self._parse_header(header)
        logger.info(f'Server received an {'Upload' if action == 1 else 'Download'} action '
                    f'using {'S&W' if ptocol == 1 else 'TCP + SACK'} protocol for a file named {file_name} ')
        file_path = os.path.join(self.storage_path, file_name)

        #TODO: check error cases (memory/ports/filename usage) depending on the action. In case of error, answer here to the respective client
        if action == 0:
            new_client_protocol = StopAndWait(self.socket.host, addr, file_path) if ptocol == 1 \
                else TCPSAckSender(10, 10, file_path, self.socket.host, addr, 0)
        else:
            new_client_protocol = StopAndWait(self.socket.host, addr, file_path) if ptocol == 1 \
                else TCPSAckKReceiver(10, 10, file_path, self.socket.host, addr,0)
        

        new_client_action = Uploader(new_client_protocol) if action == 0 else Downloader(new_client_protocol)
        return new_client_action

    @staticmethod
    def _parse_header(header):
        first_byte = header[0]

        action = (first_byte >> 7) & 0b00000001
        protocol = (first_byte >> 6) & 0b00000001
        file_name_length = first_byte & 0b00111111
        file_name = header[1:1 + file_name_length].decode()
        return action, protocol, file_name

    def close(self):
        self.socket.close()

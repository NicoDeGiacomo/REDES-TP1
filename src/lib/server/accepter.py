import logging
import os

from lib.server.uploader import Uploader
from lib.server.downloader import Downloader

from lib.utils.action import Action
from lib.utils.udp_client import UDPClient
from lib.protocols.TCP_SACK.tcp_sack_sender import TCPSAckSender
from lib.protocols.TCP_SACK.tcp_sack_receiver import TCPSAckKReceiver
from lib.protocols.stop_and_wait.stop_and_wait import StopAndWait

logger = logging.getLogger(__name__)


class Accepter:
    def __init__(self, storage, host, port):
        self.storage_path = storage
        self.socket = UDPClient(host, port)
        self.socket.set_timeout(None)
        logger.info(
            f"Server accepter bounded to "
            f"{self.socket.host}:{self.socket.port}")

    def receive_client(self):
        logger.info(
            f'Server waiting for client at '
            f'{self.socket.host}:{self.socket.port}')
        header, addr = self.socket.receive_message(100)
        action, ptocol, file_name = self._parse_header(header)
        logger.info(
            f'Server received an '
            f'{'Upload' if action == 1 else 'Download'} action '
            f'using {'S&W' if ptocol == 1 else 'TCP + SACK'} protocol '
            f'for a file named {file_name} ')
        file_path = str(os.path.join(self.storage_path, file_name))

        error_code = 0
        error_bite = 0

        if action == Action.UPLOAD.value and os.path.exists(file_path):
            logger.error(f"File '{file_name}' already exists.")
            error_code = 1

        if action == Action.DOWNLOAD.value and (not os.path.exists(file_path)):
            logger.error(f"File '{file_name}' does not exists.")
            error_code = 2

        if error_code:
            error_bite = 1
            self.answer_connection(error_bite, error_code, addr)
            return None

        if action == 0:
            new_client_protocol = StopAndWait(self.socket.host, addr,
                                              file_path) if ptocol == 1 \
                else TCPSAckSender(100, file_path, self.socket.host, addr, 0)
        else:
            new_client_protocol = StopAndWait(self.socket.host, addr,
                                              file_path) if ptocol == 1 \
                else TCPSAckKReceiver(100, file_path, self.socket.host, addr,
                                      0)

        new_client_action = Uploader(
            new_client_protocol) if action == 0 else Downloader(
            new_client_protocol)
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

    def answer_connection(self, error_bite, error_code, addr):
        logger.info("Answering client request")
        answer_header = bytearray()
        first_byte = (error_bite << 7) | error_code
        answer_header.append(first_byte)
        self.socket.send_message_to(answer_header, addr)

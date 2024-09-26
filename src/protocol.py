from abc import ABC, abstractmethod
import logging
import os

from udp_client import UDPClient

logger = logging.getLogger(__name__)

RANDOM_HOST = 0


class Protocol(ABC):
    def __init__(self, host, addr: (str, int), file_path):
        self.socket = UDPClient(host, RANDOM_HOST)
        self.addr = addr
        self.file_path = file_path
        self.protocol_bit = None

    @abstractmethod
    def start_upload(self):
        pass

    @abstractmethod
    def start_download(self):
        pass

    @staticmethod
    @abstractmethod
    def get_header_value():
        pass

    def answer_connection(self):
        logger.info(f"Answering client request")
        error_bite = 0
        error_code = 0
        answer_header = bytearray()
        first_byte = (error_bite << 7) | error_code
        answer_header.append(first_byte)
        self.socket.send_message_to(answer_header, self.addr)

    def __receive_confirmation(self):
        logger.info(f"Waiting for confirmation")
        status, new_addr = self.socket.receive_message(1)
        first_byte = status[0]
        error = (first_byte >> 7) & 0b00000001
        error_code = first_byte & 0b01111111

        if not error:
            logger.info(f"Connection successful")
            self.addr = new_addr
            return True
        else:
            # TODO: handle error code
            return False

    def establish_connection(self, action):
        self.__send_header(action)
        logger.info(f"Connection request sent")
        return self.__receive_confirmation()

    def __send_header(self, action_bit):
        file_name = os.path.basename(self.file_path)
        file_name_bytes = file_name.encode()  # utf-8 by default
        first_byte = (action_bit << 7) | (self.protocol_bit << 6) | len(file_name_bytes)
        header = bytearray()
        header.append(first_byte)
        header.extend(file_name_bytes)

        logger.info(f"sending connection request to Addr: {(self.addr[0], int(self.addr[1]))}")
        if not self.socket.send_message_to(header, (self.addr[0], int(self.addr[1]))):
            return 0

    def close(self):
        self.socket.close()

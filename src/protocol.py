from abc import ABC, abstractmethod
import logging
import socket
import os

logger = logging.getLogger(__name__)

RANDOM_HOST = 0

class Protocol(ABC):
    def __init__(self, host, addr, file_path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, RANDOM_HOST))
        self.addr = addr
        self.file_path = file_path
        self.protocol_bit = None

    @abstractmethod
    def start_upload(self, dst_host, dst_port):
        pass

    @abstractmethod
    def start_download(self):
        pass

    @abstractmethod
    def get_header_value(self):
        pass

    def answer_connection(self):
        logger.info(f"Answering client request")
        error_bite = 0
        error_code = 0
        answer_header = bytearray()
        first_byte = (error_bite << 7) | error_code
        answer_header.append(first_byte)
        self.socket.sendto(answer_header, self.addr)

    @abstractmethod
    def stablish_connection(self, action):
        pass

    def send_header(self, action_bit):
        file_name = os.path.basename(self.file_path)
        file_name_bytes = file_name.encode()  # utf-8 by default
        first_byte = (action_bit << 7) | (self.protocol_bit << 6) | len(file_name_bytes)
        header = bytearray()
        header.append(first_byte)
        header.extend(file_name_bytes)
        logger.info(f"Handshake header created\n")

        if not self.socket.sendto(header, self.addr):
            return 0



class StopAndWait(Protocol):
    def __init__(self, host, addr, file_path):
        self.protocol_bit = 1
        super().__init__(host, addr, file_path)

    @staticmethod
    def get_header_value(self):
        return 0
        

    def start_upload(self, dst_host, dst_port):
        logger.info(f"Starting upload with Stop And Wait protocol")

        #starts uploading the file

        #TODO: implement S&W upload logic

    def start_download(self):
        logger.info(f"Starting download with Stop And Wait protocol")
        #TODO: implement S&W download logic




class TCPSAck(Protocol):
    def __init__(self, host, addr, file_path):
        self.protocol_bit = 0
        super().__init__(host, addr, file_path)
        
    @staticmethod
    def get_header_value(self):
        return 1
    
    def start_upload(self, dst_host, dst_port):

        #self.answer_connection(error, error_code)

        logger.info(f"Starting upload with TCP + SAck protocol")

        # TODO: implement S&W download logic

    def start_download(self):
        logger.info(f"Starting download with TCP + SAck protocol")
        # TODO: implement TCP + SACK download logic


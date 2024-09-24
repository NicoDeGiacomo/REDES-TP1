from abc import ABC, abstractmethod
import logging
import socket

logger = logging.getLogger(__name__)

RANDOM_HOST = 0

class Protocol(ABC):
    @abstractmethod
    def start_upload(self, dst_host, dst_port, file_name):
        pass

    @abstractmethod
    def start_download(self, file_name):
        pass

    def answer_connection(self):
        logger.info(f"Answering client request")
        # TODO: implement connection possitive ACK message (the required verifications of error ack are made before)


class StopAndWait(Protocol):
    def __init__(self, host, dst_host, dst_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, RANDOM_HOST))
        self.dst_host, self.dst_port = dst_host, dst_port

    def start_upload(self, dst_host, dst_port, file_name):
        logger.info(f"Starting upload with Stop And Wait protocol")
        #TODO: implement S&W upload logic

    def start_download(self, file_name):
        logger.info(f"Starting download with Stop And Wait protocol")
        #TODO: implement S&W download logic


class TCPSAck(Protocol):
    def __init__(self, host, dst_host, dst_port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, RANDOM_HOST))
        self.dst_host, self.dst_port = dst_host, dst_port

    def start_upload(self, dst_host, dst_port, file_name):
        logger.info(f"Starting upload with TCP + SAck protocol")
        # TODO: implement S&W download logic

    def start_download(self, file_name):
        logger.info(f"Starting download with TCP + SAck protocol")
        # TODO: implement TCP + SACK download logic
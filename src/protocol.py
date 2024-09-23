from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class Protocol(ABC):
    @abstractmethod
    def start_upload(self, dst_host, dst_port, file_name):
        pass

    @abstractmethod
    def start_download(self, file_name):
        pass


class StopAndWait(Protocol):
    def __init__(self, socket):
        self.socket = socket

    def start_upload(self, dst_host, dst_port, file_name):
        logger.info(f"Starting upload with Stop And Wait protocol")

    def start_download(self, file_name):
        logger.info(f"Starting download with Stop And Wait protocol")

class TCPSAck(Protocol):
    def __init__(self, socket):
        self.socket = socket

    def start_upload(self, dst_host, dst_port, file_name):
        logger.info(f"Starting upload with TCP + SAck protocol")

    def start_download(self, file_name):
        logger.info(f"Starting download with TCP + SAck protocol")

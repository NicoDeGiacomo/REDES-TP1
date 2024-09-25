import socket
import threading
import logging
from protocol import Protocol, TCPSAck, StopAndWait

logger = logging.getLogger(__name__)

class Uploader(threading.Thread):
    def __init__(self, comm_protocol):
        super().__init__()
        self.uploading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting upload")
        self.protocol.answer_connection()
        self.protocol.start_download()

    def stop(self):
        self.uploading = False


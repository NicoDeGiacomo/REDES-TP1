import threading
import logging

from protocol import Protocol

logger = logging.getLogger(__name__)


class Downloader(threading.Thread):
    def __init__(self, comm_protocol: Protocol):
        super().__init__()
        self.downloading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting download ")
        self.protocol.answer_connection()
        self.protocol.start_upload()

    def stop(self):
        self.downloading = False


import threading
import logging

from lib.protocols.protocol import Protocol

logger = logging.getLogger(__name__)


class Downloader(threading.Thread):
    def __init__(self, comm_protocol: Protocol):
        super().__init__()
        self.downloading = threading.Event()
        self.downloading.set()
        self.protocol = comm_protocol

    def run(self):
        logger.info("Starting download ")
        self.protocol.answer_connection()
        self.protocol.start_download(self.downloading)

    def stop(self):
        self.downloading.clear()

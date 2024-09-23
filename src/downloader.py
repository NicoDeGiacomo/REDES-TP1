import socket
import threading
import logging
import protocol

logger = logging.getLogger(__name__)


class Downloader(threading.Thread):
    def __init__(self, filename, comm_protocol):
        super().__init__()
        self.filename = filename
        self.uploading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting download of {self.filename}")
        # TODO: implement download logic, calls protocol start_download

    def stop(self):
        self.uploading = False


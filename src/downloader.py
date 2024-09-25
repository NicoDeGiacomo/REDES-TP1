import threading
import logging

logger = logging.getLogger(__name__)


class Downloader(threading.Thread):
    def __init__(self, comm_protocol):
        super().__init__()
        self.uploading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting download ")
        self.protocol.answer_connection()
        self.protocol.start_download()
        # TODO: implement download logic, calls protocol start_download

    def stop(self):
        self.uploading = False


import logging
import threading

logger = logging.getLogger(__name__)


class Uploader(threading.Thread):
    def __init__(self, comm_protocol):
        super().__init__()
        self.uploading = threading.Event()
        self.uploading.set()
        self.protocol = comm_protocol

    def run(self):
        logger.info("Starting upload")
        self.protocol.answer_connection()
        self.protocol.start_upload(self.uploading)

    def stop(self):
        self.uploading.clear()

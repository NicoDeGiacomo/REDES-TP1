import socket
import threading
import logging
import protocol

logger = logging.getLogger(__name__)

class Uploader(threading.Thread):
    def __init__(self, socket, filename, dst_host, dst_port, protocol):
        super().__init__()
        self.socket = socket
        self.filename = filename
        self.dst_host, self.dst_port = dst_host, dst_port
        self.uploading = True
        self.protocol = protocol

    def run(self):
        logger.info(f"Starting upload of {self.filename}")
        # TODO: implement upload logic, calls protocol start_upload

    def stop(self):
        self.uploading = False


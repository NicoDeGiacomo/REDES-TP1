import socket
import threading
import logging
import protocol

logger = logging.getLogger(__name__)

class Uploader(threading.Thread):
    def __init__(self, filename, comm_protocol):
        super().__init__()
        self.filename = filename
        self.uploading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting upload of {self.filename}")
        # TODO: implement upload logic, calls protocol start_upload
        #self.protocol.start_upload(self.filename)
        #logger.info(f"Upload finished")

    def stop(self):
        self.uploading = False


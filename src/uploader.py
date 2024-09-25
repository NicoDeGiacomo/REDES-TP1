import socket
import threading
import logging
import protocol.protocol_config as protocol_config

logger = logging.getLogger(__name__)

class Uploader(threading.Thread):
    def __init__(self, comm_protocol):
        super().__init__()
        self.uploading = True
        self.protocol = comm_protocol

    def run(self):
        logger.info(f"Starting upload")
        # TODO: implement upload logic, calls protocol start_upload
        #self.protocol.start_upload(self.filename)
        #logger.info(f"Upload finished")

    def stop(self):
        self.uploading = False


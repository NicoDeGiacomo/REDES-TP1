from protocol import Protocol, logger


class TCPSAck(Protocol):
    def __init__(self, host, addr, file_path):
        super().__init__(host, addr, file_path)
        self.protocol_bit = 0

    @staticmethod
    def get_header_value():
        return 0

    def start_upload(self):
        #self.answer_connection(error, error_code)

        logger.info(f"Starting upload with TCP + SAck protocol to Address: {self.addr}")

        # TODO: implement S&W download logic

    def start_download(self):
        logger.info(f"Starting download with TCP + SAck protocol from Address: {self.addr}")
        # TODO: implement TCP + SACK download logic

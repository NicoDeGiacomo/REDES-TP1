import threading

from lib.protocols.protocol import Protocol, logger

MAX_RETRIES = 15


class StopAndWait(Protocol):
    def __init__(self, host, addr: (str, int), file_path):
        super().__init__(host, addr, file_path)
        self.protocol_bit = 1

    @staticmethod
    def get_header_value():
        return 1

    def start_upload(self, uploading_status: threading.Event):
        self.socket.set_timeout(0.01)
        logger.info(
            f"Starting upload with Stop And Wait protocol to Address: "
            f"{self.addr}")
        self.file.open('rb')
        seq_num = 0
        try:
            while uploading_status is None or uploading_status.is_set():
                data = self.file.read(
                    1490)  # calcular tamaño real 65507 - 4 (header size)
                header = create_header(seq_num, self.file.eof,
                                       self.eoc)  # falta bit de eoc
                packet = header + data
                retries = 0
                while uploading_status is None or uploading_status.is_set():
                    logger.info(
                        f"Sending Packet: {header}, "
                        f"for the {retries + 1} time")
                    self.socket.send_message_to(packet, self.addr)
                    ack, addr = self.socket.receive_message(2)
                    # if self.addr != addr:
                    if retries > MAX_RETRIES:
                        logger.info("CONNECTION WITH DOWNLOADER LOST")
                        self.file.close()
                        super().close()
                        return False

                    if ack is None:
                        retries += 1
                        continue

                    ack_seq_num, self.eoc = parse_ack(ack)

                    if ack_seq_num == seq_num:
                        break
                    retries += 1

                if self.file.eof or self.eoc:
                    break
                seq_num = (seq_num + 1) % 2
        except KeyboardInterrupt:
            logger.debug("Exception keyboardinterrupt")
            self.eoc = 1
            header = create_header(seq_num, self.file.eof, self.eoc)
            self.socket.send_message_to(header, self.addr)
            self.file.close()
            super().close()
            return False

        if uploading_status and not uploading_status.is_set():
            logger.debug("Thread stopped")
            self.eoc = 1
            header = create_header(seq_num, self.file.eof, self.eoc)
            self.socket.send_message_to(header, self.addr)
            self.file.close()
            super().close()
            return False

        if self.eoc:
            logger.error("Connection lost due to eoc ")

        self.file.close()
        super().close()

    def start_download(self, downloading_status: threading.Event):
        self.socket.set_timeout(0.15)
        logger.info(
            f"Starting download with Stop And Wait protocol from Address: "
            f"{self.addr}")
        self.file.open('wb')
        eof = 0
        seq_num = 0
        try:
            while downloading_status is None or downloading_status.is_set():
                packet, _, = self.socket.receive_message(1500)
                if packet is None:
                    logger.error("CONNECTION WITH UPLOADER LOST")
                    self.file.delete()
                    super().close()
                    return False
                header = packet[:1]
                data = packet[1:]
                recv_seq_num, eof, self.eoc = parse_header(header)
                logger.info(f"Receiving Packet: {header}")

                if recv_seq_num == seq_num:
                    self.file.write(data)
                    ack = create_ack(seq_num, self.eoc)
                    self.socket.send_message_to(ack, self.addr)
                    if eof or self.eoc:
                        break
                    seq_num = (seq_num + 1) % 2
                else:
                    ack = create_ack((seq_num + 1) % 2, self.eoc)
                    self.socket.send_message_to(ack, self.addr)
        except KeyboardInterrupt:
            logger.debug("Exception keyboardinterrupt")
            self.eoc = 1
            ack = create_ack(seq_num, self.eoc)
            self.socket.send_message_to(ack, self.addr)
            if eof:
                logger.info("File downloaded successfully!")
                self.file.close()
            else:
                logger.error("CONNECTION WITH UPLOADER LOST")
                self.file.delete()
            super().close()
            return False

        if downloading_status and not downloading_status.is_set():
            logger.debug("Thread stopped")
            self.eoc = 1
            ack = create_ack(seq_num, self.eoc)
            self.socket.send_message_to(ack, self.addr)
            if eof:
                logger.info("File downloaded successfully!")
                self.file.close()
            else:
                logger.error("CONNECTION WITH UPLOADER LOST")
                self.file.delete()
            super().close()
            return False

        if eof:
            logger.info("File downloaded successfully!")
            self.file.close()
        else:
            logger.error("CONNECTION WITH UPLOADER LOST")
            self.file.delete()
        super().close()


def create_header(seq_num, eof, eoc):
    header = bytearray()
    first_byte = (seq_num << 7) | (eof << 6) | (eoc << 5)
    header.append(first_byte)
    return header


def parse_header(header):
    first_byte = header[0]
    seq_num = (first_byte >> 7) & 0b00000001
    eof = (first_byte >> 6) & 0b00000001
    eoc = (first_byte >> 5) & 0b00000001

    return seq_num, eof, eoc


def create_ack(seq_num, eoc):
    ack = bytearray()
    first_byte = (seq_num << 7) | (eoc << 6)
    ack.append(first_byte)
    return ack


def parse_ack(ack):
    first_byte = ack[0]
    seq_num = (first_byte >> 7) & 0b00000001
    eoc = (first_byte >> 6) & 0b00000001
    return seq_num, eoc

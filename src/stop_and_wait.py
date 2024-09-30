
from file_client import FileClient
from protocol import Protocol, logger

MAX_RETRIES = 15

class StopAndWait(Protocol):
    def __init__(self, host, addr: (str, int), file_path):
        super().__init__(host, addr, file_path)
        self.protocol_bit = 1


    @staticmethod
    def get_header_value():
        return 1

    def start_upload(self):
        self.socket.set_timeout(0.01)
        self.socket.set_retry(15)
        logger.info(f"Starting upload with Stop And Wait protocol to Address: {self.addr}")
        self.file.open('rb')
        seq_num = 0
        while True:
            data = self.file.read(1490)  # calcular tamaño real 65507 - 4 (header size)
            header = create_header(seq_num, self.file.eof)  #falta bit de eoc
            packet = header + data
            retries = 0
            while True:
                logger.info(f"Sending Packet: {header}, for the {retries + 1} time ")
                self.socket.send_message_to(packet, self.addr)
                ack, addr = self.socket.receive_message(2)
                #if self.addr != addr:
                if retries > MAX_RETRIES:
                    logger.info(f"CONNECTION WITH DOWNLOADER LOST")
                    self.file.close()
                    super().close()
                    return False

                if ack is None:
                    retries += 1
                    continue

                ack_seq_num = parse_ack(ack)
                if ack_seq_num == seq_num:
                    break



            if self.file.eof:
                break
            seq_num = (seq_num + 1) % 2

        self.file.close()
        super().close()

    def start_download(self):
        self.socket.set_timeout(0.15)
        self.socket.set_retry(1)
        logger.info(f"Starting download with Stop And Wait protocol from Address: {self.addr}")
        self.file.open('wb')
        seq_num = 0
        while True:
            packet, _ = self.socket.receive_message(1500)
            if packet is None:
                logger.info(f"CONNECTION WITH DOWNLOADER LOST")
                self.file.delete()
                super().close()
                return False
            header = packet[:1]
            data = packet[1:]
            recv_seq_num, eof = parse_header(header)
            logger.info(f"Receiving Packet: {header}")


            if recv_seq_num == seq_num:
                self.file.write(data)
                ack = create_ack(seq_num)
                self.socket.send_message_to(ack, self.addr)
                if eof:
                    break
                seq_num = (seq_num + 1) % 2
            else:
                ack = create_ack((seq_num + 1) % 2)
                self.socket.send_message_to(ack, self.addr)
        self.file.close()
        super().close()
        logger.info(f"File downloaded successfully")


def create_header(seq_num, eof):
    header = bytearray()
    first_byte = (seq_num << 7) | (eof << 6)
    header.append(first_byte)
    return header


def parse_header(header):
    first_byte = header[0]
    seq_num = (first_byte >> 7) & 0b00000001
    eof = (first_byte >> 6) & 0b00000001
    return seq_num, eof


def create_ack(seq_num):
    ack = bytearray()
    first_byte = (seq_num << 7)
    ack.append(first_byte)
    return ack


def parse_ack(ack):
    first_byte = ack[0]
    seq_num = (first_byte >> 7) & 0b00000001
    return seq_num

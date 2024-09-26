
from file_client import FileClient
from protocol import Protocol, logger


class StopAndWait(Protocol):
    def __init__(self, host, addr: (str, int), file_path):
        super().__init__(host, addr, file_path)
        self.protocol_bit = 1
        self.file = FileClient(file_path)

    @staticmethod
    def get_header_value():
        return 1

    def start_upload(self):
        self.socket.set_timeout(1)
        self.socket.set_retry(15)
        logger.info(f"Starting upload with Stop And Wait protocol to Address: {self.addr}")
        self.file.open('rb')
        seq_num = 0
        while True:
            data = self.file.read(1024)  # calcular tamaño real 65507 - 4 (header size)
            header = create_header(seq_num, self.file.eof)  #falta bit de eoc
            packet = header + data
            logger.info(f"Sending Packet: {header}")
            self.socket.send_message_to(packet, self.addr)
            ack, _ = self.socket.receive_message(2)
            ack_seq_num = parse_ack(ack)
            if ack_seq_num == seq_num:
                break
            if self.file.eof:
                break
            seq_num = (seq_num + 1) % 2
        self.file.close()
        super().close()

    def start_download(self):
        self.socket.set_timeout(15)
        self.socket.set_retry(1)
        logger.info(f"Starting download with Stop And Wait protocol from Address: {self.addr}")
        self.file.open('wb')
        seq_num = 0
        while True:
            packet, _ = self.socket.receive_message(1026)
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

from abc import abstractmethod

from protocol import Protocol, Header

MAX_RETRIES = 15


class ACKSACKHeader(Header):
    def __init__(self, eoc: int, seq_num: int, sack_length: int,
                 sack: list) -> None:
        super().__init__(None, eoc, seq_num)
        self.sack_length = sack_length
        self.sack = sack

    def get_bytes(self):
        header_first_line = (self.eoc << 31) | (0 << 30) | (
                    self.seq_num & 0b00111111111111111111111111111111)
        header_second_line = self.sack_length.to_bytes(byteorder='big')
        header_bytes = bytearray(
            header_first_line.to_bytes(4, byteorder='big'))
        header_bytes += header_second_line
        for i in self.sack:
            header_bytes += i[0].to_bytes(4, byteorder='big')
            header_bytes += i[1].to_bytes(4, byteorder='big')
        return header_bytes

    @staticmethod
    def parse_header(header_bytes: bytearray):
        # Ensure the input is more than 5 bytes
        if len(header_bytes) < 5:
            raise ValueError("Header must be at least 5 bytes long")

        # Convert the bytearray or bytes back to a 32-bit integer (big-endian)
        header = int.from_bytes(header_bytes[:4], byteorder='big')

        # Extract the EOC bit (bit 31)
        eoc_bit = (header >> 31) & 0b1

        # Extract the sequence number (bits 0-30)
        sequence_number = header & 0x7FFFFFFF

        sack_length = int.from_bytes(header_bytes[4:5], byteorder='big')
        sack = []
        for i in range(5, len(header_bytes), 4):
            sack.append(int.from_bytes(header_bytes[i:i + 4], byteorder='big'))
        return ACKSACKHeader(eoc_bit, sequence_number, sack_length, sack)


class TCPSAck(Protocol):
    def __init__(self, host, addr, file_path, initial_seq_num, window_size):
        super().__init__(host, addr, file_path)
        self.window_size = window_size
        self.window = []
        self.protocol_bit = 0
        self.initial_seq_num = initial_seq_num
        self.max_retry = MAX_RETRIES

    @staticmethod
    def get_header_value():
        return 0

    @abstractmethod
    def start_upload(self):
        pass

    @abstractmethod
    def start_download(self):
        pass

from abc import ABC, abstractmethod
import logging
import os
from file_client import FileClient

from udp_client import UDPClient

logger = logging.getLogger(__name__)

RANDOM_HOST = 0


class Header:
    def __init__(self, eof, eoc, seq_num):
        eoc_bit = 1 if eoc else 0
        eof_bit = 1 if eof else 0
        if not (0 <= seq_num < 2 ** 30):
            raise ValueError("Sequence number must be in range [0, 2^30 - 1]")
        self.eof = eof_bit
        self.eoc = eoc_bit
        self.seq_num = seq_num

    def get_bytes(self):
        header = (self.eoc << 31) | (self.eof << 30) | self.seq_num
        return bytearray(header.to_bytes(4, byteorder='big'))

    @staticmethod
    def parse_header(header_bytes: bytearray):
        # Ensure the input is 4 bytes
        if len(header_bytes) != 4:
            raise ValueError("Header must be exactly 4 bytes long")

        # Convert the bytearray or bytes back to a 32-bit integer (big-endian)
        header = int.from_bytes(header_bytes, byteorder='big')

        # Extract the EOC bit (bit 31)
        eoc_bit = (header >> 31) & 0b1

        # Extract the EOF bit (bit 30)
        eof_bit = (header >> 30) & 0b1

        # Extract the sequence number (bits 0-29)
        sequence_number = header & 0x3FFFFFFF  # Mask to get lower 30 bits

        # Convert bits to booleans and return the parsed values
        return Header(eof_bit, eoc_bit, sequence_number)


class Packet:
    def __init__(self, header, payload):
        self.header = header
        self.payload = payload
        self.retries = 0
        self.retransmit = None


class Protocol(ABC):
    def __init__(self, host, addr: (str, int), file_path):
        self.socket = UDPClient(host, RANDOM_HOST)
        self.addr = addr
        self.file_path = file_path
        self.protocol_bit = None
        self.file = FileClient(file_path)
        self.eoc = 0

    @abstractmethod
    def start_upload(self, uploading_status):
        pass

    @abstractmethod
    def start_download(self, downloading_status):
        pass

    @staticmethod
    @abstractmethod
    def get_header_value():
        pass

    def answer_connection(self):
        logger.info("Answering client request")
        error_bite = 0
        error_code = 0
        answer_header = bytearray()
        first_byte = (error_bite << 7) | error_code
        answer_header.append(first_byte)
        self.socket.send_message_to(answer_header, self.addr)

    def __receive_confirmation(self):
        logger.info("Waiting for confirmation")
        status, new_addr = self.socket.receive_message(1)
        first_byte = status[0]
        error = (first_byte >> 7) & 0b00000001
        error_code = first_byte & 0b01111111

        if not error:
            logger.info("Connection successful")
            self.addr = new_addr
            return True
        else:
            logger.error(f"Error code:{error_code} {"No such file in server" if error_code == 2 
            else "File already exists in server" if error_code == 1 else "No memory left"} connection failed")
            return False

    def establish_connection(self, action):
        self.__send_header(action)
        logger.info("Connection request sent")
        return self.__receive_confirmation()

    def __send_header(self, action_bit):
        file_name = os.path.basename(self.file_path)
        file_name_bytes = file_name.encode()  # utf-8 by default
        first_byte = (action_bit << 7) | (self.protocol_bit << 6) | len(
            file_name_bytes)
        header = bytearray()
        header.append(first_byte)
        header.extend(file_name_bytes)

        logger.info(
            f"sending connection request to Addr: "
            f"{(self.addr[0], int(self.addr[1]))}")
        if not self.socket.send_message_to(header,
                                           (self.addr[0], int(self.addr[1]))):
            return 0

    def close(self):
        self.socket.close()


def create_ack(seq_num, eoc):
    # Ensure sequence number is within range (0 to 2^30 - 1)
    if not (0 <= seq_num < 2 ** 30):
        raise ValueError("Sequence number must be in range [0, 2^30 - 1]")

    # Convert the EOC bit to a bit value (0 or 1)
    eoc_bit = 1 if eoc else 0

    # Pack the bits into a 32-bit integer
    header = (eoc_bit << 31) | seq_num

    # Convert the 32-bit integer into a 4-byte array (big-endian)
    header_bytes = header.to_bytes(4, byteorder='big')

    # Return the header as a bytearray
    return bytearray(header_bytes)


def parse_ack(ack):
    if len(ack) != 4:
        raise ValueError("Header bytearray must be exactly 4 bytes long")

    # Convert the bytearray back to a 32-bit integer (big-endian)
    header = int.from_bytes(ack, byteorder='big')

    # Extract the EOC bit (bit 31)
    eoc = (header >> 31) & 1

    # Extract the 30-bit sequence number (bits 0-30)
    sequence_number = header & 0x7FFFFFFF  # Mask for the lower 31 bits

    return eoc, sequence_number

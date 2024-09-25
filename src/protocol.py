from abc import ABC, abstractmethod
import logging
import socket
import os

logger = logging.getLogger(__name__)

RANDOM_HOST = 0

class Protocol(ABC):
    def __init__(self, host, addr: (str,int), file_path):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, RANDOM_HOST))
        self.socket.settimeout(1) 
        self.addr = addr
        self.file_path = file_path
        self.protocol_bit = None

    @abstractmethod
    def start_upload(self):
        pass

    @abstractmethod
    def start_download(self):
        pass

    @staticmethod
    @abstractmethod
    def get_header_value():
        pass

    def answer_connection(self):
        logger.info(f"Answering client request")
        error_bite = 0
        error_code = 0
        answer_header = bytearray()
        first_byte = (error_bite << 7) | error_code
        answer_header.append(first_byte)
        self.socket.sendto(answer_header, self.addr)

    def __receive_confirmation(self):
        logger.info(f"Waiting for confirmation")
        status, new_addr = self.socket.recvfrom(1)
        first_byte =  status[0]
        error = (first_byte >> 7) & 0b00000001
        error_code = first_byte  & 0b01111111

        if not error:
            logger.info(f"Connection successful")
            self.addr = new_addr
            return True
        else:
            # TODO: handle error code
            return False

    def stablish_connection(self, action):
        self.__send_header(action)
        logger.info(f"Connection request sended")
        return self.__receive_confirmation()


    def __send_header(self, action_bit):
        file_name = os.path.basename(self.file_path)
        file_name_bytes = file_name.encode()  # utf-8 by default
        first_byte = (action_bit << 7) | (self.protocol_bit << 6) | len(file_name_bytes)
        header = bytearray()
        header.append(first_byte)
        header.extend(file_name_bytes)
        logger.info(f"Handshake header created\n")

        logger.info(f"Addr: {(self.addr[0], int(self.addr[1]))}\n")
        if not self.socket.sendto(header, (self.addr[0], int(self.addr[1]))):
            return 0

    def close(self):
        self.socket.close()


class StopAndWait(Protocol):
    def __init__(self, host, addr: (str,int), file_path):
        super().__init__(host, addr, file_path)
        self.protocol_bit = 1

    @staticmethod
    def get_header_value():
        return 1

    def start_upload(self):
        logger.info(f"Starting upload with Stop And Wait protocol to Address: {self.addr}")
        with open(self.file_path, 'rb') as file:
            seq_num = 0
            while True:
                data = file.read(1024) # calcular tamaño real 65507 - 4 (header size)
                if not data:
                    eof = 1
                else:
                    eof = 0

                header = self.create_header(seq_num, eof) #falta bit de eoc 
                packet = header + data

                MAX_RETRANSMISSIONS = 15
                retries = 0
                while retries < MAX_RETRANSMISSIONS:
                    try:
                        logger.info(f"Sending Packet: {header}")
                        self.socket.sendto(packet, self.addr)
                        ack, _ = self.socket.recvfrom(2)
                        ack_seq_num = self.parse_ack(ack)
                        if ack_seq_num == seq_num:
                            break
                    except socket.timeout:
                        retries += 1
                        logger.warning("Timeout, resending packet")
                if retries == MAX_RETRANSMISSIONS:
                    logger.error("Max retransmissions reached. Aborting.")
                    return False

                if eof:
                    break

                seq_num = (seq_num + 1) % 2

    def start_download(self):
        logger.info(f"Starting download with Stop And Wait protocol from Address: {self.addr}")
        self.socket.settimeout(15) 
        with open(self.file_path, 'wb') as file: 
            seq_num = 0
            while True:
                packet, _ = self.socket.recvfrom(1026) # calcular tamaño real 65507
                header = packet[:1]
                data = packet[1:]

                recv_seq_num, eof = self.parse_header(header)
                logger.info(f"Receiving Packet: {header}")
                if recv_seq_num == seq_num:
                    file.write(data)
                    ack = self.create_ack(seq_num)
                    self.socket.sendto(ack, self.addr)
                    if eof:
                        break
                    seq_num = (seq_num + 1) % 2  # bit alternante 0 y 1
                else:
                    ack = self.create_ack((seq_num + 1) % 2)
                    self.socket.sendto(ack, self.addr)

    def create_header(self, seq_num, eof):
        header = bytearray()
        first_byte = (seq_num << 7) | (eof << 6)
        header.append(first_byte)
        return header

    def parse_header(self, header):
        first_byte = header[0]
        seq_num = (first_byte >> 7) & 0b00000001
        eof = (first_byte >> 6) & 0b00000001
        return seq_num, eof

    def create_ack(self, seq_num):
        ack = bytearray()
        first_byte = (seq_num << 7)
        ack.append(first_byte)
        return ack

    def parse_ack(self, ack):
        first_byte = ack[0]
        seq_num = (first_byte >> 7) & 0b00000001
        return seq_num



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


import socket
import logging

logger = logging.getLogger(__name__)

HANDSHAKE_TIMEOUT = 5


class UdpHeader:
    def __init__(self) -> None:
        self.dst_host = None
        self.src_port = None
        self.dst_port = None


class UDPClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"attempting to bind to {self.host}:{self.port}")
        self.client.bind((self.host, self.port))
        logger.info(f"UDP client bound to {self.host}:{self.port}")
        self.set_timeout(HANDSHAKE_TIMEOUT)
        self.header = UdpHeader()
        self.packet_number = 1

    def set_timeout(self, timeout: int | None) -> None:
        self.client.settimeout(timeout)

    def send_message_to(self, message: bytearray,
                        dst_addr: (str, int)) -> bool:
        logger.debug(
            f"Sending message of length: {len(message)} to{dst_addr}.")
        self.client.sendto(message, dst_addr)

    def receive_message(self, buffer: int):
        logger.debug("Waiting for packet...")
        try:
            packet, addr = self.client.recvfrom(buffer)
            logger.debug(f"Received packet: {self.packet_number} from {addr}")
            self.packet_number += 1
            return packet, addr
        except socket.timeout:
            logger.debug("Timeout triggered")
            return None, None

    def close(self):
        self.client.close()

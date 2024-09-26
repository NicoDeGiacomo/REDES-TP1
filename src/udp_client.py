import socket
import logging

logger = logging.getLogger(__name__)

HANDSHAKE_TIMEOUT = 5
HANDSHAKE_RETRY = 1

class UdpHeader:
    def __init__(self) -> None:
        self.dst_host = None
        self.src_port = None
        self.dst_port = None


class UDPClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.max_retry = HANDSHAKE_RETRY
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(f"attempting to bind to {self.host}:{self.port}")
        self.client.bind((self.host, self.port))
        logger.info(f"UDP client bound to {self.host}:{self.port}")
        self.set_timeout(HANDSHAKE_TIMEOUT)
        self.header = UdpHeader()

    def set_timeout(self, timeout: int | None) -> None:
        self.client.settimeout(timeout)

    def set_retry(self, retry: int) -> None:
        self.max_retry = retry

    def send_message_to(self, message: bytearray, dst_addr: (str, int)) -> bool:
        retries = 0
        logger.info(f"Sending message of length: {len(message)} to{dst_addr}.")
        self.client.sendto(message, dst_addr)

        
    def receive_message(self, buffer: int):
        logger.info("Waiting for packet...")
        try:
            packet, addr = self.client.recvfrom(buffer)
            logger.info(f"Received packet from {addr}")
            return packet, addr
        except socket.timeout:
            return None, None

    def close(self):
        self.client.close()

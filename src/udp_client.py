import socket
import logging
import struct

logger = logging.getLogger(__name__)


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
        #self.client.bind((self.host, self.port))
        logger.info(f"UDP client bound to {self.host}:{self.port}")
        self.header = UdpHeader()

    def send_message_to(self, message: bytearray, dst_host: str, dst_port: int) -> bool:
        retries = 3     # number of retries
        timeout = 1     # seconds

        self.client.settimeout(timeout)

        while retries > 0:
            try:
                self.client.sendto(message, (dst_host, dst_port))
                logger.info(f"Message sent to {dst_host}:{dst_port}")
                
                ack, addr = self.client.recvfrom(1024)

                if ack == b'ACK':
                    logger.info(f"Received ACK from {addr}")
                    return True
            except socket.timeout:
                logger.error(f"Timeout sending message to {dst_host}:{dst_port}")
                retries -= 1
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                retries -= 1

        logger.error(f"Failed to send message to {dst_host}:{dst_port}")
        self.client.close()

        return False
        
    def receive_message(self) -> tuple[UdpHeader, bytes]:
        # wipe the header
        self.header = UdpHeader()
        logger.info("Waiting for packet...")
        packet, addr = self.client.recvfrom(65565)
        logger.info(f"Received packet from {addr}")
        # Parse UDP header
        self.header.dst_host = addr[0]
        self.header.dst_port = addr[1]
        self.header.src_port = self.port
        # Print UDP header and payload
        logger.info(f"Source Port: {self.header.src_port}")
        logger.info(f"Destination Port: {self.header.dst_port}")
        logger.info(f"Payload: {packet.decode(errors='ignore')}")  # decode as string, ignoring errors for non-text
        return self.header, packet

    def close(self):
        self.client.close()
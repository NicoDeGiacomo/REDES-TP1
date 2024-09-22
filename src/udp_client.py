import socket
import struct
import asyncio

class UdpHeader:
    def __init__(self) -> None:
        self.src_port = None
        self.dst_port = None
        self.udp_length = None
        self.udp_checksum = None

class UDPClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        self.header = UdpHeader()

    async def send_message(self, message: str) -> None:
        self.client.sendto(message.encode(), (self.host, self.port))

    async def receive_message(self) -> tuple[UdpHeader, bytes]:
        # wipe the header
        self.header = UdpHeader()
        packet, addr = self.client.recvfrom(65535)
        # the IP header is the first 20 bytes of the packet
        udp_header = packet[20:28]
        # Unpack UDP header (8 bytes: Source Port, Destination Port, Length, Checksum)
        udp_header_fields = struct.unpack('!HHHH', udp_header)

        # Extract UDP header fields
        self.header.src_port = udp_header_fields[0]
        self.header.dst_port = udp_header_fields[1]
        self.header.udp_length = udp_header_fields[2]
        self.header.udp_checksum = udp_header_fields[3]

        # Extract the payload (everything after the UDP header)
        udp_payload = packet[28:]

        # Print UDP header and payload
        print(f"Source Port: {self.header.src_port}")
        print(f"Destination Port: {self.header.dst_port}")
        print(f"UDP Length: {self.header.udp_length}")
        print(f"UDP Checksum: {self.header.udp_checksum}")
        print(f"Payload: {udp_payload.decode(errors='ignore')}")  # decode as string, ignoring errors for non-text
        return self.header, udp_payload

    def close(self):
        self.client.close()
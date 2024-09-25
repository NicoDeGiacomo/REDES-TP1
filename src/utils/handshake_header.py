
from src.protocol import Protocol
from src.action import Action

class HandshakeHeader:
    def __init__(self, protocol: Protocol, action: Action, file_name: str):
        action_bit = action.value
        protocol_bit = protocol.get_header_value()
        file_name_length = len(file_name)
        file_name_bytes = file_name.encode() # utf-8 by default

        first_byte = (action_bit << 7) | (protocol_bit << 6) | file_name_length

        header = bytearray()
        header.append(first_byte)
        header.extend(file_name_bytes)

        self.protocol = protocol
        self.action = action
        self.file_name = file_name
        self.file_name_length = file_name_length
        self.header = header
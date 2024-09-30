
import socket
import time
from unittest.result import failfast

from tcp_sack import TCPSAck, ACKSACKHeader
from protocol import Header, Packet, logger

class TCPSAckSender(TCPSAck):
    def __init__(self, window_size: int, file_path: str, host: str, addr, initial_seq_num: int) -> None:
        super().__init__(host, addr, file_path, initial_seq_num, window_size)
        self.file.open('rb')
        self.timestamps = {}
        self.socket.set_timeout(0.2) # TODO definir timeout
        self.timeout = 0.2 # TODO definir timeout timestamps
        self.seq_num_to_send = initial_seq_num
        self.last_ack_data = None
        self.fast_retransmit = 0

    def start_upload(self):
        logger.info(f"Starting upload with TCP + SAck protocol to Address: {self.addr}")
        while not self.eoc:
            if self.read_and_send():
                self.listen_for_ack_and_sack()
        logger.info(f"File transmitted successfully")

    def read_and_send(self):
        #self.answer_connection(error, error_code)
        logger.debug(f"reading window TCP + SAck protocol to Address: {self.addr}")

        while len(self.window) < self.window_size and not self.file.eof:
            logger.debug(f"EOF: {self.file.eof}")
            data = self.file.read(1400)
            header = Header(self.file.eof, self.eoc, self.seq_num_to_send)
            packet = Packet(header, data)
            self.socket.send_message_to(header.get_bytes() + data, self.addr)

            timestamp = time.time() + self.timeout
            logger.debug(f"Sending packet {self.seq_num_to_send} at time: {timestamp}")
            self.timestamps[self.seq_num_to_send] = timestamp
            self.window.append(packet)
            self.seq_num_to_send += 1

        # Resend the packets that are due
        due_packets = self.get_due_timestamps()
        # TODO ver que timestamp sea un atributo de la clase Packet
        for packet in due_packets:
            logger.debug(f"TIMEOUT PACKETS")
            if packet.retries >= self.max_retry:
                logger.debug(f"Max retries reached for packet with sequence number: {packet.header.seq_num}. Connection lost.")
                self.file.close()
                super().close()
                return False # TODO validar para salir del thread


            # Retransmitir el paquete
            if packet.retransmit is False:
                continue
            logger.debug(f"Retransmitting packet with sequence number: {packet.header.seq_num}")
            self.socket.send_message_to(packet.header.get_bytes() + packet.payload, self.addr)
            packet.retries += 1
            packet.retransmit = False
            # Actualizar el tiempo de retransmisión
            self.timestamps[packet.header.seq_num] = time.time() + self.timeout


        # Resend packets that are set as retransmit
        if not len(due_packets) and self.fast_retransmit < 3:
            return True

        self.fast_retransmit = 0
        for packet in self.window:
            if not packet.retransmit:
                continue
            if packet.retries >= self.max_retry:
                logger.debug(f"Max retries reached for packet with sequence number: {packet.header.seq_num}. Connection lost.")
                self.eoc = 1
                self.file.close()
                super().close()
                return False
            logger.debug(f"Retransmitting packet with sequence number: {packet.header.seq_num}")
            self.socket.send_message_to(packet.header.get_bytes() + packet.payload, self.addr)
            packet.retries += 1
            packet.retransmit = False
            self.timestamps[packet.header.seq_num] = time.time() + self.timeout
    
    def listen_for_ack_and_sack(self):
        logger.debug(f"Listening for ACKs and SACKs")

        data, addr = self.socket.receive_message(1400)

        if not data:
            data = self.last_ack_data
        else:
            self.last_ack_data = data

        header = ACKSACKHeader.parse_header(data)
        if self.seq_num_to_send == header.seq_num:
            self.fast_retransmit += 1
        else:
            self.fast_retransmit = 0

        logger.debug(f"Received ACK with sequence number: {header.seq_num}")
        self.handle_ack(header)

        if header.eoc:
            logger.debug(f"Received EOC with sequence number: {header.seq_num}")
            self.handle_eoc()

    def handle_ack(self, header: ACKSACKHeader):

        # Remove packets from the window that are smaller than the one ACKed
        logger.debug(f"Window before: {[packet.header.seq_num for packet in self.window]}")
        self.window = [packet for packet in self.window if packet.header.seq_num >= header.seq_num]
        logger.debug(f"Window after: {[packet.header.seq_num for packet in self.window]}")

        # Remove the timestamps that are no longer in the window
        seq_nums_in_window = [packet.header.seq_num for packet in self.window]
        self.timestamps = {k: v for k, v in self.timestamps.items() if k in seq_nums_in_window}

        # Check if there are any SACKs
        if header.sack_length > 0:
            logger.debug(f"SACK Received: {header.sack}")
            for packet in self.window:
                if packet.header.seq_num <= header.sack[header.sack_length - 1]:
                    packet.retransmit = False
                if header.seq_num <= packet.header.seq_num < header.sack[0]:
                    packet.retransmit = True
            for i in range(1, 2 * header.sack_length - 1, 2):
                end = header.sack[i]
                next_start = header.sack[i + 1]
                for packet in self.window:
                    if  end <= packet.header.seq_num < next_start:
                        packet.retransmit = True
        else:
            logger.debug(f"No SACK Received")
            # Resend the acked packet
            for packet in self.window:
                if packet.header.seq_num == header.seq_num:
                    logger.debug(f"ACK number: {packet.header.seq_num}, in current window")
                    packet.retransmit = True



    
    def handle_eoc(self):
        # Close the connection
        logger.info(f"Received EOC. Closing connection")
        self.eoc = 1
        self.file.close()
        super().close()
        

    
    def get_due_timestamps(self):
        logger.debug(f"Current time {time.time()}")
        current_time = time.time()
    
        # Get the items that are due (due > current_time)
        logger.debug(f"Timestamps {self.timestamps}")
        due_items = {k: v for k, v in self.timestamps.items() if v < current_time}
        logger.debug(f"Due timestamps {due_items}")
        
        # Remove due items from the original dictionary
        for k in due_items:
            del self.timestamps[k]
        
        due_packets = []
        for v in self.window:
            if v.header.seq_num in due_items:
                due_packets.append(v)
        return due_packets

    def start_download(self):
        pass


        
        

import time
from tcp_sack import TCPSAck, ACKSACKHeader, parse_header
from protocol import Header, Packet, logger

class TCPSAckSender(TCPSAck):
    def __init__(self, window_size: int, max_retry: int, file_path: str, host: str, addr, initial_seq_num: int) -> None:
        super().__init__(host, addr, file_path, initial_seq_num, window_size, max_retry)
        super().file.open('rb')
        self.timestamps = {}
        self.socket.set_timeout(10) # TODO definir timeout
        self.timeout = 10 # TODO definir timeout timestamps
        self.biggest_seq_num_sacked = initial_seq_num

    def start_upload(self):
        logger.info(f"Starting upload with TCP + SAck protocol to Address: {self.addr}")
        while self.file.eof:
            self.read_and_send()
            self.listen_for_ack_and_sack()

    def read_and_send(self):
        #self.answer_connection(error, error_code)
        logger.info(f"reading window TCP + SAck protocol to Address: {self.addr}")
        seq_num = self.initial_seq_num

        while len(self.window) < self.window_size and not self.file.eof:
            data = self.file.read(1400)
            header = Header(seq_num, self.file.eof, self.eoc)
            packet = Packet(header, data)
            self.socket.send_message_to(header.get_bytes() + data, self.addr)

            timestamp = time.time() + self.timeout
            self.timestamps[seq_num] = timestamp
            self.window.append(packet)
            seq_num += 1

        # Resend the packets that are due
        due_packets = self.get_due_timestamps()
        for packet in due_packets:
            if packet.retries >= self.max_retry:
                logger.info(f"Max retries reached for packet with sequence number: {packet.header.seq_num}. Connection lost.")
                self.file.close()
                super().close()
                return False

            # Retransmitir el paquete
            logger.info(f"Retransmitting packet with sequence number: {packet.header.seq_num}")
            self.socket.send_message_to(packet.header.get_bytes() + packet.data)
            packet.retries += 1
            packet.retrnasmit = False
            # Actualizar el tiempo de retransmisión
            self.timestamps[packet.header.seq_num] = time.time() + self.timeout

        # Resend packets that are set as retransmit
        retransmit_packets = [packet for packet in self.window if packet.retransmit]
        for packet in retransmit_packets:
            if packet.retries >= self.max_retry:
                logger.info(f"Max retries reached for packet with sequence number: {packet.header.seq_num}. Connection lost.")
                self.file.close()
                super().close()
                return False
            logger.info(f"Retransmitting packet with sequence number: {packet.header.seq_num}")
            self.socket.send_message_to(packet.header.get_bytes() + packet.data)
            packet.retries += 1
            packet.retransmit = False
            self.timestamps[packet.header.seq_num] = time.time() + self.timeout
    
    def listen_for_ack_and_sack(self):
        logger.info(f"Listening for ACKs and SACKs")
        while not self.file.eof:
            data, addr = self.socket.receive_message(1400)
            header, biggest_sack_seq_num = parse_header(data)
            if header.eoc:
                logger.info(f"Received EOC with sequence number: {header.seq_num}")
                self.handle_eoc(header)
            logger.info(f"Received ACK with sequence number: {header.seq_num}")
            if biggest_sack_seq_num > self.biggest_seq_num_sacked:
                self.biggest_seq_num_sacked = biggest_sack_seq_num
            self.handle_ack(header)

    def handle_ack(self, header: ACKSACKHeader):
        # Check if the ACK is in the window
        ack_in_window = False
        # TODO solo menores o tambien mayores dropeo?
        for packet in self.window:
            if packet.header.seq_num == header.seq_num:
                ack_in_window = True
                break
        
        if not ack_in_window:
            logger.info(f"Received an out-of-window ACK with sequence number: {header.seq_num}")
            return
        
        # Remove packets from the window that are smaller than the one ACKed
        self.window = [packet for packet in self.window if packet.header.seq_num < header.seq_num]

        # Check if there are any SACKs
        if header.sack_length > 0:
            logger.info(f"Received SACK with length: {header.sack_length}")
            for i in range(0, 2 * header.sack_length, 2):
                start = header.sack[i]
                end = header.sack[i + 1]
                logger.info(f"Received SACK for range: {start} - {end}")
                # Remove the packets in the SACK range from the window
                self.window = [packet for packet in self.window if not start <= packet.header.seq_num < end]
                for packet in self.window:
                    if packet.header.seq_num <= self.biggest_seq_num_sacked
                        packet.retransmit = True
        else:
            # Resend the acked packet
            for packet in self.window:
                if packet.seq_num == header.seq_num:
                    packet.retransmit = True

        # Remove the timestamps that are no longer in the window
        for timestamp in self.timestamps:
            if timestamp not in [packet.header.seq_num for packet in self.window]:
                del self.timestamps[timestamp]
    
    def handle_eoc(self, header: ACKSACKHeader):
        # Close the connection
        # TODO deberia enviar el seq num que pidio antes de cerrar y enviar el ack?
        logger.info(f"Received EOC. Closing connection")
        self.file.close()
        super().close()
        

    
    def get_due_timestamps(self):
        current_time = time.time()
    
        # Get the items that are due (due > current_time)
        due_items = {k: v for k, v in self.timestamps.items() if v > current_time}
        
        # Remove due items from the original dictionary
        for k in due_items:
            del self.timestamps[k]
        
        due_packets = []
        for v in self.window:
            if v.header.seq_num in due_items:
                due_packets.append(v)
        return due_packets


        
        
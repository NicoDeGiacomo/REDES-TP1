
from tcp_sack import ACKSACKHeader, TCPSAck
from protocol import Header, Packet, logger


class TCPSAckKReceiver(TCPSAck):
    def __init__(self, window_size: int, max_retry: int, file_path: str, host: str, addr, initial_seq_num: int) -> None:
        super().__init__(host, addr, file_path, initial_seq_num, window_size, max_retry)
        self.socket.set_timeout(10) # TODO definir timeout
        self.file.open('wb')
        self.eof = 0
        self.eoc = 0
        self.seq_num_to_write = initial_seq_num

    def start_download(self):
        logger.info(f"Starting download with TCP + SAck protocol to Address: {self.addr}")
        while not self.eof and not self.eoc:
            self.list_packets()
            self.send_ack_and_sack()
        super().close()
    
    def list_packets(self):
        logger.debug(f"Listening for packets from {self.addr}")
        data, addr = self.socket.receive_message(1040, self.addr)
        header = Header.parse_header(data[:4]) 
        payload = data[4:]
        self.eoc = header.eoc
        self.eof = header.eof
        if header.seq_num >= self.seq_num_to_write + self.window_size or header.seq_num < self.seq_num_to_write:
            return
        if header.seq_num == self.seq_num_to_write:
            logger.debug(f"Writing packet with seq_num: {header.seq_num}")
            self.file.write(payload)
            self.seq_num_to_write += 1
            self.seq_num_to_write %= 2**30 # copilot me tiro esto quiza nos sirve xd
            packets_written = []
            for packet in self.window:
                if packet.header.seq_num == self.seq_num_to_write:
                    logger.debug(f"Writing packet in window with seq_num: {packet.header.seq_num}")
                    self.file.write(packet.payload)
                    self.seq_num_to_write += 1
                    self.seq_num_to_write %= 2**30
                    packets_written.append(packet)
            for packet in packets_written:
                self.window.remove(packet)
        else:
            logger.debug(f"Adding packet with seq_num: {header.seq_num} to window")
            self.window.append(Packet(header, payload))
        self.winow.sort(key=lambda x: x.header.seq_num)
        self.send_ack_and_sack()
    
    def send_ack_and_sack(self):
        logger.info(f"Sending ACK and SACK to {self.addr}")
        sack = []
        
        for packet in self.window:
            # set first sack with the first packet in the window
            if previous_seq_num == packet.header.seq_num:
                previous_seq_num = self.window[0].header.seq_num
                sack.append(previous_seq_num)
                continue
            # check if packet is contiguous and update previous_seq_num
            if packet.header.seq_num == previous_seq_num + 1:
                previous_seq_num = packet.header.seq_num
            # if not, add the next seq num to "previous_seq_num" and this one to open a new interval
            else:
                 sack.append(previous_seq_num + 1)
                 previous_seq_num = packet.header.seq_num
                 sack.append(previous_seq_num)
        # len of sack is the number of intervals
        sack_len = len(sack) / 2
        header = ACKSACKHeader(self.eoc, self.seq_num_to_write, sack_len, sack)
        logger.debug(f"Sending ACK and SACK to {self.addr}")
        self.socket.send_message_to(header.get_bytes(), self.addr)

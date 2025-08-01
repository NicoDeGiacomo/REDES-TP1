from lib.protocols.TCP_SACK.tcp_sack import ACKSACKHeader, TCPSAck
from lib.protocols.protocol import Header, Packet, logger


class TCPSAckKReceiver(TCPSAck):
    def __init__(self, window_size: int, file_path: str, host: str, addr,
                 initial_seq_num: int) -> None:
        super().__init__(host, addr, file_path, initial_seq_num, window_size)
        self.socket.set_timeout(10)
        self.file.open('wb')
        self.eof = 0
        self.eoc = 0
        self.seq_num_to_write = initial_seq_num

    def start_download(self, downloading_status):
        logger.info(
            f"Starting download with TCP+SAck protocol to Address: "
            f"{self.addr}")
        try:
            while (not self.eof and not self.eoc and
                   (downloading_status is None or
                    downloading_status.is_set())):
                if self.listen_packet():
                    self.send_ack_and_sack()
        except KeyboardInterrupt:
            logger.debug("Keyboard interrupt received, stopping download")
            self.eoc = 1
            header = ACKSACKHeader(self.eoc | self.eof, self.seq_num_to_write,
                                   0, [])
            self.socket.send_message_to(header.get_bytes(), self.addr)

        if downloading_status and not downloading_status.is_set():
            logger.debug("Thread stopped")
            self.eoc = 1
            header = ACKSACKHeader(self.eoc | self.eof, self.seq_num_to_write,
                                   0, [])
            self.socket.send_message_to(header.get_bytes(), self.addr)

        if self.eof:
            logger.info("File downloaded successfully")
            self.file.close()
            super().close()
            return True
        self.file.delete()
        super().close()

    def listen_packet(self):
        logger.debug(
            f"Listening for packets from {self.addr}, expecting seq_num: "
            f"{self.seq_num_to_write}")

        data, addr = self.socket.receive_message(1500)
        if not data:
            self.eoc = 1
            return False

        header = Header.parse_header(data[:4])

        logger.debug(f"Received packet with seq_num: {header.seq_num}")
        payload = data[4:]
        self.eoc = header.eoc
        if self.eoc:
            logger.info(
                f"Received EOC packet from {self.addr}, SENDER DISCONNECTED")
            return False

        logger.debug(
            f"Window before: "
            f"{[packet.header.seq_num for packet in self.window]}")
        if (header.seq_num >= self.seq_num_to_write + self.window_size or
                header.seq_num < self.seq_num_to_write):
            return True
        if header.seq_num == self.seq_num_to_write:
            logger.debug(f"Writing packet with seq_num: {header.seq_num}")
            self.file.write(payload)
            self.seq_num_to_write += 1
            self.seq_num_to_write %= 2 ** 30
            packets_written = []
            self.eof = header.eof
            for packet in self.window:
                if packet.header.seq_num == self.seq_num_to_write:
                    logger.debug(
                        f"Writing packet in window with seq_num: "
                        f"{packet.header.seq_num}")
                    self.eof = packet.header.eof
                    self.file.write(packet.payload)
                    self.seq_num_to_write += 1
                    self.seq_num_to_write %= 2 ** 30
                    packets_written.append(packet)
            for packet in packets_written:
                self.window.remove(packet)
            logger.debug(
                f"Window after: "
                f"{[packet.header.seq_num for packet in self.window]}")
        elif len(self.window) < self.window_size:
            logger.debug(
                f"Adding packet with seq_num: {header.seq_num} to window")
            seq_num_in_window = [p.header.seq_num for p in self.window]
            if header.seq_num not in seq_num_in_window:
                self.window.append(Packet(header, payload))
        self.window.sort(key=lambda x: x.header.seq_num)

        return True

    def send_ack_and_sack(self):
        sack = []

        if len(self.window):

            left_seq_num = self.window[0].header.seq_num

            if len(self.window) == 1:
                sack.append((left_seq_num, left_seq_num + 1))
            else:
                for i in range(1, len(self.window) + 1):
                    if i >= len(self.window):
                        sack.append((left_seq_num,
                                     self.window[i - 1].header.seq_num + 1))
                    elif not (self.window[i - 1].header.seq_num ==
                              self.window[i].header.seq_num - 1):
                        sack.append(
                            (left_seq_num, self.window[i - 1].header.seq_num + 1))
                        left_seq_num = self.window[i].header.seq_num

            logger.debug(
                f"ACK: {self.seq_num_to_write} SACK formed with blocks: "
                f"{sack}")

        # len of sack is the number of intervals
        sack_len = len(sack)

        header = ACKSACKHeader(self.eoc | self.eof, self.seq_num_to_write,
                               sack_len, sack)

        logger.debug(f"Sending ACK {self.seq_num_to_write} and SACK {sack} "
                     f"to {self.addr}")
        self.socket.send_message_to(header.get_bytes(), self.addr)

    def start_upload(self, uploading_status):
        pass

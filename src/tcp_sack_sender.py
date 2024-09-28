
import time
from tcp_sack import TCPSAck
from protocol import Header, Packet, create_header, logger


class TCPSAckSender(TCPSAck):
    def __init__(self, window_size: int, max_retry: int, file_path: str, host: str, addr, initial_seq_num: int) -> None:
        super().__init__(window_size, max_retry, file_path, host, addr, initial_seq_num)
        super().file.open('rb')
        self.timestamps = {}
        self.timeout = 10


    def start_upload(self):
        #self.answer_connection(error, error_code)
        logger.info(f"Starting upload with TCP + SAck protocol to Address: {self.addr}")
        seq_num = self.initial_seq_num

        while True:
            if len(self.window) < self.window_size and not self.file.eof:
                data = self.file.read(1400)
                header = Header(seq_num, self.file.eof, self.eoc)
                packet = Packet(header, data)
                self.socket.send_message_to(header.get_bytes() + data)

                timestamp = time.time() + self.timeout
                self.timestamps[seq_num] = timestamp
                self.window.append(packet)

                seq_num += len(data)

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

                    # Actualizar el tiempo de retransmisión
                    self.timestamps[packet.header.seq_num] = time.time() + self.timeout



    
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


        
        
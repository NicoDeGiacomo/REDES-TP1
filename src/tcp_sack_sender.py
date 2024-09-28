
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
            data = self.file.read(1400)
            header = Header(seq_num, self.file.eof, self.eoc)
            self.socket.send_message_to(header.get_bytes() + data)
            timestamp = time.time() + self.timeout
            self.timestamps[seq_num] = timestamp
            packet = Packet(header, data)
            self.window.append(packet)
    
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


        
        
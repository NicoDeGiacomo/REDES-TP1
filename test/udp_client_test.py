import threading
import unittest
from src.udp_client import UDPClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestUDPClient(unittest.TestCase):
    def run_clients(self, message: str):
        host1, port1 = '127.0.0.1', 9999
        host2, port2 = '127.0.0.1', 8888
        
        client1 = UDPClient(host1, port1)
        client2 = UDPClient(host2, port2)

        def client1_task():
            client1.send_message_to(message, host2, port2)
            header, payload = client1.receive_message()
            self.assertEqual(payload.decode(), message)
            self.assertEqual(header.src_port, port1)
            self.assertEqual(header.dst_host, host2)
            self.assertEqual(header.dst_port, port2)
            return header, payload

        def client2_task():
            header, payload = client2.receive_message()
            client2.send_message_to(payload.decode(), host1, port1)
            self.assertEqual(payload.decode(), message)
            self.assertEqual(header.src_port, port2)
            self.assertEqual(header.dst_host, host1)
            self.assertEqual(header.dst_port, port1)
            return header, payload

        logger.info("Running clients...")
        try:
            thread1 = threading.Thread(target=client1_task)
            thread2 = threading.Thread(target=client2_task)

            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()
        finally:
            client1.close()
            client2.close()

    def test_udp_communication(self):
        logger.info("Starting UDP communication test");
        message = "Hello from Client 1"
        self.run_clients(message)

if __name__ == '__main__':
    unittest.main()
import threading
import unittest
from src.udp_client import UDPClient
from src.accepter import Accepter
from src.protocol import StopAndWait, TCPSAck
from src.action import Action
from src.utils.handshake_header import HandshakeHeader
import logging
import queue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAccepter(unittest.TestCase):
    def run_clients(self, message: str):
        host1, port1 = '127.0.0.1', 9999
        host2, port2 = '127.0.0.1', 8888
        path = './test/'

        accepter = Accepter(path, host1, port1)
        client = UDPClient(host2, port2)

        # Queues to store return values from threads
        client_queue = queue.Queue()
        accepter_queue = queue.Queue()

        def client_task():
            try:
                client.send_message_to(message, host1, port1)
                header, payload = client.receive_message()
                # Store the result in the queue
                client_queue.put((header, payload))
            except Exception as e:
                logger.error(f"Client task failed: {e}")
                client_queue.put((None, None))  # Handle exceptions

        def accepter_task():
            try:
                new_client = accepter.receive_client()
                # Store the result in the queue
                accepter_queue.put(new_client)
            except Exception as e:
                logger.error(f"Accepter task failed: {e}")
                accepter_queue.put(None)  # Handle exceptions

        logger.info("Running clients...")
        try:
            # Start threads
            thread1 = threading.Thread(target=client_task)
            thread2 = threading.Thread(target=accepter_task)

            thread1.start()
            thread2.start()

            thread1.join()
            thread2.join()

            # Retrieve results from the queues
            client_result = client_queue.get()
            accepter_result = accepter_queue.get()

            return client_result, accepter_result
        finally:
            client.close()
            accepter.close()

    def test_accept_client_downloader_SAW(self):
        message = HandshakeHeader(StopAndWait.get_header_value(), Action.DOWNLOAD, 'test.txt').header

        # Get the results from run_clients
        client_result, accepter_result = self.run_clients(message)

        # Perform assertions using the results
        header, payload = client_result

        # Ensure client_task returned a result
        self.assertIsNotNone(header, "Client task did not return a header")
        self.assertIsNotNone(payload, "Client task did not return a payload")

        # Assert client header and payload
        self.assertEqual(payload.decode(), message)
        self.assertEqual(header.src_port, 8888)
        self.assertEqual(header.dst_host, '127.0.0.1')
        self.assertEqual(header.dst_port, 9999)

        # Ensure accepter_task returned a result
        self.assertIsNotNone(accepter_result, "Accepter task did not return a client")
        self.assertTrue(accepter_result.uploading, "Accepter task did not return an uploading client")
        self.assertIsInstance(accepter_result.protocol, StopAndWait, 
                              "Accepter task did not return a StopAndWait protocol")
        
    def test_accept_client_uploader_TCPACK(self):
        message = HandshakeHeader(TCPSAck.get_header_value(), Action.UPLOAD, 'test.txt').header

        # Get the results from run_clients
        client_result, accepter_result = self.run_clients(message)

        # Perform assertions using the results
        header, payload = client_result

        # Ensure client_task returned a result
        self.assertIsNotNone(header, "Client task did not return a header")
        self.assertIsNotNone(payload, "Client task did not return a payload")

        # Assert client header and payload
        self.assertEqual(payload.decode(), message)
        self.assertEqual(header.src_port, 8888)
        self.assertEqual(header.dst_host, '127.0.0.1')
        self.assertEqual(header.dst_port, 9999)

        # Ensure accepter_task returned a result
        self.assertIsNotNone(accepter_result, "Accepter task did not return a client")
        self.assertTrue(accepter_result.uploading, "Accepter task did not return an uploading client")
        self.assertIsInstance(accepter_result.protocol, TCPSAck, 
                              "Accepter task did not return a StopAndWait protocol")

if __name__ == '__main__':
    unittest.main()
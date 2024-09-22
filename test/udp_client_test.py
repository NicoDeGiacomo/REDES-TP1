import asyncio
import unittest
from src.udp_client import UDPClient

class TestUDPClient(unittest.TestCase):
    async def run_clients(self, message: str):
        host1, port1 = '127.0.0.1', 9999
        host2, port2 = '127.0.0.1', 8888
        
        client1 = UDPClient(host1, port1)
        client2 = UDPClient(host2, port2)

        async def client1_task():
            await client1.send_message_to(message, host2, port2)
            header, payload = await client1.receive_message()
            self.assertEqual(payload.decode(), message)
            self.assertEquals(header.src_port, port2)
            self.assertEquals(header.dst_port, port1)
            self.assertIsNotNone(header.udp_length)
            self.assertIsNotNone(header.udp_checksum)
            return header, payload

        async def client2_task():
            header, payload = await client2.receive_message()
            await client2.send_message_to(payload.decode(), host1, port1)
            self.assertEqual(payload.decode(), message)
            self.assertEquals(header.src_port, port1)
            self.assertEquals(header.dst_port, port2)
            self.assertIsNotNone(header.udp_length)
            self.assertIsNotNone(header.udp_checksum)
            return header, payload

        print("Running clients...")
        await asyncio.gather(client1_task(), client2_task())

        client1.close()
        client2.close()

    def test_udp_communication(self):
        loop = asyncio.get_event_loop()
        print("Starting UDP communication test");
        message = "Hello from Client 1"
        loop.run_until_complete(self.run_clients(message))

if __name__ == '__main__':
    unittest.main()
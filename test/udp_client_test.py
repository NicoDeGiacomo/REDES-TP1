import unittest
import asyncio

from src.udp_client import UDPClient


class TestUDPClient(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        self.udp_client = UDPClient("localhost", 12345)
        self.udp_server = UDPClient("localhost", 12344)

    async def test_udp_client_send_message_should_receive_at_server(self):
        await self.udp_client.send_message("Hello, world!")
        header, payload = await self.udp_server.receive_message()
        
        self.assertEqual(header.src_port, 12345)
        self.assertEqual(header.dst_port, 12344)
        self.assertEqual(header.udp_length, 17)
        self.assertEqual(header.udp_checksum, 0)
        self.assertEqual(payload, b"Hello, world!")

if __name__ == '__main__':
    unittest.main()

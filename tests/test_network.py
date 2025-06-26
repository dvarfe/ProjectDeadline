import unittest
import sys
import time
from Deadline.network import Network

sys.path.insert(0, "..")


class TestNetwork(unittest.TestCase):
    """
    Test suite for the Network class.

    This test class validates:
    - Connection establishment
    - Message sending and receiving
    - Proper resource cleanup
    """

    def test_01_connect_to_host_success(self):
        """
        Test successful connection establishment between host and client.

        This test verifies that:
        1. A host can successfully start listening on a port
        2. A client can successfully connect to the host
        3. Both sides properly establish their connection states
        4. All socket objects are properly initialized
        5. Connection cleanup works doesn't throw exceptions
        """
        TIMEOUT = 30
        host_network = Network()
        client_network = Network()
        start_time = time.time()

        host_network.run_host(0, use_bore_flag=False)
        while time.time() - start_time < TIMEOUT:
            if host_network.external_port is not None:
                external_port = host_network.server_socket.getsockname()[1]
                break
        else:
            raise Exception()

        client_network.connect_to_host('localhost', external_port)
        while time.time() - start_time < TIMEOUT:
            if client_network.connection:
                break
        else:
            raise Exception()
        self.assertTrue(client_network.connection)
        self.assertTrue(host_network.connection)
        self.assertIsNotNone(client_network.socket)
        self.assertIsNotNone(host_network.socket)
        self.assertIsNotNone(host_network.external_port)
        self.assertIsNotNone(host_network.external_port)

        client_network.close_all_connections()
        host_network.close_all_connections()

    def test_02_connect_to_host_failure(self):
        """
        Test connection failure to non-existent host.
        """
        network = Network()
        with self.assertRaises(Exception):
            network.connect_to_host('localhost', 99999)

    def test_03_send_msg(self):
        """
        Test message sending, receiving and buffer handling between two Network objects.

        This test validates:
        1. Message sending/receiving in both directions
        2. Partial message reception and buffering
        3. Multiple messages handling
        4. Message parsing into events
        """
        TIMEOUT = 30
        host_network = Network()
        client_network = Network()
        host_network.run_host(0, use_bore_flag=False)
        start_time = time.time()

        # Wait for host to be ready
        while time.time() - start_time < TIMEOUT:
            if host_network.external_port is not None:
                external_port = host_network.server_socket.getsockname()[1]
                break
        else:
            self.fail("Host setup timeout")

        # Connect client
        client_network.connect_to_host('localhost', external_port)

        # Wait for connection
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if client_network.connection and host_network.connection:
                break
        else:
            self.fail("Connection timeout")

        test_message = "test_msg,123\n"
        client_network.send_msg(test_message)
        time.sleep(0.1)

        host_network.check_for_message()
        self.assertEqual(len(host_network.get_active_events()), 1)
        self.assertEqual(host_network.events_dict["test_msg"][0], ["123"])

        partial_msg1 = "partial,msg"
        partial_msg2 = "_part2,456\n"
        client_network.send_msg(partial_msg1)
        time.sleep(0.1)
        host_network.check_for_message()
        self.assertEqual(len(host_network.get_active_events()), 1)

        client_network.send_msg(partial_msg2)
        time.sleep(0.1)
        host_network.check_for_message()
        self.assertEqual(len(host_network.get_active_events()), 2)
        self.assertEqual(host_network.events_dict["partial"][0], ["msg_part2", "456"])

        multi_msg = "msg1,1\nmsg2,2,3\nmsg3\n"
        client_network.send_msg(multi_msg)
        time.sleep(0.1)
        host_network.check_for_message()

        self.assertEqual(len(host_network.get_active_events()), 5)
        self.assertEqual(host_network.events_dict["msg1"][0], ["1"])
        self.assertEqual(host_network.events_dict["msg2"][0], ["2", "3"])
        self.assertEqual(host_network.events_dict["msg3"][0], [])

        host_msg = "host_msg,789\n"
        host_network.send_msg(host_msg)
        time.sleep(0.1)
        client_network.check_for_message()
        self.assertEqual(len(client_network.get_active_events()), 1)
        self.assertEqual(client_network.events_dict["host_msg"][0], ["789"])

        client_network.close_all_connections()
        host_network.close_all_connections()

        if __name__ == '__main__':
            unittest.main()

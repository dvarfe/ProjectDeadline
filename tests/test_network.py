import unittest
import sys
import time
from game_logic import Network

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
        Test message sending and receiving between two Network objects.

        This test validates the core messaging functionality of the Network class:
        1. Establishes a connection between host and client
        2. Tests sending a message from client to host and other way
        3. Verifies that messages are received correctly using check_for_message()
        """
        TIMEOUT = 30
        host_network = Network()
        client_network = Network()
        host_network.run_host(0, use_bore_flag=False)
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if host_network.external_port is not None:
                external_port = host_network.server_socket.getsockname()[1]
                break
        else:
            raise Exception()

        client_network.connect_to_host('localhost', external_port)

        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            if client_network.connection and host_network.connection:
                break
        else:
            raise Exception("Connection timeout")

        test_message = "Hello from client!"
        client_network.send_msg(test_message)
        time.sleep(0.1)

        received_data = host_network.check_for_message()
        self.assertEqual(received_data, test_message)

        response_message = "Hello from host!"
        host_network.send_msg(response_message)
        time.sleep(0.1)
        received_response = client_network.check_for_message()
        self.assertEqual(received_response, response_message)

        client_network.close_all_connections()
        host_network.close_all_connections()


if __name__ == '__main__':
    unittest.main()

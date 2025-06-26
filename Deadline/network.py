import socket
import threading
import subprocess
import time
import re
from typing import List, Optional, Dict

from colors import strip_color

from .localization import _


class Network:
    """
    A class for handling network connections between game clients.

    This class provides functionality for both hosting and connecting to multiplayer
    game sessions.

    Messages follow a format: [Action_name][,params]*\n

            Supported Actions:
                quit
                    - Indicates the player has left the game

                draw [first_player_flag]
                    - Used at game start to determine move order
                    - Params:
                        first_player_flag (int):
                            1 - opponent moves first
                            0 - player moves first

                work [task_idx] [hours]
                    - Player works on specified task
                    - Params:
                        task_idx (int): index of task in task list
                        hours (int): duration of work in hours

                use_card [card_id] [player_pid] [target_idx]
                    - Player uses a card
                    - Params:
                        card_id (int): ID of the card being used
                        player_pid (int): target player ID
                        target_idx (int): Index of target card (-1 if no target)

    Attributes:
        server_socket (socket.socket): Server socket for hosting connections
        socket (socket.socket): Client socket for peer-to-peer communication
        connection (bool): Flag indicating if a connection is established
        external_ip (str): External IP address for the connection
        external_port (int): External port number for the connection
        TIMEOUT (int): Timeout value in seconds for connection attempts
        buffer_size (int): Buffer size in bytes for receiving messages
        events_dict (str): Queue of messages that were received, but not processed
    """

    def __init__(self, buffer_size: int = 1024):
        """
        Initialize a new Network instance.

        Args:
            buffer_size (int, optional): Size of the buffer for receiving messages.
                                       Defaults to 1024 bytes.
        """
        self.server_socket = None
        self.socket = None
        self.connection = False
        self.external_ip = None
        self.external_port = None
        self.TIMEOUT = 30
        self.buffer_size = buffer_size
        self._recv_buffer = b""
        self.events_dict: Dict[str, List[List[str]]] = {
            "quit": [],
            "create_deck": []
        }

    def connect_to_host(self, host: str, port: str):
        """
        Create connection to an existing host.

        Establishes a client connection to a host server. Uses non-blocking socket
        operations to prevent the application from freezing during connection attempts.

        Args:
            host (str): Host IP address or hostname to connect to
            port (str): Port number on the host to connect to

        Raises:
            Exception: Raised when connection fails for any reason
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)
        try:
            while True:
                try:
                    self.socket.connect((host, port))
                    self.connection = True
                    break
                except BlockingIOError:
                    pass
        except Exception as e:
            raise Exception(_(f"Error: {e}"))

    def _accept_connection(self):
        """
        Accept incoming client connections.

        This method is called in a separate thread to handle incoming connections
        to the server socket. When a client connects, it sets up the peer-to-peer
        communication socket and marks the connection as established.
        """
        self.socket, self.client_address = self.server_socket.accept()
        self.socket.setblocking(False)
        self.connection = True

    def _get_bore_output(self, process):
        """
        Monitor bore tunnel process output to extract connection details.

        Reads the output from the bore tunnel process to extract the external port
        number that clients can use to connect.

        Args:
            process (subprocess.Popen): The bore tunnel subprocess to monitor

        Raises:
            ValueError: If bore tunnel fails, times out, or encounters errors
        """
        start_time = time.time()

        while time.time() - start_time < self.TIMEOUT:
            if process.poll() is not None:
                # If the process finished due to some errors
                error = strip_color(process.stderr.read())
                raise ValueError(_("Bore failed: ") + str(error))
            try:
                # If bore have printed something
                output = process.stdout.readline()
                if output:
                    output = strip_color(output)
                    print(output)
                    match = re.search(r"remote_port=(\d+)", output)
                    if match:
                        self.external_port = int(match.group(1))
                        return
            except Exception as e:
                raise ValueError(_("Error reading bore output:") + str(e))
        else:
            process.terminate()
            raise ValueError(_("Bore tunnel setup timed out"))

    def _run_bore_tunnel(self, local_port):
        """
        Start a bore tunnel process for external access.

        Launches a bore tunnel subprocess that creates a public tunnel to the local
        server, allowing external clients to connect over the internet. The tunnel
        connects to bore.pub service.

        Args:
            local_port (int): The local port number to tunnel
        """
        process = subprocess.Popen(
            ["bore", "local", str(local_port), "--to", "bore.pub"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        thread = threading.Thread(target=self._get_bore_output, args=(process,), daemon=True)
        thread.start()

    def run_host(self, port: str, use_bore_flag: bool = False) -> None:
        """
        Start hosting a game server on the specified port.

        Creates a server socket that listens for incoming client connections.
        Can optionally create a public tunnel via bore for external access.

        Args:
            port (str): Port number to bind the server to
            use_bore_flag (bool, optional): Whether to create a public bore tunnel.
            Defaults to False for local-only hosting.

        Note:
            When use_bore_flag is True, the method sets up external access via bore.pub so bore should be installed.
        """
        if not use_bore_flag:
            external_ip = "0.0.0.0"
            external_port = port
        else:
            external_ip = 'bore.pub'
            self._run_bore_tunnel(port)
            external_port = self.external_port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("", port))
        self.server_socket.listen()
        connection_thread = threading.Thread(
            target=self._accept_connection,
            daemon=True
        )
        connection_thread.start()
        self.external_ip, self.external_port = external_ip, external_port

    def send_msg(self, msg: str):
        """
        Send a message to the connected peer.

        Args:
            msg (str): The message string to send to the connected peer
        """
        while True:
            try:
                self.socket.send(msg.encode())
                break
            except BlockingIOError:
                pass

    def send_deck(self, deck) -> None:
        """Send created to oppennt.

        Args:
            deck (List[Card]): deck of cards
        """
        msg = 'create_deck,' + ','.join([card.cid for card in deck])
        self.send_msg(msg)

    def check_for_message(self) -> Optional[str]:
        """
        Check for incoming messages without blocking.

        Raises:
            Exception: If an error occurs while checking for messages
        """
        if not self.socket:
            return None
        try:

            data = self.socket.recv(self.buffer_size)
            if not data:
                return None

            self._recv_buffer += data
            msg_count = self._recv_buffer.count(b"\n")
            valid_messages = self._recv_buffer.split(b"\n", msg_count)
            for msg in valid_messages:
                self.add_event(msg.decode())

        except BlockingIOError:
            return None
        except Exception as e:
            raise Exception(_("Error checking for message:") + str(e))

    def add_event(self, msg: str) -> None:
        """Add Event to events dict.

        Args:
            msg (str): Message containing event info.
        """
        msg_split = msg.split(',')
        event = msg_split[0]
        args = []
        if len(msg_split) > 1:
            args = msg_split[1:]
        self.events_dict[event] = self.events_dict.get(event, []) + [args]

    def close_client_socket(self):
        """
        Close the client/peer socket connection.
        """
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(_("Error closing client socket:") + str(e))
            self.socket = None
            self.connection = False

    def close_server_socket(self):
        """
        Close the server socket.
        """
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception as e:
                print(_("Error closing server socket:") + str(e))
            self.server_socket = None

    def close_all_connections(self):
        """
        Close all network connections and reset network state.
        """
        self.close_client_socket()
        self.close_server_socket()
        self.external_ip = None
        self.external_port = None

    def __del__(self):
        """
        Destructor to ensure proper cleanup of network resources.
        """
        self.close_all_connections()

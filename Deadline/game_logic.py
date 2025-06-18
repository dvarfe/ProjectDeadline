import abc
import enum
import socket
import gettext
import threading
import subprocess
import time
import re

from colors import strip_color

translation = gettext.translation("Dummy", 'po', fallback=True)
_ = translation.gettext  # TODO: Replace dummy with real path and domain

# Typing
Day = int
Days = int
Hours = int
Points = int
PlayerID = ...
Image = ...


class Effect:
    def __init__(self, name: str, description: str, image: Image,
                 period: Days, delay: Days, is_removable: bool,
                 init_event: callable, final_event: callable, everyday_event: callable, init_day: Day):
        """
        An effect applied to the player

        :param name: Effect name
        :param description: Effect description
        :param image: Effect image
        :param period: Duration of the effect
        :param delay: Delay before the effect starts
        :param is_removable: Can the player remove the effect or not
        :param init_event: An event that occurs at the beginning of the effect
        :param final_event: An event that occurs at the end of the effect
        :param everyday_event: An event that occurs every day while the effect is active
        :param init_day: The day when the effect was applied
        """
        self.name = name
        self.description = description
        self.image = image
        self.period = period
        self.delay = delay
        self.is_removable = is_removable
        self.init_event = init_event
        self.final_event = final_event
        self.everyday_event = everyday_event
        self.init_day = init_day


class Task:
    def __init__(self, name: str, description: str, image: Image,
                 difficulty: Hours, award: Points, penalty: Points,
                 event_on_success: callable, event_on_fail: callable):
        """
        A task that can be given to a player

        :param name: Task name
        :param description: Task description
        :param image: Task image
        :param difficulty: The number of hours required to complete the task
        :param award: The number of points awarded for completing the task
        :param penalty: The number of points taken away if the task is failed
        :param event_on_success: An event that occurs if the task is completed
        :param event_on_fail: An event that occurs if the task is failed
        """
        self.name = name
        self.description = description
        self.image = image
        self.difficulty = difficulty
        self.award = award
        self.penalty = penalty
        self.event_on_success = event_on_success
        self.event_on_fail = event_on_fail


class Card(abc.ABC):
    @abc.abstractmethod
    def __init__(self, name: str, description: str, image: Image):
        """
        Playing card

        :param name: Card name
        :param description: Card description
        :param image: Card image
        """
        self.name = name
        self.description = description
        self.image = image


class ActionCard(Card):
    def __init__(self, name: str, description: str, image: Image, cost: Hours,
                 action: callable, req_args: list[str], check_args: callable):
        """
        Action card - one of the card types

        :param name: Card name
        :param description: Card description
        :param image: Card image
        :param cost: The cost of the card in hours
        :param action: Card action
        :param req_args: A list of parameter names that the `action` function accepts
        :param check_args: A function for verifying the correctness of parameters
            passed to the `action` function
        """
        super().__init__(name, description, image)
        self.cost = cost
        self.action = action
        self.req_args = req_args
        self.check_args = check_args


class TaskTarget(enum.Enum):
    """
    Targets for cards
    """
    ME = 1  # Player
    OPPONENT = 2  # Opponent
    BOTH = 3  # Player or his opponent


class TaskCard(Card):
    def __init__(self, name: str, description: str, image: Image, task: Task, valid_targets: TaskTarget):
        """
        Task card - one of the card types

        :param name: Card name
        :param description: Card description
        :param image: Card image
        :param task: A task that is given when the card is played
        :param valid_targets: Valid targets
        """
        super().__init__(name, description, image)
        self.task = task
        self.valid_targets = valid_targets


class Deadline(Task):
    def __init__(self, name: str, description: str, image: Image,
                 difficulty: Hours, award: Points, penalty: Points,
                 event_on_success: callable, event_on_fail: callable,
                 init_day: Day):
        """
        Player's deadline

        :param name: Task name
        :param description: Task description
        :param image: Task image
        :param difficulty: The number of hours required to complete the task
        :param award: The number of points awarded for completing the task
        :param penalty: The number of points taken away if the task is failed
        :param event_on_success: An event that occurs if task is completed
        :param event_on_fail: An event that occurs if task is failed
        :param init_day: The day when the task was issued
        """
        super().__init__(name, description, image, difficulty, award, penalty, event_on_success, event_on_fail)
        self.init_day = init_day
        self.deadline: Day = init_day + difficulty  # The day before which the task must be completed
        self.progress: Hours = 0  # How many hours the player has already worked on the task.

    def work(self, hours: Hours):
        """
        Work on the task for `hours` hours

        :param hours: How long to work on the task
        """
        pass

    def new_day(self):
        """
        Update the deadline when a new day arrives
        """
        pass


class Player:
    def __init__(self, pid: PlayerID, name: str, hours_in_day: Hours):
        """
        A player

        :param pid: Player unique identifier
        :param name: Player name
        :param hours_in_day: Number of free hours per day
        """
        self.pid = pid
        self.name = name
        self.free_hours_today = hours_in_day

        self.score: Points = 0  # Player score
        self.hand: list[Card] = []  # Player's cards
        self.deadlines: list[Deadline] = []  # Player deadlines
        self.effects: list[Effect] = []  # Effects applied to the player
        self.delayed_effects: dict[Day, list[Effect]] = {}  # Delayed effects by the days when they start

    def use_card(self):
        """
        Play a card
        """
        pass

    def manage_time(self):
        """
        Allocate time for tasks
        """
        pass


class Game:
    def __init__(self, player_pid: PlayerID, player_name: str, opponent_pid: PlayerID, opponent_name: str):
        """
        A game. Contains all the data of the current game

        :param player_pid: Player unique identifier
        :param player_name: Player name
        :param opponent_pid: Opponent unique identifier
        :param opponent_name: Opponent name
        """
        self.WIN_THRESHOLD: Points  # The upper score threshold; when it is reached, the player wins
        self.DEFEAT_THRESHOLD: Points  # The lower score threshold; when it is reached, the player loses
        self.DAYS_IN_TERM: Days  # The number of days in a term; the session starts after that number of days
        self.HOURS_IN_DAY_DEFAULT: Hours  # Number of free hours per day with no effects
        self.ALL_TASKS: tuple[Task, ...]  # All tasks in the game
        self.ALL_EFFECTS: tuple[Effect, ...]  # All effects in the game
        self.ALL_CARDS: tuple[Card, ...]  # All cards in the game

        # Load game data
        self.WIN_THRESHOLD, self.DEFEAT_THRESHOLD, self.DAYS_IN_TERM, self.HOURS_IN_DAY_DEFAULT, \
            self.ALL_TASKS, self.ALL_EFFECTS, self.ALL_CARDS = self.__load_data()

        self.me: Player = Player(player_pid, player_name, self.HOURS_IN_DAY_DEFAULT)  # Player
        self.opponent: Player = Player(opponent_pid, opponent_name, self.HOURS_IN_DAY_DEFAULT)  # Opponent

        self.day: Day = 1  # Day number
        self.have_exams: bool = False  # True when players have exams
        self.effects: list[Effect] = []  # Effects affecting both players
        self.deck: list[Card] = self.__create_deck()  # Deck of cards

    def __load_data(self) -> tuple[Points, Points, Days, Hours, tuple[Task, ...], tuple[Effect, ...], tuple[Card, ...]]:
        """
        Load initial game data
        """
        pass

    def __create_deck(self) -> list[Card]:
        """
        Create a deck of cards
        """
        pass

    def get_new_card(self):
        """
        Let player pick a new card from the deck
        """
        pass

    def get_targets(self):
        """
        Get valid targets for an action card
        """
        pass


class Network:
    """
    A class for handling network connections between game clients.

    This class provides functionality for both hosting and connecting to multiplayer
    game sessions.

    Attributes:
        server_socket (socket.socket): Server socket for hosting connections
        socket (socket.socket): Client socket for peer-to-peer communication
        connection (bool): Flag indicating if a connection is established
        external_ip (str): External IP address for the connection
        external_port (int): External port number for the connection
        TIMEOUT (int): Timeout value in seconds for connection attempts
        buffer_size (int): Buffer size in bytes for receiving messages
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

        thread = threading.Thread(target=self._get_bore_output, args=(process), daemon=True)
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

    def check_for_message(self):
        """
        Check for incoming messages without blocking.

        Raises:
            Exception: If an error occurs while checking for messages
        """
        if not self.socket:
            return None
        try:
            data = self.socket.recv(self.buffer_size)
            if data:
                return data.decode()
            else:
                return None
        except BlockingIOError:
            return None
        except Exception as e:
            raise Exception(_("Error checking for message:") + str(e))

    def close_client_socket(self):
        """
        Close the client/peer socket connection.
        """
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                print(f"Error closing client socket: {e}")
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
                print(f"Error closing server socket: {e}")
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

import abc
import enum

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

import os
import abc
import enum
import json
import random


# Typing
Day = int
Days = int
Hours = int
Points = int
Image = ...
EffectID = str
TaskID = str
CardID = str


# Global constants
GAME_CONFIG_FN = os.path.join('Deadline', 'game_config.json')


class Effect:
    def __init__(self, eid: EffectID, name: str, description: str, image: Image,
                 period: Days, delay: Days, is_removable: bool,
                 init_event: callable, final_event: callable, everyday_event: callable, init_day: Day):
        """
        An effect applied to the player.

        :param eid: Effect id.
        :param name: Effect name.
        :param description: Effect description.
        :param image: Effect image.
        :param period: Duration of the effect.
        :param delay: Delay before the effect starts.
        :param is_removable: Can the player remove the effect or not.
        :param init_event: An event that occurs at the beginning of the effect.
        :param final_event: An event that occurs at the end of the effect.
        :param everyday_event: An event that occurs every day while the effect is active.
        :param init_day: The day when the effect was applied.
        """
        self.eid = eid
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
    def __init__(self, tid: TaskID, name: str, description: str, image: Image,
                 difficulty: Hours, deadline: Days, award: Points, penalty: Points,
                 event_on_success: callable, event_on_fail: callable):
        """
        A task that can be given to a player.

        :param tid: Task id.
        :param name: Task name.
        :param description: Task description.
        :param image: Task image.
        :param difficulty: Number of hours required to complete the task.
        :param deadline: Number of days to complete the task.
        :param award: Number of points awarded for completing the task.
        :param penalty: Number of points taken away if the task is failed.
        :param event_on_success: An event that occurs if the task is completed.
        :param event_on_fail: An event that occurs if the task is failed.
        """
        self.tid = tid
        self.name = name
        self.description = description
        self.image = image
        self.difficulty = difficulty
        self.deadline = deadline
        self.award = award
        self.penalty = penalty
        self.event_on_success = event_on_success
        self.event_on_fail = event_on_fail


class Card(abc.ABC):
    @abc.abstractmethod
    def __init__(self, cid: CardID, name: str, description: str, image: Image):
        """
        Playing card.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        """
        self.cid = cid
        self.name = name
        self.description = description
        self.image = image

    @abc.abstractmethod
    def get_info(self):
        """
        Get card information.
        """
        pass


class TaskTarget(enum.Enum):
    """
    Targets for cards.
    """
    ME = 1  # Player
    OPPONENT = 2  # Opponent
    BOTH = 3  # Player or his opponent


class TaskCard(Card):
    def __init__(self, cid: CardID, name: str, description: str, image: Image, task: Task, valid_targets: TaskTarget):
        """
        Task card - one of the card types.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param task: A task that is given when the card is played.
        :param valid_targets: Valid targets.
        """
        super().__init__(cid, name, description, image)
        self.task = task
        self.valid_targets = valid_targets

    def get_info(self):
        pass


class ActionCard(Card):
    def __init__(self, cid: CardID, name: str, description: str, image: Image, cost: Hours,
                 action: callable, req_args: list[str], check_args: callable):
        """
        Action card - one of the card types.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param cost: The cost of the card in hours.
        :param action: Card action.
        :param req_args: A list of parameter names that the `action` function accepts.
        :param check_args: A function for verifying the correctness of parameters
            passed to the `action` function.
        """
        super().__init__(cid, name, description, image)
        self.cost = cost
        self.action = action
        self.req_args = req_args
        self.check_args = check_args

    def get_info(self):
        pass


class Deadline(Task):
    def __init__(self, name: str, description: str, image: Image,
                 difficulty: Hours, deadline: Days, award: Points, penalty: Points,
                 event_on_success: callable, event_on_fail: callable,
                 init_day: Day):
        """
        Player's deadline.

        :param name: Task name.
        :param description: Task description.
        :param image: Task image.
        :param difficulty: Number of hours required to complete the task.
        :param deadline: Number of days to complete the task.
        :param award: Number of points awarded for completing the task.
        :param penalty: Number of points taken away if the task is failed.
        :param event_on_success: An event that occurs if task is completed.
        :param event_on_fail: An event that occurs if task is failed.
        :param init_day: The day when the task was issued.
        """
        super().__init__(name, description, image,
                         difficulty, deadline, award, penalty,
                         event_on_success, event_on_fail)
        self.init_day = init_day
        self.deadline: Day = init_day + deadline  # The day before which the task must be completed
        self.progress: Hours = 0  # How many hours the player has already worked on the task.

    def work(self, hours: Hours):
        """
        Work on the task for `hours` hours.

        :param hours: How long to work on the task.
        """
        pass

    def new_day(self):
        """
        Update the deadline when a new day arrives.
        """
        pass


class Player:
    def __init__(self, name: str, hours_in_day: Hours):
        """
        A player.

        :param name: Player name.
        :param hours_in_day: Number of free hours per day.
        """
        self.name = name
        self.free_hours_today = hours_in_day

        self.score: Points = 0  # Player score
        self.hand: list[Card] = []  # Player's cards
        self.deadlines: list[Deadline] = []  # Player deadlines
        self.effects: list[Effect] = []  # Effects applied to the player
        self.delayed_effects: dict[Day, list[Effect]] = {}  # Delayed effects by the days when they start

    def use_card(self):
        """
        Play a card.
        """
        pass

    def manage_time(self):
        """
        Allocate time for tasks.
        """
        pass


class Game:
    def __init__(self, player_name: str, opponent_name: str):
        """
        A game. Contains all the data of the current game.

        :param player_name: Player name.
        :param opponent_name: Opponent name.
        """
        self.DECK_SIZE: int  # Number of cards in deck
        self.WIN_THRESHOLD: Points  # Upper score threshold; when it is reached, the player wins
        self.DEFEAT_THRESHOLD: Points  # Lower score threshold; when it is reached, the player loses
        self.DAYS_IN_TERM: Days  # Number of days in a term; the session starts after that number of days
        self.HOURS_IN_DAY_DEFAULT: Hours  # Number of free hours per day with no effects
        self.ALL_EFFECTS: tuple[Effect, ...]  # All effects in the game
        self.ALL_TASKS: tuple[Task, ...]  # All tasks in the game
        self.ALL_CARDS: tuple[Card, ...]  # All cards in the game
        # Load game data
        self.__load_data()

        self.player: Player = Player(player_name, self.HOURS_IN_DAY_DEFAULT)  # Player
        self.opponent: Player = Player(opponent_name, self.HOURS_IN_DAY_DEFAULT)  # Opponent

        self.day: Day = 1  # Day number
        self.have_exams: bool = False  # True when players have exams
        self.effects: list[EffectID] = []  # Effects affecting both players
        self.deck: list[CardID] = self.__create_deck()  # Deck of cards

    def __load_data(self):
        """
        Load initial game data.
        """
        with open(GAME_CONFIG_FN, 'r') as f:
            data = json.load(f)
        self.DECK_SIZE = data['DECK_SIZE']
        self.WIN_THRESHOLD = data['WIN_THRESHOLD']
        self.DEFEAT_THRESHOLD = data['DEFEAT_THRESHOLD']
        self.DAYS_IN_TERM = data['DAYS_IN_TERM']
        self.HOURS_IN_DAY_DEFAULT = data['HOURS_IN_DAY_DEFAULT']
        self.ALL_EFFECTS = [Effect(**dct) for dct in data['effects']]
        self.ALL_TASKS = [Task(**dct) for dct in data['tasks']]
        self.ALL_CARDS = [TaskCard(**dct) for dct in data['task_cards']] + \
                         [ActionCard(**dct) for dct in data['action_cards']]

        """
        print(self.DECK_SIZE)
        print(self.WIN_THRESHOLD)
        print(self.DEFEAT_THRESHOLD)
        print(self.DAYS_IN_TERM)
        print(self.HOURS_IN_DAY_DEFAULT)
        print(self.ALL_EFFECTS)
        print(self.ALL_TASKS)
        print(self.ALL_CARDS)
        #"""

    def __create_deck(self) -> list[CardID]:
        """
        Create a deck of cards.
        """
        return random.choices(self.ALL_CARDS, k=self.DECK_SIZE)

    def get_new_card(self):
        """
        Let player pick a new card from the deck.
        """
        pass

    def get_targets(self):
        """
        Get valid targets for an action card.
        """
        pass

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
Image = str
Event = str
EffectID = str
TaskID = str
CardID = str
PlayerID = int

# Global constants
GAME_CONFIG_FN = os.path.join('Deadline', 'game_config.json')


class CardTarget(enum.Enum):
    """
    Kinds of card targets.
    """
    GLOBAL = 0  # Affects everyone
    PLAYER = 1  # Affects the player himself
    OPPONENT = 2  # Affects the opponent
    ANY = 3  # Affects one of the players


str_to_card_target = {'GLOBAL': CardTarget.GLOBAL,
                      'PLAYER': CardTarget.PLAYER,
                      'OPPONENT': CardTarget.OPPONENT,
                      'ANY': CardTarget.ANY}


class Effect:
    def __init__(self, eid: EffectID, name: str, description: str, image: Image,
                 period: Days, delay: Days, is_removable: bool,
                 init_events: list[Event], final_events: list[Event], everyday_events: list[Event]):
        """
        An effect applied to the player.

        :param eid: Effect id.
        :param name: Effect name.
        :param description: Effect description.
        :param image: Effect image.
        :param period: Duration of the effect.
        :param delay: Delay before the effect starts.
        :param is_removable: Can the player remove the effect or not.
        :param init_events: Events that occur at the beginning of the effect.
        :param final_events: Events that occur at the end of the effect.
        :param everyday_events: Events that occur every day while the effect is active.
        """
        self.eid = eid
        self.name = name
        self.description = description
        self.image = image
        self.period = period
        self.delay = delay
        self.is_removable = is_removable
        self.init_events = init_events
        self.final_events = final_events
        self.everyday_events = everyday_events

    def __str__(self) -> str:
        return f'\nEffect #{self.eid}: {self.name}\n' \
               f'    description = "{self.description}"\n' \
               f'    image = {self.image}\n' \
               f'    period = {self.period}\n' \
               f'    delay = {self.delay}\n' \
               f'    is_removable = {self.is_removable}\n' \
               f'    init_events = {self.init_events}\n' \
               f'    final_events = {self.final_events}\n' \
               f'    everyday_events = {self.everyday_events}'

    def __repr__(self) -> str:
        return f'{self.eid} "{self.name}"'


class Task:
    def __init__(self, tid: TaskID, name: str, description: str, image: Image,
                 difficulty: Hours, deadline: Days, award: Points, penalty: Points,
                 events_on_success: list[Event], events_on_fail: list[Event]):
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
        :param events_on_success: Events that occur if the task is completed.
        :param events_on_fail: Events that occur if the task is failed.
        """
        self.tid = tid
        self.name = name
        self.description = description
        self.image = image
        self.difficulty = difficulty
        self.deadline = deadline
        self.award = award
        self.penalty = penalty
        self.events_on_success = events_on_success
        self.events_on_fail = events_on_fail

    def __str__(self) -> str:
        return f'\nTask #{self.tid}: {self.name}\n' \
               f'    description = "{self.description}"\n' \
               f'    image = {self.image}\n' \
               f'    difficulty = {self.difficulty}\n' \
               f'    deadline = {self.deadline}\n' \
               f'    award = {self.award}\n' \
               f'    penalty = {self.penalty}\n' \
               f'    events_on_success = {self.events_on_success}\n' \
               f'    events_on_fail = {self.events_on_fail}'

    def __repr__(self) -> str:
        return f'{self.tid} "{self.name}"'


class Card(abc.ABC):
    @abc.abstractmethod
    def __init__(self, cid: CardID, name: str, description: str, image: Image,
                 valid_target: CardTarget | str, special: bool):
        """
        Playing card.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param valid_target: Valid targets.
        :param special: Can the card be in the deck or not.
            If the card is special, then it can only be obtained as a result of the event.
        """
        self.cid = cid
        self.name = name
        self.description = description
        self.image = image
        self.valid_target = str_to_card_target[valid_target] if isinstance(valid_target, str) else valid_target
        self.special = special

    def __str__(self) -> str:
        return f'\nCard #{self.cid}: {self.name}\n' \
               f'    description = "{self.description}"\n' \
               f'    image = {self.image}\n' \
               f'    valid_target = {self.valid_target}\n' \
               f'    special = {self.special}'

    def __repr__(self) -> str:
        return f'{self.cid} "{self.name}"'


class TaskCard(Card):
    def __init__(self, cid: CardID, name: str, description: str, image: Image,
                 valid_target: CardTarget | str, special: bool, tasks: list[TaskID]):
        """
        Task card - one of the card types.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param valid_target: Valid targets.
        :param special: Can the card be in the deck or not.
            If the card is special, then it can only be obtained as a result of the event.
        :param tasks: Tasks that are given when the card is played.
        """
        super().__init__(cid, name, description, image, valid_target, special)
        self.tasks = tasks


class ActionCard(Card):
    def __init__(self, cid: CardID, name: str, description: str, image: Image,
                 valid_target: CardTarget | str, special: bool, cost: Hours, action: list[EffectID],
                 req_args: list[list[str] | None], check_args: list[str | None]):
        """
        Action card - one of the card types.

        :param cid: Card id.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param valid_target: Valid targets.
        :param special: Can the card be in the deck or not.
            If the card is special, then it can only be obtained as a result of the event.
        :param cost: The cost of the card in hours.
        :param action: Card action.
        :param req_args: Lists of parameter names that the `action` functions accepts.
        :param check_args: Functions for verifying the correctness of parameters
            passed to the `action` functions (if `action` is Event).
        """
        super().__init__(cid, name, description, image, valid_target, special)
        self.cost = cost
        self.action = action
        self.req_args = req_args
        self.check_args = check_args


class Deadline:
    def __init__(self, task: TaskID, init_day: Day, deadline: Days):
        """
        Player's deadline.

        :param task: Task id.
        :param deadline: Number of days to complete the task.
        :param init_day: The day when the task was issued.
        """
        self.task = task
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
    def __init__(self, pid: PlayerID, name: str, hours_in_day: Hours):
        """
        A player.

        :param pid: Player id.
        :param name: Player name.
        :param hours_in_day: Number of free hours per day.
        """
        self.pid = pid
        self.name = name
        self.free_hours_today = hours_in_day

        self.score: Points = 0  # Player score
        self.hand: list[CardID] = []  # Player's cards
        self.deadlines: list[Deadline] = []  # Player deadlines
        self.effects: list[EffectID] = []  # Effects applied to the player
        self.delayed_effects: dict[Day, list[EffectID]] = {}  # Delayed effects by the days when they start

    def __str__(self) -> str:
        return f'\nPlayer #{self.pid}: {self.name}\n' \
               f'    free_hours_today = {self.free_hours_today}\n' \
               f'    score = {self.score}\n' \
               f'    hand = {self.hand}\n' \
               f'    deadlines = {self.deadlines}\n' \
               f'    effects = {self.effects}\n' \
               f'    delayed_effects = {self.delayed_effects}'

    def __repr__(self) -> str:
        return f'Player {self.name}: ' \
               f'hand "{self.hand}" ' \
               f'deadlines {self.deadlines} ' \
               f'effects {self.effects} ' \
               f'delayed_effects {self.delayed_effects}'

    def take_cards_from_deck(self, cards: list[CardID]):
        """
        Get new cards from deck.

        :param cards: Cards ids.
        """
        self.hand += cards

    def use_card(self, idx: int) -> str:
        """
        Use a card.

        :return: Card ID to use a card.
        """
        assert 0 <= idx < len(self.hand)
        return self.hand.pop(idx)

    def spend_time(self, h: Hours):
        """
        Spend `h` hours for something.

        :param h: Number of hours to spend.
        """
        self.free_hours_today -= h

    def apply_effect(self, action, req_args, check_args):
        pass

    def manage_time(self):
        """
        Allocate time for tasks.
        """
        pass


class Game:
    def __init__(self, player_name: str, opponent_name: str, is_first: bool):
        """
        A game. Contains all the data of the current game.

        :param player_name: Player name.
        :param opponent_name: Opponent name.
        :param is_first: 1 if the player plays first.
        """
        self.DECK_SIZE: int  # Number of cards in deck
        self.HAND_SIZE: int  # Number of cards in players hand
        self.WIN_THRESHOLD: Points  # Upper score threshold; when it is reached, the player wins
        self.DEFEAT_THRESHOLD: Points  # Lower score threshold; when it is reached, the player loses
        self.DAYS_IN_TERM: Days  # Number of days in a term; the session starts after that number of days
        self.HOURS_IN_DAY_DEFAULT: Hours  # Number of free hours per day with no effects
        self.ALL_EFFECTS: tuple[Effect, ...]  # All effects in the game
        self.ALL_TASKS: tuple[Task, ...]  # All tasks in the game
        self.ALL_CARDS: tuple[Card, ...]  # All cards in the game
        # Load basic game data
        self.__load_data()
        self.__check_consistency()

        # Initialize players
        self.is_first = is_first  # 1 if the player plays first
        player_pid, opponent_pid = (1, 0) if self.is_first else (0, 1)
        self.player = Player(player_pid, player_name, self.HOURS_IN_DAY_DEFAULT)
        self.opponent = Player(opponent_pid, opponent_name, self.HOURS_IN_DAY_DEFAULT)
        self.players = {player_pid: self.player, opponent_pid: self.opponent}

        self.day: Day = 1  # Day number
        self.have_exams: bool = False  # True when players have exams
        self.effects: list[EffectID] = []  # Effects affecting both players

        self.deck: list[CardID]  # Deck of cards

        self.__create_deck()
        self.__deal_cards()

    def __load_data(self):
        """
        Load basic game data.
        """
        with open(GAME_CONFIG_FN, 'r') as f:
            data = json.load(f)

        self.HAND_SIZE = data['HAND_SIZE']
        self.DECK_SIZE = data['DECK_SIZE']
        assert self.DECK_SIZE >= 2 * self.HAND_SIZE
        assert self.HAND_SIZE > 0
        self.WIN_THRESHOLD = data['WIN_THRESHOLD']
        self.DEFEAT_THRESHOLD = data['DEFEAT_THRESHOLD']
        assert self.WIN_THRESHOLD > self.DEFEAT_THRESHOLD
        assert self.WIN_THRESHOLD > 0
        self.DAYS_IN_TERM = data['DAYS_IN_TERM']
        self.HOURS_IN_DAY_DEFAULT = data['HOURS_IN_DAY_DEFAULT']
        self.ALL_EFFECTS = {dct['eid']: Effect(**dct) for dct in data['effects']}
        self.ALL_TASKS = {dct['tid']: Task(**dct) for dct in data['tasks']}
        self.ALL_CARDS = {dct['cid']: TaskCard(**dct) for dct in data['task_cards']}
        self.ALL_CARDS.update({dct['cid']: ActionCard(**dct) for dct in data['action_cards']})

        """
        print(self.HAND_SIZE)
        print(self.DECK_SIZE)
        print(self.WIN_THRESHOLD)
        print(self.DEFEAT_THRESHOLD)
        print(self.DAYS_IN_TERM)
        print(self.HOURS_IN_DAY_DEFAULT)
        print(self.ALL_EFFECTS)
        print(self.ALL_TASKS)
        print(self.ALL_CARDS)
        #"""

    def __check_consistency(self):
        """
        Check the consistency of configurations between players.
        """
        pass

    def __create_deck(self):
        """
        First player creates a deck of cards and share it with the second one.
        """
        # if self.is_first:
        if True:
            self.deck = random.choices([k for k, v in self.ALL_CARDS.items() if not v.special], k=self.DECK_SIZE)
            pass  # todo: send deck
        else:
            pass  # todo: receive deck

    def __deal_cards(self):
        """
        Deal cards to players.
        """
        self.players[1].take_cards_from_deck(self.deck[:self.HAND_SIZE])
        self.players[0].take_cards_from_deck(self.deck[self.HAND_SIZE:2*self.HAND_SIZE])
        self.deck = self.deck[2*self.HAND_SIZE:]

    def can_take_card(self) -> dict:
        """
        Whether the player can take a card from the deck.

        :return: dict with keys `res` and optionally `msg`.
            `res` is main result (bool).
            `msg` is used in case of a False response to indicate the reason.
        """
        if len(self.deck) == 0:
            return {'res': False, 'msg': 'No more cards in deck!'}
        if len(self.player.hand) >= self.HAND_SIZE:
            return {'res': False, 'msg': 'Cards limit is reached!'}
        return {'res': True}

    def take_card(self):
        """
        Let the player pick a new card from the deck.
        """
        self.player.take_cards_from_deck([self.deck.pop(0)])

    def get_hand_info(self) -> list[CardID]:
        """
        Get list of card ids in player hand.
        """
        return self.player.hand

    def get_card_info(self, cid: CardID) -> Card:
        """
        Get card info by card id.

        :param cid: Card id.
        """
        return self.ALL_CARDS[cid]

    def get_card_type(self, cid: CardID) -> str:
        """
        Get card type: TaskCard or ActionCard.

        :param cid: Card id.
        :return: string 'TaskCard' or 'ActionCard'.
        """
        if isinstance(self.ALL_CARDS[cid], TaskCard):
            return 'TaskCard'
        if isinstance(self.ALL_CARDS[cid], ActionCard):
            return 'ActionCard'
        raise TypeError

    def get_card_targets(self, cid: CardID) -> CardTarget:
        """
        Get valid targets for an action card.

        :param cid: Card id.
        """
        return self.get_card_info(cid).valid_target

    def can_use_card(self, cid: CardID) -> dict:
        """
        Whether the player can use a card from the deck.

        :param cid: Card id.
        :return: dict with keys `res` and optionally `msg`.
            `res` is main result (bool).
            `msg` is used in case of a False response to indicate the reason.
        """
        if self.get_card_type(cid) == 'ActionCard' and self.ALL_CARDS[cid].cost > self.player.free_hours_today:
            return {'res': False, 'msg': 'Not enough free time!'}
        return {'res': True}

    def use_card(self, card_idx_in_hand: int, target_pid: PlayerID = None, target_cid: CardID = None):
        """
        Use a card from hand.

        :param card_idx_in_hand: Card index in hand.
        :param target_pid: Target player id (if card is applied to a player).
        :param target_cid: Target card id (if card is applied to a specific player card).
        """
        cid = self.player.use_card(card_idx_in_hand)
        card = self.ALL_CARDS[cid]
        if card.valid_target == CardTarget.GLOBAL:
            if self.get_card_type(cid) != 'ActionCard':
                raise TypeError
            self.player.spend_time(card.cost)
            self.effects += card.action
        else:
            for effect, args, check_func in zip(card.action, card.req_args, card.check_args):
                self.players[target_pid].effects.add((effect, args, check_func))

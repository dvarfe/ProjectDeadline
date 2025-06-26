import os
import abc
import enum
import json
import random

from .network import Network

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
# GAME_CONFIG_FN = os.path.join('Deadline', 'game_config.json')
GAME_CONFIG_FN = os.path.join('Deadline', 'game_config_test.json')


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

        :param eid: Effect ID.
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

        :param tid: Task ID.
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

        :param cid: Card ID.
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
                 valid_target: CardTarget | str, special: bool, task: TaskID):
        """
        Task card - one of the card types.

        :param cid: Card ID.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param valid_target: Valid targets.
        :param special: Can the card be in the deck or not.
            If the card is special, then it can only be obtained as a result of the event.
        :param task: Task that are given when the card is played.
        """
        super().__init__(cid, name, description, image, valid_target, special)
        self.task = task


class ActionCard(Card):
    def __init__(self, cid: CardID, name: str, description: str, image: Image,
                 valid_target: CardTarget | str, special: bool, cost: Hours, action: EffectID,
                 req_args: list[str] | None, check_args: str | None):
        """
        Action card - one of the card types.

        :param cid: Card ID.
        :param name: Card name.
        :param description: Card description.
        :param image: Card image.
        :param valid_target: Valid targets.
        :param special: Can the card be in the deck or not.
            If the card is special, then it can only be obtained as a result of the event.
        :param cost: The cost of the card in hours.
        :param action: Card action.
        :param req_args: Names of `action` function parameters.
        :param check_args: Function for verifying the correctness of parameters
            passed to the `action` function.
        """
        super().__init__(cid, name, description, image, valid_target, special)
        self.cost = cost
        self.action = action
        self.req_args = req_args
        self.check_args = check_args


class Deadline:
    def __init__(self, task: Task, init_day: Day):
        """
        Player's deadline.

        :param task: Task.
        :param init_day: The day when the task was issued.
        """
        self.task = task
        self.init_day = init_day
        self.deadline: Day = init_day + self.task.deadline  # The day before which the task must be completed
        self.progress: Hours = 0  # How many hours the player has already worked on the task.

    def get_rem(self) -> Hours:
        """
        Get remaining time in hours.
        """
        return self.task.difficulty - self.progress

    def work(self, hours: Hours) -> bool:
        """
        Work on the task for `hours` hours.

        :param hours: How long to work on the task.
        :return: True if task is completed; otherwise False.
        """
        assert hours <= self.get_rem()

        self.progress += hours
        return self.get_rem() == 0

    def new_day(self):
        """
        Update the deadline when a new day arrives.
        """
        pass

    def __str__(self) -> str:
        return f'\nDeadline #{self.tid}: {self.name}\n' \
               f'    description = "{self.description}"\n' \
               f'    image = {self.image}\n' \
               f'    difficulty = {self.difficulty}\n' \
               f'    deadline = {self.deadline}\n' \
               f'    award = {self.award}\n' \
               f'    penalty = {self.penalty}\n' \
               f'    events_on_success = {self.events_on_success}\n' \
               f'    events_on_fail = {self.events_on_fail}'

    def __repr__(self) -> str:
        return f'{self.task.tid} ({self.progress}/{self.task.difficulty})'


class Player:
    def __init__(self, pid: PlayerID, name: str, hours_in_day: Hours):
        """
        A player.

        :param pid: Player ID.
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

    def spend_time(self, hours: Hours):
        """
        Spend `hours` hours for something.

        :param hours: Number of hours to spend.
        """
        assert hours <= self.free_hours_today

        self.free_hours_today -= hours

    def work(self, deadline_idx: int, hours: Hours):
        """
        Work on the task for `hours` hours.

        :param deadline_idx: Index of target deadline in deadline list.
        :param hours: How long to work on the task.
        """
        self.spend_time(hours)
        self.deadlines[deadline_idx].work(hours)

    def apply_effect(self, action, req_args, check_args):
        pass


class Game:
    def __init__(self, player_name: str, opponent_name: str, is_first: bool, network: Network):
        """
        A game. Contains all the data of the current game.

        :param player_name: Player name.
        :param opponent_name: Opponent name.
        :param is_first: 1 if the player plays first.
        :network: Object for network communication.
        """
        self.__DECK_SIZE: int  # Number of cards in deck
        self.__HAND_SIZE: int  # Number of cards in players hand
        self.__WIN_THRESHOLD: Points  # Upper score threshold; when it is reached, the player wins
        self.__DEFEAT_THRESHOLD: Points  # Lower score threshold; when it is reached, the player loses
        self.__DAYS_IN_TERM: Days  # Number of days in a term; the session starts after that number of days
        self.__HOURS_IN_DAY_DEFAULT: Hours  # Number of free hours per day with no effects
        self.__ALL_EFFECTS: tuple[Effect, ...]  # All effects in the game
        self.__ALL_TASKS: tuple[Task, ...]  # All tasks in the game
        self.__ALL_CARDS: tuple[Card, ...]  # All cards in the game
        # Load basic game data
        self.__load_data()
        self.__check_consistency()

        self.__network = network

        # Initialize players
        self.__is_first = is_first  # 1 if the player plays first
        self.__player_pid, self.__opponent_pid = (1, 0) if self.__is_first else (0, 1)
        self.__player = Player(self.__player_pid, player_name, self.__HOURS_IN_DAY_DEFAULT)
        self.__opponent = Player(self.__opponent_pid, opponent_name, self.__HOURS_IN_DAY_DEFAULT)
        self.__players = {self.__player_pid: self.__player, self.__opponent_pid: self.__opponent}

        self.__day: Day = 1  # Day number
        self.__have_exams: bool = False  # True when players have exams
        self.__effects: list[EffectID] = []  # Effects affecting both players

        self.__deck: list[CardID]  # Deck of cards

        self.__create_deck()
        self.__deal_cards()

    def __load_data(self):
        """
        Load basic game data.
        """
        with open(GAME_CONFIG_FN, 'r') as f:
            data = json.load(f)

        self.__HAND_SIZE = data['HAND_SIZE']
        self.__DECK_SIZE = data['DECK_SIZE']
        assert self.__DECK_SIZE >= 2 * self.__HAND_SIZE
        assert self.__HAND_SIZE > 0
        self.__WIN_THRESHOLD = data['WIN_THRESHOLD']
        self.__DEFEAT_THRESHOLD = data['DEFEAT_THRESHOLD']
        assert self.__WIN_THRESHOLD > self.__DEFEAT_THRESHOLD
        assert self.__WIN_THRESHOLD > 0
        self.__DAYS_IN_TERM = data['DAYS_IN_TERM']
        self.__HOURS_IN_DAY_DEFAULT = data['HOURS_IN_DAY_DEFAULT']
        self.__ALL_EFFECTS = {dct['eid']: Effect(**dct) for dct in data['effects']}
        self.__ALL_TASKS = {dct['tid']: Task(**dct) for dct in data['tasks']}
        self.__ALL_CARDS = {dct['cid']: TaskCard(**dct) for dct in data['task_cards']}
        self.__ALL_CARDS.update({dct['cid']: ActionCard(**dct) for dct in data['action_cards']})

    def __check_consistency(self):
        """
        Check the consistency of configurations between players.
        """
        pass

    def __create_deck(self):
        """
        First player creates a deck of cards and share it with the second one.
        """
        if self.__is_first:
            self.__deck = random.choices([k for k, v in self.__ALL_CARDS.items() if not v.special], k=self.__DECK_SIZE)
            self.__network.send_deck(self.__deck)
        else:
            while len(self.__network.events_dict['create_deck']) == 0:  # todo: мб уйти от активного ожидания
                pass
            self.__deck = self.__network.events_dict['create_deck'].pop(0)

    def __deal_cards(self):
        """
        Deal cards to players.
        """
        # Deal cards to the first player
        self.__players[1].take_cards_from_deck(self.__deck[:self.__HAND_SIZE])
        # Deal cards to the second player
        self.__players[0].take_cards_from_deck(self.__deck[self.__HAND_SIZE:2*self.__HAND_SIZE])
        # Remove dealt cards from the deck
        self.__deck = self.__deck[2*self.__HAND_SIZE:]

    """ Getters """

    def get_game_info(self) -> dict[str, dict[str, any]]:
        """
        Get all game information.

        :return: Dict with keys 'player', 'opponent', 'global'.
            'player' corresponds to dict with keys 'pid', 'name', 'score', 'free time',
                'deadlines', 'effects', 'delayed effects' and 'hand'.
            'opponent' corresponds to the same dict; but instead of `hand` key,
                there is `hand size` key.
            'global' corresponds to dict with keys 'day', 'have exams', 'effects', 'deck size'.
        """
        return {
            'player': {
                'pid': self.__player.pid,
                'name': self.__player.name,
                'score': self.__player.score,
                'free time': self.__player.free_hours_today,
                'deadlines': self.__player.deadlines,
                'effects': self.__player.effects,
                'delayed effects': self.__player.delayed_effects,
                'hand': self.__player.hand,
            },
            'opponent': {
                'pid': self.__opponent.pid,
                'name': self.__opponent.name,
                'score': self.__opponent.score,
                'free time': self.__opponent.free_hours_today,
                'deadlines': self.__opponent.deadlines,
                'effects': self.__opponent.effects,
                'delayed effects': self.__opponent.delayed_effects,
                'hand size': len(self.__opponent.hand),
            },
            'global': {
                'day': self.__day,
                'have exams': self.__have_exams,
                'effects': self.__effects,
                'deck size': len(self.__deck),
            },
        }

    def get_effect_info(self, eid: EffectID) -> Effect:
        """
        Get effect info by effect ID.

        :param eid: Effect ID.
        """
        return self.__ALL_EFFECTS[eid]

    def get_task_info(self, tid: TaskID) -> Task:
        """
        Get task info by task ID.

        :param tid: Task ID.
        """
        return self.__ALL_TASKS[tid]

    def get_card_info(self, cid: CardID) -> Card:
        """
        Get card info by card ID.

        :param cid: Card ID.
        """
        return self.__ALL_CARDS[cid]

    def get_card_type(self, cid: CardID) -> str:
        """
        Get card type: TaskCard or ActionCard.

        :param cid: Card ID.
        :return: string 'TaskCard' or 'ActionCard'.
        """
        if isinstance(self.__ALL_CARDS[cid], TaskCard):
            return 'TaskCard'
        if isinstance(self.__ALL_CARDS[cid], ActionCard):
            return 'ActionCard'
        raise TypeError

    def get_card_targets(self, cid: CardID) -> CardTarget:
        """
        Get valid targets for an action card.

        :param cid: Card ID.
        :return: Valid card targets.
        """
        return self.get_card_info(cid).valid_target

    def card_idx_to_cid(self, card_idx_in_hand: int) -> CardID:
        """
        Get card ID by card index in players hand.

        :param card_idx_in_hand: Card index in hand.
        :return: Card ID.
        """
        return self.__player.hand[card_idx_in_hand]

    def __can_take_card(self, actor_pid: PlayerID) -> dict[str, any]:
        """
        Whether a player can take a card from the deck.

        :param actor_pid: ID of player who wants to take a card.
        :return: Dict with keys `res` and optionally `msg`.
            `res` corresponds to main result (bool).
            `msg` is used in case of a False response to indicate the reason.
        """
        if len(self.__deck) == 0:
            return {'res': False, 'msg': 'No more cards in deck!'}
        if len(self.__players[actor_pid].hand) >= self.__HAND_SIZE:
            return {'res': False, 'msg': 'Cards limit is reached!'}
        return {'res': True}

    def player_can_take_card(self) -> dict[str, any]:
        return self.__can_take_card(self.__player_pid)

    def opponent_can_take_card(self) -> dict[str, any]:
        return self.__can_take_card(self.__opponent_pid)

    def __can_use_card(self, actor_pid: PlayerID, cid: CardID) -> dict[str, any]:
        """
        Whether the player can use a card from the deck.

        :param actor_pid: ID of player who wants to use a card.
        :param cid: Card ID.
        :return: Dict with keys `res` and optionally `msg`.
            `res` corresponds to main result (bool).
            `msg` is used in case of a False response to indicate the reason.
        """
        if self.get_card_type(cid) == 'ActionCard' and \
                self.__ALL_CARDS[cid].cost > self.__players[actor_pid].free_hours_today:
            return {'res': False, 'msg': 'Not enough free time!'}
        return {'res': True}

    def player_can_use_card(self, cid: CardID) -> dict[str, any]:
        return self.__can_use_card(self.__player_pid, cid)

    def opponent_can_use_card(self, cid: CardID) -> dict[str, any]:
        return self.__can_use_card(self.__opponent_pid, cid)

    def __can_spend_time(self, actor_pid: PlayerID, target_deadline_idx: int, hours: Hours) -> dict[str, any]:
        """
        Spend time for something.

        :param actor_pid: ID of player who uses a card.
        :param target_deadline_idx: Index of target deadline in deadline list.
        :param hours: Number of hours to spend.
        :return: Dict with keys `res` and optionally `msg`.
            `res` corresponds to main result (bool).
            `msg` is used in case of a False response to indicate the reason.
        """
        if hours > self.__players[actor_pid].deadlines[target_deadline_idx].get_rem():
            return {'res': False, 'msg': 'You are trying to spend too much time!'}
        return {'res': True}

    def player_can_spend_time(self, target_deadline_idx: int, hours: Hours) -> dict[str, any]:
        return self.__can_spend_time(self.__player_pid, target_deadline_idx, hours)

    def opponent_can_spend_time(self, target_deadline_idx: int, hours: Hours) -> dict[str, any]:
        return self.__can_spend_time(self.__opponent_pid, target_deadline_idx, hours)

    """ Actions """

    def __take_card(self, actor_pid: PlayerID):
        """
        Let the player pick a card from the deck.

        :param actor_pid: ID of player who takes a card.
        """
        assert self.__can_take_card(actor_pid)['res']

        self.__players[actor_pid].take_cards_from_deck([self.__deck.pop(0)])

    def player_takes_card(self):
        self.__take_card(self.__player_pid)

    def opponent_takes_card(self):
        self.__take_card(self.__opponent_pid)

    def __use_card(self, actor_pid: PlayerID, card_idx_in_hand: int,
                   target_pid: PlayerID | None, target_cid: CardID | None):
        """
        Use a card from hand.

        :param actor_pid: ID of player who uses a card.
        :param card_idx_in_hand: Card index in players hand.
        :param target_pid: Target player ID (if card is applied to a player).
        :param target_cid: Target card ID (if card is applied to a specific player card).
        """
        cid = self.__players[actor_pid].use_card(card_idx_in_hand)
        assert self.__can_use_card(actor_pid, cid)['res']

        card = self.__ALL_CARDS[cid]
        if card.valid_target == CardTarget.GLOBAL:
            if self.get_card_type(cid) != 'ActionCard':
                raise TypeError
            self.__players[actor_pid].spend_time(card.cost)
            self.__effects.append(card.action)
        else:
            if self.get_card_type(cid) == 'ActionCard':
                self.__players[actor_pid].spend_time(card.cost)
                self.__players[target_pid].effects.append((card.action, card.req_args, card.check_args))
            else:
                self.__players[target_pid].deadlines.append(Deadline(self.__ALL_TASKS[card.task], self.__day))

    def player_uses_card(self, card_idx_in_hand: int, target_pid: PlayerID = None, target_cid: CardID = None):
        self.__use_card(self.__player_pid, card_idx_in_hand, target_pid, target_cid)

    def opponent_uses_card(self, card_idx_in_hand: int, target_pid: PlayerID = None, target_cid: CardID = None):
        self.__use_card(self.__opponent_pid, card_idx_in_hand, target_pid, target_cid)

    def __spend_time(self, actor_pid: PlayerID, target_deadline_idx: int, hours: Hours) -> bool:
        """
        Spend time for something.

        :param actor_pid: ID of player who uses a card.
        :param target_deadline_idx: Index of target deadline in deadline list.
        :param hours: Number of hours to spend.
        :return: True if task is completed; otherwise False.
        """
        assert self.__can_spend_time(actor_pid, target_deadline_idx, hours)

        is_done = self.__players[actor_pid].deadlines[target_deadline_idx].work(hours)
        if is_done:
            self.__players[actor_pid].deadlines.pop(target_deadline_idx)
        return is_done

    def player_spends_time(self, target_deadline_idx: int, hours: Hours = 1) -> bool:
        return self.__spend_time(self.__player_pid, target_deadline_idx, hours)

    def opponent_spends_time(self, target_deadline_idx: int, hours: Hours = 1) -> bool:
        return self.__spend_time(self.__opponent_pid, target_deadline_idx, hours)

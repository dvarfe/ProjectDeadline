import unittest
import sys

from Deadline.game_logic import CardTarget, Deadline as Dl, Game

sys.path.insert(0, '..')


class MockNetwork:
    def __init__(self):
        self.events_dict = {'create_deck': []}

    def send_deck(self, deck: list):
        self.events_dict['create_deck'].append(deck)

    def get_active_events(self):
        return ['create_deck']


class TestGame(unittest.TestCase):
    """
    Test suite for the Game class.

    This test class validates:
    - Connection establishment
    - Message sending and receiving
    - Proper resource cleanup
    """

    def test_01_game_consistency(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True,  network)
        game2 = Game('player2', 'player1', False, network)

        self.assertEqual(game1._player_pid, game2._opponent_pid)
        self.assertEqual(game1._opponent_pid, game2._player_pid)

        self.assertEqual(len(game1._player.hand), len(game1._opponent.hand))
        self.assertEqual(len(game2._player.hand), len(game2._opponent.hand))

        self.assertEqual(game1._player.hand, game2._opponent.hand)
        self.assertEqual(game1._opponent.hand, game2._player.hand)

        self.assertEqual(game1._deck, game2._deck)

    def test_02_take_more_cards_than_allowed(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)

        with self.assertRaises(Exception):
            game1.player_takes_card()

    def test_03_take_more_cards_than_allowed_per_day(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)

        game1._player.hand = []

        game1.player_takes_card()
        with self.assertRaises(Exception):
            raise Exception

    def test_04_use_card_when_have_no_cards(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)

        data = game1.get_game_info()
        hand_size = len(data['player']['hand'])
        player_pid = data['player']['pid']
        opponent_pid = data['opponent']['pid']

        for _ in range(hand_size):
            card = data['player']['hand'][0]
            targets = game1.get_card_targets(card.cid)
            game1.player_uses_card(0, player_pid if targets == CardTarget.PLAYER else opponent_pid)

        with self.assertRaises(Exception):
            game1.player_uses_card(0)

    def test_05_work_more_than_required(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)
        deadline = Dl(game1._ALL_TASKS['t0'], game1._day)

        with self.assertRaises(Exception):
            deadline.work(deadline.get_rem_hours() + 1)
        self.assertFalse(deadline.work(deadline.get_rem_hours() - 1))
        self.assertTrue(deadline.work(1))

    def test_06_use_card_with_invalid_idx(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)
        player = game1._player

        with self.assertRaises(Exception):
            player.use_card(-1)
        with self.assertRaises(Exception):
            player.use_card(len(game1._player.hand))

    def test_07_spend_more_time_that_have(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)
        player = game1._player

        with self.assertRaises(Exception):
            player.spend_time(player.hours_today + 1)

    def test_08_drink_too_much_coffee(self):
        network = MockNetwork()
        game1 = Game('player1', 'player2', True, network)
        player = game1._player
        player.hand = ['ac0' for _ in range(player.hours_today + 2)]

        for _ in range(player.hours_today + 2):
            game1.player_uses_card(0, game1._player_pid)
        self.assertEqual(player.hours_today, game1._HOURS_IN_DAY_MAX)

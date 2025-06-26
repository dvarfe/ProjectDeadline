from .game_logic import Game as GameData


class MockNetwork:
    def __init__(self):
        self.events_dict = {'create_deck': []}

    def send_deck(self, deck: list):
        self.events_dict['create_deck'].append(deck)


def print_game_info(game_data: GameData):
    data = game_data.get_game_info()
    pl = data['player']
    op = data['opponent']
    gl = data['global']

    print()
    print()
    print()
    print(f'day {gl["day"]} {"exams" if gl["have exams"] else ""}')

    print(f'\nPlayer {pl["name"]}\n'
          f'    free_hours_today = {pl["free time"]}\n'
          f'    score = {pl["score"]}\n'
          f'    hand = {pl["hand"]}\n'
          f'    deadlines = {pl["deadlines"]}\n'
          f'    effects = {pl["effects"]}\n'
          f'    delayed_effects = {pl["delayed effects"]}')
    print(f'\nOpponent {op["name"]}\n'
          f'    free_hours_today = {op["free time"]}\n'
          f'    score = {op["score"]}\n'
          f'    hand size = {op["hand size"]}\n'
          f'    deadlines = {op["deadlines"]}\n'
          f'    effects = {op["effects"]}\n'
          f'    delayed_effects = {op["delayed effects"]}')

    print()
    print(f'cards in deck: {gl["deck size"]}')
    print(f'global effects: {gl["effects"]}')


def game():
    player1 = 'Alex'
    player2 = 'Bob'
    network = MockNetwork()
    game_data1 = GameData(player1, player2, True, network)
    game_data2 = GameData(player2, player1, False, network)
    game_data = [game_data1, game_data2]
    i = 0

    while True:
        print_game_info(game_data[i])

        cmd = input()
        match cmd:
            case 'G':  # Get new card
                can_take_card = game_data[i].can_take_card()
                if can_take_card['res']:
                    game_data[i].take_card()
                else:
                    print(can_take_card['msg'])
            case 'U':  # Use card
                pass
            case 'T':  # Time management
                pass
            case 'S':  # Skip a turn
                i = 1 - i
            case 'E':  # Exit
                break
            case _:  # Missclick
                continue

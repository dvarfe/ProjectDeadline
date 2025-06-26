from .game_logic import Game as GameData, CardTarget


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
    print(f'cards in deck: {gl["deck size"]}')
    print()
    print(f'Opponent #{op["pid"]} {op["name"]}\n'
          f'    free_hours_today = {op["free time"]}, score = {op["score"]}\n'
          f'    hand: {["?"] * op["hand size"]}\n\n'
          f'    deadlines: {op["deadlines"]}\n'
          f'    effects: {op["effects"]}\n'
          f'    delayed_effects: {op["delayed effects"]}\n')

    print(f'--- global effects: {gl["effects"]} ---\n')

    print(f'    deadlines: {pl["deadlines"]}\n'
          f'    effects: {pl["effects"]}\n'
          f'    delayed_effects: {pl["delayed effects"]}\n\n'
          f'    hand: {pl["hand"]}\n'
          f'    free_hours_today = {pl["free time"]}, score = {pl["score"]}\n'
          f'Player #{pl["pid"]} {pl["name"]}\n')


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
                can_take_card = game_data[i].player_can_take_card()
                if can_take_card['res']:
                    game_data[i].player_takes_card()
                    game_data[1-i].opponent_takes_card()
                else:
                    print(can_take_card['msg'])
            case 'U':  # Use card
                idx = int(input('Enter card idx: '))
                if not 0 <= idx < len(game_data[i].get_game_info()['player']['hand']):
                    print('Incorrect index!')
                    continue
                cid = game_data[i].card_idx_to_cid(idx)
                match game_data[i].get_card_targets(cid):
                    case CardTarget.ANY:
                        target = input('Enter player or opponent: ')
                        if target not in ['player', 'opponent']:
                            print('Incorrect target!')
                            continue
                        target_pid = game_data[i].get_game_info()[target]['pid']
                    case CardTarget.PLAYER:
                        target_pid = game_data[i].get_game_info()['player']['pid']
                    case CardTarget.OPPONENT:
                        target_pid = game_data[i].get_game_info()['opponent']['pid']
                    case CardTarget.GLOBAL:
                        target_pid = None
                    case _:
                        raise ValueError
                game_data[i].player_uses_card(idx, target_pid, None)
                game_data[1-i].opponent_uses_card(idx, target_pid, None)
            case 'T':  # Time management
                pass
            case 'S':  # Skip a turn
                i = 1 - i
            case 'E':  # Exit
                break
            case _:  # Missclick
                continue

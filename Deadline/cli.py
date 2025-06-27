from .game_logic import Game as GameData, CardTarget


class MockNetwork:
    def __init__(self):
        self.events_dict = {'create_deck': []}

    def send_deck(self, deck: list):
        self.events_dict['create_deck'].append(deck)


def print_game_info(game_data: GameData):
    def print_deadlines(dct):
        deadlines = dct['deadlines']
        if not deadlines:
            print('    no deadlines')
        else:
            print('    deadlines:')
            for deadline in deadlines:
                days_rem = deadline.deadline - gl['day']
                print(f'        {deadline.task.name} ({deadline.progress}/{deadline.task.difficulty}, '
                      f'{days_rem} days remain)')

    def print_effects(dct):
        effects = dct['effects']
        if not effects:
            print('    no effects')
        else:
            print('    effects:')
            for init_day, effect in effects:
                print(f'        {effect.name} ({gl["day"] + effect.period - init_day} days remain)')

    def print_global_effects(dct):
        effects = dct['effects']
        if not effects:
            print('--- no global effects ---')
        else:
            print(f'--- global effects: {[ef.name for _, ef in effects]} ---')

    data = game_data.get_game_info()
    pl = data['player']
    op = data['opponent']
    gl = data['global']

    print('\n\n')
    print(f'====== day {gl["day"]} {"exams" if gl["have exams"] else ""} ======')
    print(f'Cards in deck: {gl["deck size"]}')
    print()

    print(f'{op["name"]} (opponent, id:{op["pid"]})')
    print(f'    score: {op["score"]}')
    print(f'    free_hours_today: {op["free hours"]}')
    print()
    print(f'    hand: {", ".join(["[?]"] * op["hand size"])}')
    print()
    print_deadlines(op)
    print_effects(op)
    print()

    print_global_effects(gl)

    print()
    print_effects(pl)
    print_deadlines(pl)
    print()
    print(f'    hand: {", ".join(card.name for card in pl["hand"])}')
    print()
    print(f'    free_hours_today: {pl["free hours"]}')
    print(f'    score: {pl["score"]}')
    print(f'{pl["name"]} (you, id:{pl["pid"]})')


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
            case 'G':
                can_take_card = game_data[i].player_can_take_card()
                if not can_take_card['res']:
                    print(can_take_card['msg'])
                    continue
                game_data[i].player_takes_card()
                game_data[1-i].opponent_takes_card()
            case 'U':
                idx = int(input('Enter card idx: '))
                if not 0 <= idx < len(game_data[i].get_game_info()['player']['hand']):
                    print('Incorrect index!')
                    continue
                cid = game_data[i].card_idx_to_cid(idx)
                can_use_card = game_data[i].player_can_use_card(cid)
                if not can_use_card['res']:
                    print(can_use_card['msg'])
                    continue
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
            case 'S':
                idx = int(input('Enter deadline idx: '))
                if not 0 <= idx < len(game_data[i].get_game_info()['player']['deadlines']):
                    print('Incorrect index!')
                    continue
                can_spend_time = game_data[i].player_can_spend_time(idx, 1)
                if not can_spend_time['res']:
                    print(can_spend_time['msg'])
                    continue
                game_data[i].player_spends_time(idx, 1)
                game_data[1-i].opponent_spends_time(idx, 1)
            case 'N':
                res = game_data[i].turn_end()
                if res == 'win':
                    print(f'Player {game_data[i].get_game_info()["player"]["name"]} won!')
                    break
                elif res == 'defeat':
                    print(f'Player {game_data[i].get_game_info()["player"]["name"]} lost!')
                    break
                i = 1 - i
                game_data[i].turn_begin()
            case 'E':
                break
            case _:
                continue

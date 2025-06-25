from .game_logic import Game as GameData


def print_game_info(game_data: GameData):
    print()
    print()
    print()

    print(f'day {game_data.day} {"exams" if game_data.have_exams else ""}')

    print(game_data.player)
    print(game_data.opponent)

    print()
    print(f'cards in deck: {game_data.deck}')
    print(f'global effects: {game_data.effects}')


def game():
    player1 = 'Alex'
    player2 = 'Bob'
    game_data1 = GameData(player1, player2, True)
    game_data2 = GameData(player2, player1, False)
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
                pass
            case 'E':  # Exit
                break
            case _:  # Missclick
                continue

        i = 1 - i

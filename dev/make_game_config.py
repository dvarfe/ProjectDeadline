"""Module for game config building."""

import json


def effect(eid, name, description, image, period, delay, is_removable, init_events, final_events, everyday_events):
    """Make effect dict."""
    return {
        'eid': eid,
        'name': name,
        'description': description,
        'image': image,
        'period': period,
        'delay': delay,
        'is_removable': is_removable,
        'init_events': init_events,
        'final_events': final_events,
        'everyday_events': everyday_events,
    }


def task(tid, name, description, image, difficulty, deadline, award, penalty, events_on_success, events_on_fail):
    """Make task dict."""
    return {
        'tid': tid,
        'name': name,
        'description': description,
        'image': image,
        'difficulty': difficulty,
        'deadline': deadline,
        'award': award,
        'penalty': penalty,
        'events_on_success': events_on_success,
        'events_on_fail': events_on_fail,
    }


def task_card(cid, name, description, image, valid_target, special, task):
    """Make task card dict."""
    return {
        'cid': cid,
        'name': name,
        'description': description,
        'image': image,
        'valid_target': valid_target,
        'special': special,
        'task': task,
    }


def action_card(cid, name, description, image, valid_target, special, cost, action, req_args, check_args):
    """Make action card dict."""
    return {
        'cid': cid,
        'name': name,
        'description': description,
        'image': image,
        'valid_target': valid_target,
        'special': special,
        'cost': cost,
        'action': action,
        'req_args': req_args,
        'check_args': check_args,
    }


# Events
event0 = 'special task'
event1 = 'add hours'
event2 = 'take card'
event3 = 'met opt'
event4 = 'kurs failed'
event5 = 'ocean of deadlines'

# Create JSON config
with open('../Deadline/game_config.json', 'w') as f:
    data = {
        'DECK_SIZE': 50,
        'HAND_SIZE': 6,
        'WIN_THRESHOLD': 100,
        'DEFEAT_THRESHOLD': -100,
        'DAYS_IN_TERM': 30,
        'HOURS_IN_DAY_DEFAULT': 16,
        'effects': [
            effect('e0', 'Кофе', 'Выпить кружку кофе', 'coffee.png', 1, 0, False,
                   [(event1, [6])], [], []),
            effect('e1', 'Завал', 'Завал по домашке', 'textures/cards/test.png', 0, 0, False,
                   [(event5, [])], [], [])
        ],
        'tasks': [
            task('t0', 'Матан',          'Обычное задание по матану',                     'textures/cards/test.png',
                 3, 3, 3, -6,  [],                 []),
            task('t1', 'ML',             'Research-задание по ML',                        'textures/cards/test.png',
                 5, 7, 5, -5,  [(event0, ['t2'])], []),
            task('t2', 'Кросс-проверка', 'Нужно проверить 3 чужих решения домашки по ML', 'textures/cards/test.png',
                 1, 7, 0, -5,  [],                 []),
            task('t3', 'Экономика',      'Доклад по экономике',                           'textures/cards/test.png',
                 4, 7, 4, -10, [(event2, [])],     []),
            task('t4', 'Научка',         'Пришли правки от научника',                     'textures/cards/test.png',
                 1, 3, 1, -2,  [],                 []),
            task('t5', 'Метопты',        'Нужно сделать пару задач по метоптам',          'textures/cards/test.png',
                 2, 7, 0, 0,   [(event3, ['t5'])], []),
            task('t6', 'Курсовая',       'Никогда не поздно начать...',                   'textures/cards/test.png',
                 60, 20, 80, 0, [],                [(event4, ['t6'])]),
        ],
        'task_cards': [
            task_card('tc0', 'Матан',          'Обычное задание по матану',
                      'textures/cards/test.png', 'OPPONENT', False, 't0'),
            task_card('tc1', 'ML',             'Research-задание по ML',
                      'textures/cards/test.png', 'OPPONENT', False, 't1'),
            # task_card('tc2', 'Кросс-проверка', 'Нужно проверить 3 чужих решения домашки по ML',
            #           'textures/cards/test.png', 'PLAYER',   True,  't2'),
            task_card('tc3', 'Экономика',      'Доклад по экономике',
                      'textures/cards/test.png', 'OPPONENT', False, 't3'),
            task_card('tc4', 'Научка',         'Пришли правки от научника',
                      'textures/cards/test.png', 'OPPONENT', False, 't4'),
            task_card('tc5', 'Метопты',        'Нужно сделать пару задач по метоптам',
                      'textures/cards/test.png', 'OPPONENT', False, 't5'),
            task_card('tc6', 'Курсовая',       'Никогда не поздно начать...',
                      'textures/cards/test.png', 'OPPONENT', False, 't6'),
        ],
        'action_cards': [
            action_card('ac0', 'Кофе', 'Выпить кружку кофе', 'textures/cards/coffee.png', 'PLAYER',
                        False, 0, 'e0', [], []),
            action_card('ac1', 'Завал', 'Завал по домашке', 'textures/cards/test.png', 'OPPONENT',
                        False, 0, 'e1', [], []),
        ],
    }
    json.dump(data, f, ensure_ascii=False, indent=2)

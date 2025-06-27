import json


def effect(eid, name, description, image, period, delay, is_removable, init_events, final_events, everyday_events):
    """
    Make effect dict.
    """
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
    """
    Make task dict.
    """
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
    """
    Make task card dict.
    """
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
    """
    Make action card dict.
    """
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
event0 = 'self._Game__take_special_task(pid, %s)'
event1 = 'self._Game__players[pid].free_hours_today += %s'
event2 = 'self._Game__players[pid].free_hours_today -= %s'

# Check functions
check0 = 'True'

# Create JSON config
with open('../Deadline/game_config.json', 'w') as f:
    data = {
        'DECK_SIZE': 50,
        'HAND_SIZE': 6,
        'WIN_THRESHOLD': 200,
        'DEFEAT_THRESHOLD': -200,
        'DAYS_IN_TERM': 30,
        'HOURS_IN_DAY_DEFAULT': 16,
        'effects': [
            effect('e0', 'Кофе', 'Выпить кружку кофе', 'coffee.png', 1, 0, False,
                   [(event1 % '6', [], check0)], [(event2 % '6', [], check0)], []),
        ],
        'tasks': [
            task('t0', 'Матан',          'Обычное задание по матану',                     'textures/cards/test.png',
                 3, 3, 3, -6, [],                              []),
            task('t1', 'ML',             'Research-задание по ML',                        'textures/cards/test.png',
                 5, 7, 5, -5, [(event0 % '"t2"', [], check0)], []),
            task('t2', 'Кросс-проверка', 'Нужно проверить 3 чужих решения домашки по ML', 'textures/cards/test.png',
                 1, 7, 0, -5, [],                              []),
        ],
        'task_cards': [
            task_card('tc0', 'Матан',          'Обычное задание по матану',
                      'textures/cards/test.png', 'OPPONENT', False, 't0'),
            task_card('tc1', 'ML',             'Research-задание по ML',
                      'textures/cards/test.png', 'OPPONENT', False, 't1'),
            # task_card('tc2', 'Кросс-проверка', 'Нужно проверить 3 чужих решения домашки по ML',
            #           'textures/cards/test.png', 'PLAYER',   True,  't2'),
        ],
        'action_cards': [
            action_card('ac0', 'Кофе', 'Выпить кружку кофе', 'coffee.png', 'PLAYER', False, 0, 'e0', [], []),
        ],
    }
    json.dump(data, f, ensure_ascii=False, indent=2)

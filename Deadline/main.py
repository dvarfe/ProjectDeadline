import argparse

from .game import Game
from .scene import MainMenu
from .cli import game as game_cli


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', choices=['play', 'debug'], default='debug',
                        help='Mode: `play` with GUI - for playing, `debug` with no GUI - for debugging.')
    return parser.parse_args()


def main_gui():
    """
    GUI mode for players.
    """
    g = Game(MainMenu)
    g.run()


def main_cli():
    """
    CLI mode for debugging.
    """
    game_cli()


if __name__ == '__main__':
    args = get_args()
    if args.mode == 'play':
        main_gui()
    else:
        main_cli()

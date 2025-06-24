from .game import Game
from .scene import MainMenu


def main():
    g = Game(MainMenu)
    g.run()


if __name__ == '__main__':
    main()

import abc
import pygame as pg
from game import Game, Text, Anchor, SceneSwitchButton, ExitButton
from game_logic import _


class Scene(abc.ABC):
    """
    Abstract base class representing a game scene/screen.

    All game scenes should inherit from this class and implement the abstract methods.

    Attributes:
        game (Game): Reference to the main Game instance.
    """

    def __init__(self, game: Game):
        self.game = game

    @abc.abstractmethod
    def run(self):
        """Main scene loop method that coordinates event checking, updating and drawing."""

        self.check_events()
        self.update_scene()
        self.draw_scene()

    @abc.abstractmethod
    def check_events(self):
        """Check and handle all relevant input events for this scene."""
        pass

    @abc.abstractmethod
    def update_scene(self):
        """Update the scene state (game logic, animations, etc.)."""
        pass

    @abc.abstractmethod
    def draw_scene(self):
        """Draw all scene elements to the game canvas."""
        pass


class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Main menu'))

        self.title = Text(
            game,
            (self.game.window_size[0] / 2, self.game.window_size[1] / 8),
            Anchor.CENTRE,
            _("Deadline"),
            150)

        button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Host game"),
            80)

        self.button_host_game = SceneSwitchButton(
            game,
            HostScene,
            (600, 120),
            (self.game.window_size[0] / 2, self.game.window_size[1] / 16 * 5),
            Anchor.CENTRE,
            None,
            button_text,
            Anchor.CENTRE)

        button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Connect"),
            80)

        self.button_connect = SceneSwitchButton(
            game,
            ConnectScene,
            (600, 120),
            (self.game.window_size[0] / 2, self.game.window_size[1] / 16 * 7),
            Anchor.CENTRE,
            None,
            button_text,
            Anchor.CENTRE)

        button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Settings"),
            80)

        self.button_settings = SceneSwitchButton(
            game,
            SettingsScene,
            (600, 120),
            (self.game.window_size[0] / 2, self.game.window_size[1] / 16 * 9),
            Anchor.CENTRE,
            None,
            button_text,
            Anchor.CENTRE)

        button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Exit"),
            80)

        self.button_exit = ExitButton(
            game,
            (600, 120),
            (self.game.window_size[0] / 2, self.game.window_size[1] / 16 * 11),
            Anchor.CENTRE,
            None,
            button_text,
            Anchor.CENTRE)

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        self.button_host_game.check_event()
        self.button_connect.check_event()
        self.button_settings.check_event()
        self.button_exit.check_event()

    def update_scene(self):
        self.button_host_game.update()
        self.button_connect.update()
        self.button_settings.update()
        self.button_exit.update()

    def draw_scene(self):
        self.game.canvas.fill((255, 255, 255))

        self.title.draw()
        self.button_host_game.draw()
        self.button_connect.draw()
        self.button_settings.draw()
        self.button_exit.draw()

        self.game.blit_screen()


class HostScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Host game'))

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        pass

    def update_scene(self):
        pass

    def draw_scene(self):
        self.game.canvas.fill((0, 0, 0))
        self.game.blit_screen()


class ConnectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Connect'))

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        pass

    def update_scene(self):
        pass

    def draw_scene(self):
        self.game.canvas.fill((0, 0, 0))
        self.game.blit_screen()


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Settings'))

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        pass

    def update_scene(self):
        pass

    def draw_scene(self):
        self.game.canvas.fill((0, 0, 0))
        self.game.blit_screen()


class EmptyScene(Scene):
    def __init__(self, game):
        pg.display.set_caption('Empty')
        super().__init__(game)

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        pass

    def update_scene(self):
        pass

    def draw_scene(self):
        self.game.canvas.fill((0, 0, 0))
        self.game.blit_screen()

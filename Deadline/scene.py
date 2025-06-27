import abc
import pygame as pg
import locale
from .game import Game, Text, Anchor, TextField, BackButton, ChooseLanguageButton, \
    SceneSwitchButton, ExitButton, ConnectButton, CheckBoxButton, Card
from .game import _
import Deadline.game_logic as gl


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


STICKYNOTE_BUTTON_IMAGES_PATHS = ["./textures/button_idle.png",
                                  "./textures/button_hover.png", "./textures/button_pressed.png"]


class MainMenu(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Main menu'))

        self.stickynote_button_images = list(map(pg.image.load, STICKYNOTE_BUTTON_IMAGES_PATHS))

        self.title = Text(
            game,
            (self.game.window_size[0] // 2, self.game.window_size[1] // 8),
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
            (600, 325),
            (self.game.window_size[0] // 3, self.game.window_size[1] // 16 * 6),
            Anchor.CENTRE,
            self.stickynote_button_images,
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
            (600, 325),
            (self.game.window_size[0] // 3, self.game.window_size[1] // 16 * 12),
            Anchor.CENTRE,
            self.stickynote_button_images,
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
            (600, 325),
            (self.game.window_size[0] // 3 * 2, self.game.window_size[1] // 16 * 6),
            Anchor.CENTRE,
            self.stickynote_button_images,
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
            (600, 325),
            (self.game.window_size[0] // 3 * 2, self.game.window_size[1] // 16 * 12),
            Anchor.CENTRE,
            self.stickynote_button_images,
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
        self.buttons = []

        self.buttons.append(BackButton(
            game,
            MainMenu))

        checkbox_pos = self.game.window_size[0] // 32 * 11, self.game.window_size[1] // 16 * 8
        checkbox_text = Text(
            game,
            (checkbox_pos[0] + 70, checkbox_pos[1] + 15),
            Anchor.TOP_LEFT,
            _("Use Bore for connection"),
            30)
        self.bore_checkbox = CheckBoxButton(game,
                                            size=(60, 60),
                                            pos=checkbox_pos,
                                            anchor=Anchor.TOP_LEFT)
        connect_button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Host"),
            80)

        self.host_button = ConnectButton(game,
                                         size=(600, 120),
                                         pos=(self.game.window_size[0] // 32 * 16, self.game.window_size[1] // 16 * 7),
                                         anchor=Anchor.CENTRE,
                                         text=connect_button_text)

        self.port_field = TextField(game,
                                    size=(200, 120),
                                    pos=(self.game.window_size[0] // 32 * 16, self.game.window_size[1] // 16 * 5),
                                    anchor=Anchor.CENTRE,
                                    max_length=5,
                                    placeholder=_('Enter Port')
                                    )

        self.buttons += [self.host_button, self.port_field, self.bore_checkbox]
        self.texts = []
        self.texts.append(Text(
            game,
            (self.game.window_size[0] // 2, self.game.window_size[1] // 8),
            Anchor.CENTRE,
            _("Host Game"),
            150))
        self.texts.append(checkbox_text)

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        for button in self.buttons:
            button.check_event()
        if self.host_button.mousedown:
            try:
                port = int(self.port_field.value)
                self.game.network.run_host(port, use_bore_flag=self.bore_checkbox.clicked)
                print("Успех!")
            except Exception as e:
                print("Ой-ё-ё-юшки, что-то пошло совсем не так!", e)
            self.host_button.mousedown = False
            self.host_button.mousehold = False
        if self.game.network.external_port:
            waiting_for_connection_msg = _("Waiting for connection on ") + \
                str(self.game.network.external_ip) + ":" + str(self.game.network.external_port)
            waiting_for_connection_text = Text(
                self.game,
                (self.game.window_size[0] // 2, self.game.window_size[1] // 4 * 3),
                Anchor.CENTRE,
                waiting_for_connection_msg,
                40)
            self.texts.append(waiting_for_connection_text)

    def update_scene(self):
        for object in self.buttons + self.texts:
            object.update()
        if self.game.network.connection:
            self.game.current_scene = GameScene(self.game)

    def draw_scene(self):
        self.game.canvas.fill("white")
        for object in self.buttons + self.texts:
            object.draw()
        self.game.blit_screen()


class ConnectScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Connect'))
        self.buttons = []

        self.buttons.append(BackButton(
            game,
            MainMenu))

        connect_button_text = Text(
            game,
            (0, 0),
            Anchor.CENTRE,
            _("Connect"),
            80)

        self.connect_button = ConnectButton(game,
                                            size=(600, 120),
                                            pos=(self.game.window_size[0] // 32 * 14,
                                                 self.game.window_size[1] // 16 * 7),
                                            anchor=Anchor.CENTRE,
                                            text=connect_button_text)

        self.ip_field = TextField(game,
                                  size=(600, 120),
                                  pos=(self.game.window_size[0] // 32 * 14, self.game.window_size[1] // 16 * 5),
                                  anchor=Anchor.CENTRE,
                                  placeholder=_('Enter IP')
                                  )
        self.port_field = TextField(game,
                                    size=(200, 120),
                                    pos=(self.game.window_size[0] // 32 * 21, self.game.window_size[1] // 16 * 5),
                                    anchor=Anchor.CENTRE,
                                    max_length=5,
                                    placeholder=_('Enter Port')
                                    )
        self.buttons += [self.connect_button, self.ip_field, self.port_field]

        self.texts = []
        self.texts.append(Text(
            game,
            (self.game.window_size[0] // 2, self.game.window_size[1] // 8),
            Anchor.CENTRE,
            _("Connect"),
            150))

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        for button in self.buttons:
            button.check_event()
        if self.connect_button.mousedown:
            try:
                host = self.ip_field.value
                port = int(self.port_field.value)
                self.game.network.connect_to_host(host, port)
                print("Успех!")
            except Exception as e:
                print("Ой-ё-ё-юшки, что-то пошло совсем не так!", e)
                self.connect_button.mousedown = False
                self.connect_button.mousehold = False
                raise Exception(e)
            self.connect_button.mousedown = False
            self.connect_button.mousehold = False

    def update_scene(self):
        for object in self.buttons + self.texts:
            object.update()
        if self.game.network.connection:
            self.game.current_scene = GameScene(self.game)

    def draw_scene(self):
        self.game.canvas.fill("white")
        for object in self.buttons + self.texts:
            object.draw()
        self.game.blit_screen()


class SettingsScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline - Settings'))
        self.buttons = []
        self.texts = []
        self.cur_locale = locale.getlocale()
        self.texts.append(Text(
            game,
            (self.game.window_size[0] // 2, self.game.window_size[1] // 8),
            Anchor.CENTRE,
            _("Settings"),
            150))

        self.buttons.append(BackButton(
            game,
            MainMenu))
        self.buttons.append(ChooseLanguageButton(game,
                                                 (600, 120),
                                                 (self.game.window_size[0] // 2, self.game.window_size[1] // 16 * 9),
                                                 Anchor.CENTRE))

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        for button in self.buttons:
            button.check_event()
        if self.cur_locale != locale.getlocale():
            self.cur_locale = locale.getlocale()
            self.texts[0] = Text(
                self.game,
                (self.game.window_size[0] // 2, self.game.window_size[1] // 8),
                Anchor.CENTRE,
                _("Settings"),
                150)

    def update_scene(self):
        for object in self.buttons + self.texts:
            object.update()

    def draw_scene(self):
        self.game.canvas.fill("white")
        for objects in self.buttons + self.texts:
            objects.draw()
        self.game.blit_screen()


class GameScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        pg.display.set_caption(_('Deadline'))

        # example scene
        self.game_obj = gl.Game("Player1", "Player2", True, self.game.network)

        self.cardtypes_images = \
            {"TaskCard": pg.image.load("./textures/card_task.png"),
             "ActionCard": pg.image.load("./textures/card_action.png")}

        self.example = Card(
            game,
            self.game_obj,
            self.game_obj.get_game_info()['player']['hand'][0],
            self.cardtypes_images,
            350,
            (self.game.window_size[0] // 2, self.game.window_size[1] // 2),
            Anchor.CENTRE)

    def run(self):
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        pass

    def draw_scene(self):
        self.game.canvas.fill((255, 255, 255))
        self.example.draw()
        self.game.blit_screen()

    def update_scene(self):
        pass


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

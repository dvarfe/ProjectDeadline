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

    Attributes
        game (Game): Reference to the main Game instance.

    """

    def __init__(self, game: Game):
        """Initialize scene.

        Args:
            game (Game): Game instance

        """
        self.game = game

    @abc.abstractmethod
    def run(self):
        """Run main scene loop method that coordinates event checking, updating and drawing."""
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
    """Main Menu scene.

    Args:
        Scene (Scene): Scene.

    """

    def __init__(self, game):
        """Initialize Main Menu scene.

        Args:
            game (Game): Game instance.

        """
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
        """Run main scene loop method that coordinates event checking, updating and drawing."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        """Process input events for all UI buttons."""
        self.button_host_game.check_event()
        self.button_connect.check_event()
        self.button_settings.check_event()
        self.button_exit.check_event()

    def update_scene(self):
        """Update the scene state (game logic, animations, etc.)."""
        self.button_host_game.update()
        self.button_connect.update()
        self.button_settings.update()
        self.button_exit.update()

    def draw_scene(self):
        """Render the main menu: background, title, and buttons."""
        self.game.canvas.fill((255, 255, 255))

        self.title.draw()
        self.button_host_game.draw()
        self.button_connect.draw()
        self.button_settings.draw()
        self.button_exit.draw()

        self.game.blit_screen()


class HostScene(Scene):
    """Scene for hosting a multiplayer game session.

    This scene provides UI elements for:
    - Setting up connection parameters (port number)
    - Choosing connection method (Bore or direct)
    - Starting the game host
    - Returning to main menu
    """

    def __init__(self, game):
        """Initialize the host game scene.

        Args:
            game (Game): Reference to the main game instance.

        """
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
        """Execute one frame of the scene logic."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        """Process input events for all UI buttons."""
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
        """Update the scene state (game logic, animations, etc.)."""
        for object in self.buttons + self.texts:
            object.update()
        if self.game.network.connection:
            self.game.current_scene = GameScene(self.game, is_first=True)

    def draw_scene(self):
        """Render the main menu: background, title, and buttons."""
        self.game.canvas.fill("white")
        for object in self.buttons + self.texts:
            object.draw()
        self.game.blit_screen()


class ConnectScene(Scene):
    """Scene for connecting to a multiplayer game session.

    Provides UI elements for:
    - Entering server connection details (IP and port)
    - Establishing connection
    - Returning to main menu
    """

    def __init__(self, game):
        """Initialize the connection scene.

        Args:
            game (Game): Reference to the main game instance.

        """
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
        """Execute one frame of the scene logic."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        """Process input events for all UI buttons."""
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
        """Update the scene state (game logic, animations, etc.)."""
        for object in self.buttons + self.texts:
            object.update()
        if self.game.network.connection:
            self.game.current_scene = GameScene(self.game, is_first=False)

    def draw_scene(self):
        """Render the main menu: background, title, and buttons."""
        self.game.canvas.fill("white")
        for object in self.buttons + self.texts:
            object.draw()
        self.game.blit_screen()


class SettingsScene(Scene):
    """Game settings configuration scene.

    Provides interface for:
    - Changing game language/regional settings
    - Returning to main menu
    """

    def __init__(self, game):
        """Initialize settings scene with UI elements.

        Args:
            game (Game): Reference to the main game instance.

        Attributes
            buttons (list): Collection of interactive UI buttons
            texts (list): Collection of text elements
            cur_locale (tuple): Current locale settings (language, encoding)

        """
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
        """Execute one frame of the scene logic."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        """Process input events for all UI buttons."""
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
        """Update the scene state (game logic, animations, etc.)."""
        for object in self.buttons + self.texts:
            object.update()

    def draw_scene(self):
        """Render the main menu: background, title, and buttons."""
        self.game.canvas.fill("white")
        for objects in self.buttons + self.texts:
            objects.draw()
        self.game.blit_screen()


class GameScene(Scene):
    """Main gameplay scene handling core game rendering and logic."""

    def __init__(self, game, is_first):
        """Initialize the game scene.

        Args:
            game (Game): Reference to the main game controller instance.
            is_first (bool): True if this player goes first, False otherwise.
        """
        super().__init__(game)
        pg.display.set_caption(_('Deadline'))

        self.game_obj = gl.Game("Player1", "Player2", is_first, self.game.network)

        self.cardtypes_images = {
            "TaskCard": pg.image.load("./textures/card_task.png"),
            "ActionCard": pg.image.load("./textures/card_action.png")
        }

        hand = self.game_obj.get_game_info()['player']['hand']
        self.hand_cards = []
        self.card_height = 210
        self.spacing = 24
        self.num_cards = len(hand)
        card_img = self.cardtypes_images["TaskCard"]
        self.card_width = round(self.card_height * card_img.get_width() / card_img.get_height())
        self.selected_card_idx = None
        self.hovered_card_idx = None
        self.played_cards = []
        self.is_player_turn = is_first
        self.opponent_played_cards = []

        self._layout_hand_cards()

    def _layout_hand_cards(self):
        hand = self.game_obj.get_game_info()['player']['hand']
        self.hand_cards = []
        num_cards = len(hand)
        total_width = num_cards * self.card_width + (num_cards - 1) * self.spacing if num_cards > 0 else 0
        start_x = (self.game.window_size[0] - total_width) // 2 + self.card_width // 2
        y = self.game.window_size[1] - self.card_height // 2 - 80
        for i, card_info in enumerate(hand):
            x = start_x + i * (self.card_width + self.spacing)
            self.hand_cards.append({
                'card': Card(
                    self.game,
                    self.game_obj,
                    card_info,
                    self.cardtypes_images,
                    self.card_height,
                    (x, y),
                    Anchor.CENTRE
                ),
                'pos': (x, y),
                'orig_y': y
            })

    def _layout_played_cards(self):
        num = len(self.played_cards)
        if num == 0:
            return
        spacing = 24
        card_width = self.card_width
        total_width = num * card_width + (num - 1) * spacing
        start_x = (self.game.window_size[0] - total_width) // 2 + card_width // 2
        y = self.game.window_size[1] // 2 + 10
        for i, card in enumerate(self.played_cards):
            x = start_x + i * (card_width + spacing)
            card.move_to((x, y))

    def _layout_opponent_hand(self):
        hand_size = self.game_obj.get_game_info()['opponent']['hand size']
        self.opponent_hand_rects = []
        num_cards = hand_size
        total_width = num_cards * self.card_width + (num_cards - 1) * self.spacing if num_cards > 0 else 0
        start_x = (self.game.window_size[0] - total_width) // 2 + self.card_width // 2
        y = self.card_height // 2 + 40
        for i in range(num_cards):
            x = start_x + i * (self.card_width + self.spacing)
            rect = pg.Rect(0, 0, self.card_width, self.card_height)
            rect.center = (x, y)
            self.opponent_hand_rects.append(rect)

    def run(self):
        """Execute one frame of game loop processing."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        self.hovered_card_idx = None
        if not self.is_player_turn:
            return
        for idx, card_dict in enumerate(self.hand_cards):
            card = card_dict['card']
            rect = card.rect.copy()
            if self.selected_card_idx == idx:
                continue
            if rect.collidepoint(mouse_pos):
                self.hovered_card_idx = idx
                if mouse_pressed:
                    self.selected_card_idx = idx
        if self.selected_card_idx is not None and not mouse_pressed:
            played_card = self.hand_cards[self.selected_card_idx]['card']
            self.game_obj.player_uses_card(self.selected_card_idx)
            cid = played_card.card_info.cid
            target_pid = None
            target_idx = None
            card_idx_in_hand = self.selected_card_idx
            self.game.network.send_use_card(cid, target_pid, target_idx, card_idx_in_hand)
            self.selected_card_idx = None
            self._layout_hand_cards()
            self.played_cards.append(played_card)
            self._layout_played_cards()

    def update_scene(self):
        if not self.is_player_turn:
            event_keys = self.game.network.get_active_events()
            for key in event_keys:
                event_list = self.game.network.events_dict[key]
                while event_list:
                    args = event_list.pop(0)
                    if key == 'use_card':
                        card_idx_in_hand = int(args[3]) if len(args) > 3 else 0
                        self.game_obj.opponent_uses_card(card_idx_in_hand)
                        self._layout_hand_cards()
                        self._layout_played_cards()
                    elif key == 'end_turn':
                        self.is_player_turn = True

    def draw_scene(self):
        self.game.canvas.fill((255, 255, 255))
        self._layout_opponent_hand()
        for rect in self.opponent_hand_rects:
            pg.draw.rect(self.game.canvas, (120, 120, 180), rect, border_radius=16)
            pg.draw.rect(self.game.canvas, (60, 60, 100), rect, width=4, border_radius=16)
        num = len(self.opponent_played_cards)
        if num > 0:
            spacing = 24
            card_width = self.card_width
            total_width = num * card_width + (num - 1) * spacing
            start_x = (self.game.window_size[0] - total_width) // 2 + card_width // 2
            y = self.card_height // 2 + 120
            for i, card in enumerate(self.opponent_played_cards):
                x = start_x + i * (card_width + spacing)
                card.move_to((x, y))
                card.draw()
        for card in self.played_cards:
            card.draw()
        for idx, card_dict in enumerate(self.hand_cards):
            card = card_dict['card']
            x, y = card_dict['pos']
            draw_y = y
            if idx == self.hovered_card_idx:
                draw_y = y - 40
            old_pos = card.pos
            card.move_to((x, draw_y))
            card.draw()
            card.move_to(old_pos)
        self.game.blit_screen()

class EmptyScene(Scene):
    """Placeholder scene used for testing and transitions."""

    def __init__(self, game):
        """Initialize an empty placeholder scene.

        Args:
            game (Game): Reference to the main game controller instance.
        """
        pg.display.set_caption('Empty')
        super().__init__(game)

    def run(self):
        """Execute one frame of scene processing."""
        self.check_events()
        self.update_scene()
        self.draw_scene()

    def check_events(self):
        """Process input events for all UI buttons."""
        pass

    def update_scene(self):
        """Update the scene state(game logic, animations, etc.)."""
        pass

    def draw_scene(self):
        """Render the main menu: background, title, and buttons."""
        self.game.canvas.fill((0, 0, 0))
        self.game.blit_screen()

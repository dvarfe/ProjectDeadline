import enum
import abc
import locale
import gettext
from typing import Dict, List, Optional, Tuple
import pygame as pg
from pygame.typing import ColorLike

_podir = "po"
translation = gettext.translation("Deadline", _podir, fallback=True)

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("Deadline", _podir, ["ru_RU.UTF-8"]),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
}


def _(text):
    return LOCALES[locale.getlocale()].gettext(text)


# Typing
Vector2 = Tuple[int, int]
Point = Vector2

WINDOW_SIZE = (1920, 1080)
DEFAULT_FONT = pg.font.get_default_font()


def get_events_dict() -> Dict[int, List[pg.Event]]:
    """
    Get all Pygame events and organize them in a dictionary by event type.

    Returns:
        dict: A dictionary where keys are event types and values are lists of events.
    """
    events = pg.event.get()
    events_dict: Dict[int, List[pg.Event]] = {}

    for event in events:
        events_dict[event.type] = events_dict.get(event.type, []) + [event]
    return events_dict


class Game():
    """
    Main game class that manages the game loop.

    Attributes:
        window_size (tuple): The size of the game window (width, height).
        canvas (pygame.Surface): The main drawing surface.
        display (pygame.Surface): The display surface.
        default_font (str): The default font name.
        current_scene (Scene): The currently active scene.
        running (bool): Flag indicating if the game is running.
        language (str): Language selected. RU or EN.
    """

    def __init__(self, scene_class):
        """
        Initialize the game with a starting scene.

        Args:
            scene_class: The class of the initial scene to run.
        """

        pg.init()
        self.window_size = WINDOW_SIZE
        self.canvas = pg.Surface(self.window_size)
        self.display = pg.display.set_mode(self.window_size)
        self.default_font = DEFAULT_FONT
        self.current_scene = scene_class(self)
        self.running: bool = True

    def run(self) -> None:
        """Run the main game loop until self.running becomes False."""

        while self.running:
            self.events = get_events_dict()
            if pg.QUIT in self.events.keys():
                self.running = False
            self.current_scene.run()
        pg.quit()

    def blit_screen(self) -> None:
        """Update the display by blitting the canvas to the display surface."""

        self.display.blit(self.canvas, (0, 0))
        pg.display.update()


class Anchor(enum.Enum):
    """
    Enumeration for different anchor points of UI elements.

    Used for positioning elements relative to different points of their bounding boxes.
    """

    CENTRE = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5


def anchor_rect(rect: pg.rect, pos: Vector2, anchor: Anchor) -> None:
    """
    Position a rectangle relative to a given anchor point.

    Args:
        rect: The pygame Rect to position.
        pos: The target position (x, y).
        anchor: The Anchor enum value specifying which point of the rect to position.
    """

    match anchor:
        case Anchor.CENTRE:
            rect.center = pos
        case Anchor.TOP_LEFT:
            rect.topleft = pos
        case Anchor.TOP_RIGHT:
            rect.topright = pos
        case Anchor.BOTTOM_LEFT:
            rect.bottomleft = pos
        case Anchor.BOTTOM_RIGHT:
            rect.bottomright = pos


def rect_anchor_pos(rect: pg.rect, anchor: Anchor) -> Vector2:
    """
    Get the position of a specific anchor point on a rectangle.

    Args:
        rect: The pygame Rect to examine.
        anchor: The Anchor enum value specifying which point to get.

    Returns:
        Vector2: The (x, y) coordinates of the requested anchor point.
    """

    match anchor:
        case Anchor.CENTRE:
            return rect.center
        case Anchor.TOP_LEFT:
            return rect.topleft
        case Anchor.TOP_RIGHT:
            return rect.topright
        case Anchor.BOTTOM_LEFT:
            return rect.bottomleft
        case Anchor.BOTTOM_RIGHT:
            return rect.bottomright


class Text():
    """
    A class for creating and rendering text surfaces.

    Attributes:
        game (Game): Reference to the main Game instance.
        rect (pygame.Rect): The bounding rectangle of the text surface.
        pos (Point): Current position of the text.
        anchor (Anchor): Current anchor point for positioning.
        text (str): Current text string being displayed.
        font_size (int): Current font size.
        font_name (str): Current font name.
        color (pygame.Color): Current text color.
        font (pygame.font.Font): The pygame Font object.
        text_surface (pygame.Surface): The rendered text surface.
    """

    def __init__(
            self,
            game:       Game,
            pos:        Point,
            anchor:     Anchor,
            text:       str,
            font_size:  int,
            font_name:  str = DEFAULT_FONT,
            color:      pg.color = (0, 0, 0)):
        """Initialize a Text object.

        Args:
            game: Reference to the Game instance.
            pos: Position to place the text.
            anchor: Anchor point for positioning.
            text: The text string to display.
            font_size: Size of the font.
            font_name: Name of the font to use.
            color: Color of the text (RGB tuple).
        """

        self.game = game
        self.rect = None
        self.update(pos, anchor, text, font_size, font_name, color)

    def update(
            self,
            pos:        Point = None,
            anchor:     Anchor = None,
            text:       str = None,
            font_size:  int = None,
            font_name:  str = None,
            color:      pg.color = None) -> None:
        """Update the text properties.

        Any argument not provided will keep its current value.
        Automatically handles re-rendering the text surface when needed.

        Args:
            pos: New position.
            anchor: New anchor point.
            text: New text string.
            font_size: New font size.
            font_name: New font name.
            color: New text color.
        """

        update = font_size or font_name
        if update:
            if font_size:
                self.font_size = font_size
            if font_name:
                self.font_name = font_name
            self.font = pg.font.Font(font_name, font_size)

        update = update or text or color
        if update:
            if text:
                self.text = text
            if color:
                self.color = color
            self.text_surface = self.font.render(text, True, color)

        update = update or pos or anchor
        if update:
            if pos:
                self.pos = pos
            if anchor:
                self.anchor = anchor
            self.rect = self.text_surface.get_rect()
            anchor_rect(self.rect, self. pos, self.anchor)

    def draw(self):
        """Draw the text surface to the game's canvas."""
        self.game.canvas.blit(self.text_surface, self.rect)


class Button(abc.ABC):
    """Abstract base class for button UI elements.

    Attributes:
        game (Game): Reference to the main Game instance.
        size (Vector2): Size of the button (width, height).
        pos (Point): Position of the button.
        anchor (Anchor): Anchor point for positioning.
        image_path (str): Path to button image (optional).
        text (Text): Text object for the button (optional).
        text_anchor (Anchor): Anchor point for the button text.
        mouseover (bool): Whether the mouse is over the button.
        clicked (bool): Whether the button was clicked.
    """

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE,
            image_paths=None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize a Button instance.

        Args:
            game: Reference to the Game instance.
            size: Size of the button (width, height).
            pos: Position of the button.
            anchor: Anchor point for positioning.
            image_paths: Paths to button images (optional).
            text: Text object for the button (optional).
            text_anchor: Anchor point for the button text.
        """

        self.game = game
        self.size = size
        self.pos = pos
        self.anchor = anchor
        self.text = text
        self.text_anchor = text_anchor

        if image_paths:
            self.has_image = True

            image_idle = pg.image.load(image_paths[0])
            self.image_idle = pg.transform.scale(image_idle, self.size)

            image_hover = pg.image.load(image_paths[1])
            self.image_hover = pg.transform.scale(image_hover, self.size)

            image_clicked = pg.image.load(image_paths[2])
            self.image_clicked = pg.transform.scale(image_clicked, self.size)

            self.image = image_idle
        else:
            self.has_image = False

            self.color_idle = (170, 170, 170)
            self.color_hover = (120, 120, 120)
            self.color_clicked = (70, 70, 70)

            self.color = self.color_idle

        self.rect = pg.Rect(0, 0, size[0], size[1])
        anchor_rect(self.rect, pos, anchor)

        if self.text:
            self.text.update(pos=rect_anchor_pos(self.rect, text_anchor))

        self.mouseover = False
        self.mousedown = False
        self.mousehold = False
        self.mouseup = False

    def draw(self):
        """Draw the button to the game's canvas."""

        if self.has_image:
            if self.mousehold:
                self.image = self.image_clicked
            elif self.mouseover:
                self.image = self.image_hover
            else:
                self.image = self.image_idle

            self.game.canvas.blit(self.image, self.rect)
        else:
            if self.mousehold:
                self.color = self.color_clicked
            elif self.mouseover:
                self.color = self.color_hover
            else:
                self.color = self.color_idle

            pg.draw.rect(self.game.canvas, self.color, self.rect)

        if self.text:
            self.text.draw()

    def check_event(self):
        """Check for mouse events related to the button (hover, click)."""

        self.mousedown = False
        self.mouseup = False
        if pg.MOUSEMOTION in self.game.events.keys():
            self.mouseover = self.rect.collidepoint(self.game.events[pg.MOUSEMOTION][-1].pos)
            # if self.mouseover:
            #     self.color = (120, 120, 120)
            # else:
            #     self.color = (170, 170, 170)

        if self.mouseover and pg.MOUSEBUTTONDOWN in self.game.events.keys():
            for event in self.game.events[pg.MOUSEBUTTONDOWN]:
                if event.button == 1:
                    self.mousedown = True
                    self.mousehold = True
                    break

        if self.mousedown and pg.MOUSEBUTTONUP in self.game.events.keys():
            for event in self.game.events[pg.MOUSEBUTTONDOWN]:
                if event.button == 1:
                    self.mouseup = True
                    self.hold = False
                    break

    @abc.abstractmethod
    def update(self):
        """Abstract method to be implemented by subclasses for button behavior."""

        pass


class SceneSwitchButton(Button):
    """A Button implementation that switches scenes when clicked."""

    def __init__(
            self,
            game: Game,
            scene_class,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE,
            image_paths=None,
            text: Text = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize a SceneSwitchButton.

        Args:
            game: Reference to the Game instance.
            scene_class: The scene class to switch to when clicked.
            size: Size of the button (width, height).
            pos: Position of the button.
            anchor: Anchor point for positioning.
            image_paths: Paths to button images (optional).
            text: Text object for the button (optional).
            text_anchor: Anchor point for the button text.
        """

        Button.__init__(self, game, size, pos, anchor, image_paths, text, text_anchor)
        self.scene_class = scene_class

    def update(self):
        """Switch scene if clicked."""
        if self.mousedown:
            self.game.current_scene = self.scene_class(self.game)


class BackButton(SceneSwitchButton):
    """A Button implementation that brings user back when clicked."""

    def __init__(
            self,
            game: Game,
            scene_class,
            size: Vector2 = (120, 120),
            pos: Point = (0, 0),
            anchor: Anchor = Anchor.TOP_LEFT,
            image_paths: Optional[List[str]] = None):
        """Initialize a BackButton.

        Args:
            game (Game): Reference to the Game instance.
            scene_class (Scene): The scene class to switch to when clicked.
            size (Vector2, optional): Size of the button (width, height). Defaults to (120, 120).
            pos (Point, optional): Position of the button. Defaults to (0, 0).
            anchor (Anchor, optional): Anchor point for positioning. Defaults to Anchor.TOP_LEFT.
            image_paths (Optional[List[str]], optional): Paths to button images (optional). Defaults to None.
        """

        super().__init__(game, scene_class, size, pos, anchor, image_paths)
        self.arrow_color = "black"
        self.arrow_polygon = ((100, 55), (100, 65), (40, 65), (40, 75), (15, 60), (40, 45), (40, 55))

    def draw(self):
        """Draw the button to the game's canvas."""
        super().draw()
        pg.draw.polygon(self.game.canvas, self.arrow_color, self.arrow_polygon)


class ChooseLanguageButton(Button):
    """A Button implementation for the language selection drop-down menu."""

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE):
        """Initialize a ChooseLanguageButton.

        Args:
            game (Game): Reference to the Game instance.
            size (Vector2): Size of the button (width, height).
            pos (Point): Position of the button.
            anchor (Anchor, optional): Anchor point for positioning.. Defaults to Anchor.CENTRE.
        """

        super().__init__(game=game,
                         size=size,
                         pos=pos,
                         anchor=anchor)

        self.pos = pos
        self.show_options = False
        self.options = [(("en_US", "UTF-8"), "English"),
                        (("ru_RU", "UTF-8"), "Русский")]

        cur_locale = locale.getlocale()
        self.cur_option = 0
        while self.options[self.cur_option][0] != cur_locale:
            self.cur_option += 1
        self.text = Text(
            game,
            pos,
            Anchor.CENTRE,
            self.options[self.cur_option][1],
            80)

    def update(self):
        """Switch locale if clicked."""
        if self.mousedown:
            self.cur_option = (self.cur_option + 1) % len(self.options)
            locale.setlocale(locale.LC_ALL, self.options[self.cur_option][0])
            self.text = Text(
                self.game,
                self.pos,
                Anchor.CENTRE,
                self.options[self.cur_option][1],
                80)
            self.mousedown = False
            self.mousehold = False


class ExitButton(Button):
    """A Button implementation that exits the game when clicked."""

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE,
            image_paths: Optional[List[str]] = None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """
        Initialize a ExitButton.

        Args:
            game: Reference to the Game instance.
            size: Size of the button (width, height).
            pos: Position of the button.
            anchor: Anchor point for positioning.
            image_paths: Paths to button images (optional).
            text: Text object for the button (optional).
            text_anchor: Anchor point for the button text.
        """

        Button.__init__(self, game, size, pos, anchor, image_paths, text, text_anchor)

    def update(self):
        """Exit game if clicked."""
        if self.mousedown:
            self.game.running = False


class TextField:
    """TextField class to accept user input."""

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor,
            font_size: int = 40,
            font_color: ColorLike = (0, 0, 0),
            bg_color: ColorLike = (255, 255, 255),
            border_color: ColorLike = (200, 200, 200),
            border_width: int = 2,
            max_length: int = 32,
            placeholder: str = ""):
        """Initialize TextField class.

        Args:
            game (Game): Reference to the Game instance.
            size (Vector2): Size of the field (width, height).
            pos (Point): Position of the field.
            anchor (Anchor): Anchor point for positioning.
            font_size (int, optional): Font size. Defaults to 40.
            font_color (ColorLike, optional): Font color. Defaults to (0, 0, 0).
            bg_color (ColorLike, optional): Background color. Defaults to (255, 255, 255).
            border_color (ColorLike, optional): Border color. Defaults to (200, 200, 200).
            border_width (int, optional): Border width. Defaults to 2.
            max_length (int, optional): Maximum number of accepted characters. Defaults to 32.
            placeholder (str, optional): Placeholder value to show in background, while the field is inactive.
            Defaults to "".
        """
        self.game = game
        self.size = size
        self.pos = pos
        self.anchor = anchor
        self.font_size = font_size
        self.font_color = font_color
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.max_length = max_length
        self.placeholder = placeholder

        self.font = pg.font.Font(None, font_size)
        self.value = ""
        self.active = False
        if len(placeholder) > max_length:
            print(_("Warning! Placeholder length is larger then max_length of the field!"))

        self.rect = pg.Rect(0, 0, *size)
        anchor_rect(self.rect, pos, anchor)

        self.cursor_visible = True
        self.cursor_counter = 0
        self.cursor_switch_frames = 30

    def check_event(self):
        self.mousedown = False
        self.mouseover = self.rect.collidepoint(pg.mouse.get_pos())

        for event in self.game.events.get(pg.MOUSEBUTTONDOWN, []):
            if event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.active = True
                    self.mousedown = True
                else:
                    self.active = False

        # If the field is active, allow player to enter text
        if self.active:
            for event in self.game.events.get(pg.KEYDOWN, []):
                if event.key == pg.K_BACKSPACE:
                    self.value = self.value[:-1]
                elif event.key == pg.K_RETURN:
                    self.active = False
                elif event.unicode and len(self.value) < self.max_length and event.key != pg.K_TAB:
                    self.value += event.unicode

    def update(self):
        if self.active:
            self.cursor_counter += 1
            if self.cursor_counter >= self.cursor_switch_frames:
                self.cursor_counter = 0
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False

    def draw(self):
        # Field and border
        pg.draw.rect(self.game.canvas, self.bg_color, self.rect)
        pg.draw.rect(self.game.canvas, self.border_color, self.rect, self.border_width)

        # Text inside
        text = self.value if self.value else self.placeholder
        color = self.font_color if self.value else (180, 180, 180)
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.x + 8  # postition text inside rect

        # Position cursor
        cursor_x = text_rect.right + 2
        cursor_y1 = text_rect.top + 3
        cursor_y2 = text_rect.bottom - 3

        self.game.canvas.blit(text_surface, text_rect)

        if self.active and self.cursor_visible:
            pg.draw.line(self.game.canvas, self.font_color, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)

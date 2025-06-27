import enum
import abc
import locale
from typing import Dict, List, Optional
import pygame as pg
import pygame.typing as pgt

from Deadline.network import Network
from Deadline.localization import _
import Deadline.game_logic as gl

# Typing
Vector2 = tuple[int, int]
Point = Vector2

WINDOW_SIZE = (1920, 1080)
DEFAULT_FONT = pg.font.get_default_font()


def get_events_dict() -> Dict[int, List[pg.Event]]:
    """Get all Pygame events and organize them in a dictionary by event type."""
    events = pg.event.get()
    events_dict: Dict[int, List[pg.Event]] = {}

    for event in events:
        events_dict[event.type] = events_dict.get(event.type, []) + [event]
    return events_dict


class Game():
    """
    Main game class that manages the game loop.

    Attributes
        window_size (tuple): The size of the game window (width, height).
        canvas (pygame.Surface): The main drawing surface.
        display (pygame.Surface): The display surface.
        default_font (str): The default font name.
        current_scene (Scene): The currently active scene.
        running (bool): Flag indicating if the game is running.
        network (Network): class for network communication.

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
        self.network = Network()
        self.err = False
        self.err_popup = None

    def run(self) -> None:
        """Run the main game loop until self.running becomes False."""
        while self.running:
            self.events = get_events_dict()
            if pg.QUIT in self.events.keys():
                self.running = False
            try:
                if not self.err:
                    self.current_scene.run()
                else:
                    self.err_popup.run()
                    if self.err_popup.mousedown:
                        self.err = False
                        self.err_popup = None
            except Exception as e:
                err_text = Text(
                    self,
                    (0, 0),
                    Anchor.CENTRE,
                    str(e),
                    30)
                self.err_popup = ErrorPopUp(self,
                                            (1000, 600),
                                            (self.window_size[0] // 2, self.window_size[1] // 2),
                                            Anchor.CENTRE,
                                            None,
                                            err_text)
                self.err = True

        pg.quit()

    def blit_screen(self) -> None:
        """Update the display by blitting the canvas to the display surface."""
        self.display.blit(self.canvas, (0, 0))
        pg.display.update()


class Anchor(enum.Enum):
    """Enumeration for different anchor points of UI elements."""

    CENTRE = 1
    TOP_LEFT = 2
    TOP_RIGHT = 3
    BOTTOM_LEFT = 4
    BOTTOM_RIGHT = 5


def anchor_rect(rect: pg.Rect, pos: Vector2, anchor: Anchor) -> None:
    """Position a rectangle relative to a given anchor point."""
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


def rect_anchor_pos(rect: pg.Rect, anchor: Anchor) -> Vector2:
    """Get the position of a specific anchor point on a rectangle."""
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

    Attributes
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
            game: Game,
            pos: Point,
            anchor: Anchor,
            text: str,
            font_size: int,
            font_name: str = DEFAULT_FONT,
            color: pgt.ColorLike = pg.Color(0, 0, 0)):
        """Initialize a Text object."""
        self.game = game
        self.change(pos, anchor, text, font_size, font_name, color)

    def change(
            self,
            pos: Optional[Point] = None,
            anchor: Optional[Anchor] = None,
            text: Optional[str] = None,
            font_size: Optional[int] = None,
            font_name: Optional[str] = None,
            color: Optional[pgt.ColorLike] = None) -> None:
        """Update the text properties."""
        change = bool(font_size) or bool(font_name)
        if change:
            if font_size:
                self.font_size = font_size
            if font_name:
                self.font_name = font_name
            self.font = pg.font.Font(self.font_name, self.font_size)

        change = change or bool(text) or bool(color)
        if change:
            if text:
                self.text = text
            if color:
                self.color = color
            self.text_surface = self.font.render(self.text, True, self.color)

        change = change or bool(pos) or bool(anchor)
        if change:
            if pos:
                self.pos = pos
            if anchor:
                self.anchor = anchor
            self.rect = self.text_surface.get_rect()
            anchor_rect(self.rect, self.pos, self.anchor)

    def update(self):
        """Do nothing.Dummy."""
        pass

    def draw(self):
        """Draw the text surface to the game's canvas."""
        self.game.canvas.blit(self.text_surface, self.rect)


class Button(abc.ABC):
    """Abstract base class for button UI elements."""

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE,
            images: Optional[List[pg.Surface]] = None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize a Button instance."""
        self.game = game

        self.mouseover = False
        self.mousedown = False
        self.mousehold = False
        self.mouseup = False

        if not images:
            self.images = None
            self.color_idle = (170, 170, 170)
            self.color_hover = (120, 120, 120)
            self.color_clicked = (70, 70, 70)

            self.color = self.color_idle

        if not text:
            self.text = None

        self.change(size, pos, anchor, images, text, text_anchor)

    def change(
            self,
            size: Optional[Vector2] = None,
            pos: Optional[Point] = None,
            anchor: Optional[Anchor] = None,
            images: Optional[List[pg.Surface]] = None,
            text: Optional[Text] = None,
            text_anchor: Optional[Anchor] = None):
        """Change the button's properties."""
        change = bool(size)
        if change:
            self.size = size
            self.rect = pg.Rect(0, 0, self.size[0], self.size[1])

        if images:
            self.images = images
            change = True

        if change and self.images:
            self.image_idle = pg.transform.scale(images[0], self.size)
            self.image_hover = pg.transform.scale(images[1], self.size)
            self.image_clicked = pg.transform.scale(images[2], self.size)
            self.image = self.image_idle

        change = bool(pos) or bool(anchor)
        if change:
            if pos:
                self.pos = pos
            if anchor:
                self.anchor = anchor
            anchor_rect(self.rect, self.pos, self.anchor)

        change = bool(text) or bool(text_anchor)
        if change:
            if text:
                self.text = text
            if text_anchor:
                self.text_anchor = text_anchor

        if change and self.text:
            self.text.change(pos=rect_anchor_pos(self.rect, self.text_anchor))

    def draw(self):
        """Draw the button to the game's canvas."""
        if self.images:
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
            images: Optional[List[pg.Surface]] = None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize a SceneSwitchButton."""
        Button.__init__(self, game, size, pos, anchor, images, text, text_anchor)
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
            images: Optional[List[pg.Surface]] = None):
        """Initialize a BackButton."""
        super().__init__(game, scene_class, size, pos, anchor, images)
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
        """Initialize a ChooseLanguageButton."""
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
            images: Optional[List[pg.Surface]] = None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize an ExitButton."""
        Button.__init__(self, game, size, pos, anchor, images, text, text_anchor)

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
            font_color: pgt.ColorLike = (0, 0, 0),
            bg_color: pgt.ColorLike = (255, 255, 255),
            border_color: pgt.ColorLike = (200, 200, 200),
            border_width: int = 2,
            max_length: int = 32,
            placeholder: str = ""):
        """Initialize TextField class."""
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
        """Check for mouse events related to the button (hover, click)."""
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
        """Update the cursor for the text field."""
        if self.active:
            self.cursor_counter += 1
            if self.cursor_counter >= self.cursor_switch_frames:
                self.cursor_counter = 0
                self.cursor_visible = not self.cursor_visible
        else:
            self.cursor_visible = False

    def draw(self):
        """Draw the text field with current value and cursor."""
        # Field and border
        pg.draw.rect(self.game.canvas, self.bg_color, self.rect)
        pg.draw.rect(self.game.canvas, self.border_color, self.rect, self.border_width)

        # Text inside
        text = self.value if self.value else self.placeholder
        color = self.font_color if self.value else (180, 180, 180)
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.x + 8  # Position text inside rect

        # Position cursor
        cursor_x = text_rect.right + 2
        cursor_y1 = text_rect.top + 3
        cursor_y2 = text_rect.bottom - 3

        self.game.canvas.blit(text_surface, text_rect)

        if self.active and self.cursor_visible:
            pg.draw.line(self.game.canvas, self.font_color, (cursor_x, cursor_y1), (cursor_x, cursor_y2), 2)


class ConnectButton(Button):
    """A Button that connects to network (stub for extension)."""

    def update(self):
        """Update button."""
        return super().update()


class CheckBoxButton(Button):
    """Checkbox button."""

    def __init__(
            self,
            game: Game,
            size: Vector2,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE,
            images: Optional[List[pg.Surface]] = None,
            text: Optional[Text] = None,
            text_anchor: Anchor = Anchor.CENTRE):
        """Initialize CheckBoxButton."""
        super().__init__(game,
                         size,
                         pos,
                         anchor,
                         images,
                         text,
                         text_anchor)
        self.clicked = False
        self.tick_color = "black"
        match anchor:
            case Anchor.TOP_LEFT:
                pos_top_left = pos
            case  Anchor.TOP_RIGHT:
                pos_top_left = (pos[0] - size[0], pos[1])
            case Anchor.BOTTOM_LEFT:
                pos_top_left = (pos[0], pos[1] - size[1])
            case Anchor.BOTTOM_RIGHT:
                pos_top_left = (pos[0] - size[0], pos[1] - size[1])
            case Anchor.CENTRE:
                pos_top_left = (pos[0] - size[0] // 2, pos[1] - size[1] // 2)

        self.tick_polygon = (
                            (pos_top_left[0] + size[0] // 10, pos_top_left[1] + size[1] // 10),
                            (pos_top_left[0] + size[0] // 10 * 9, pos_top_left[1] + size[1] // 10),
                            (pos_top_left[0] + size[0] // 10 * 9, pos_top_left[1] + size[1] // 10 * 9),
                            (pos_top_left[0] + size[0] // 10, pos_top_left[1] + size[1] // 10 * 9),

        )

    def draw(self):
        """Draw the checkbox button (with tick if clicked)."""
        super().draw()
        if self.clicked:
            pg.draw.polygon(self.game.canvas, self.tick_color, self.tick_polygon)

    def update(self):
        """Toggle checkbox state if clicked."""
        if self.mousedown:
            self.clicked = not self.clicked
            self.mousedown = False
            self.mousehold = False


class ErrorPopUp(Button):
    """Class representing error popup message."""

    def run(self):
        """Display the error popup and handle events."""
        self.check_event()
        self.draw()
        self.game.blit_screen()

    def update(self):
        """Do nothing. Dummy."""
        pass


CARD_TEXTURE_SIZE = (700, 1000)
CARD_IMAGE_SIZE = (474, 360)
CARD_IMAGE_OFFSET = (101, 154)
CARD_NAME_CENTRE_OFFSET = (340, 560)
CARD_DESCRIPTION_CENTRE_OFFSET = (340, 685)
CARD_CLOCK_CENTRE_OFFSET = (590, 140)
CARD_AWARD_CENTRE_OFFSET = (90, 910)
CARD_PENALTY_CENTRE_OFFSET = (215, 910)
CARD_PROGGRESS_CENTRE_OFFSET = (510, 910)


def get_size_ratio(x: Vector2, y: Vector2):
    """Return the width and height ratios between two vectors."""
    return (x[0] / y[0], x[1] / y[1])


CARD_WIDTH_TO_HEIGHT_RATIO = CARD_TEXTURE_SIZE[0] / CARD_TEXTURE_SIZE[1]
CARD_IMAGE_RATIO = get_size_ratio(CARD_IMAGE_SIZE, CARD_TEXTURE_SIZE)
CARD_IMAGE_OFFSET_RATIO = get_size_ratio(CARD_IMAGE_OFFSET, CARD_TEXTURE_SIZE)
CARD_NAME_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_NAME_CENTRE_OFFSET, CARD_TEXTURE_SIZE)
CARD_DESCRIPTION_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_DESCRIPTION_CENTRE_OFFSET, CARD_TEXTURE_SIZE)
CARD_CLOCK_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_CLOCK_CENTRE_OFFSET, CARD_TEXTURE_SIZE)
CARD_AWARD_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_AWARD_CENTRE_OFFSET, CARD_TEXTURE_SIZE)
CARD_PENALTY_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_PENALTY_CENTRE_OFFSET, CARD_TEXTURE_SIZE)
CARD_PROGGRESS_CENTRE_OFFSET_RATIO = get_size_ratio(CARD_PROGGRESS_CENTRE_OFFSET, CARD_TEXTURE_SIZE)


class Card():
    """Class representing a card UI element."""

    def __init__(
            self,
            game: Game,
            game_obj: gl.Game,
            card_info: gl.Card,
            card_type_images: Dict[str, pg.Surface],
            height: int,
            pos: Point,
            anchor: Anchor = Anchor.CENTRE):
        """Initialize a Card UI element."""
        self.game = game
        self.game_obj = game_obj
        self.card_info = card_info
        self.card_type_images = card_type_images
        self.card_image = pg.image.load(card_info.image)
        self.size = (round(height * CARD_WIDTH_TO_HEIGHT_RATIO), height)
        self.pos = pos
        self.anchor = anchor

        match self.game_obj.get_card_type(self.card_info.cid):
            case "TaskCard":
                self.card_type = "TaskCard"
            case "ActionCard":
                self.card_type = "ActionCard"

        self.card_type_image = self.card_type_images[self.card_type]

        self.rect = pg.Rect(0, 0, self.size[0], self.size[1])
        self.rect_image = pg.Rect(0, 0, round(self.size[0] * CARD_IMAGE_RATIO[0]),
                                  round(self.size[1] * CARD_IMAGE_RATIO[1]))
        anchor_rect(self.rect, self.pos, self.anchor)
        image_pos = rect_anchor_pos(self.rect, Anchor.TOP_LEFT)
        image_pos = (image_pos[0] + round(self.size[0] * CARD_IMAGE_OFFSET_RATIO[0]),
                     image_pos[1] + round(self.size[1] * CARD_IMAGE_OFFSET_RATIO[1]))
        anchor_rect(self.rect_image, image_pos, Anchor.TOP_LEFT)

        self.surface_card_type_image = pg.transform.scale(self.card_type_image, self.size)
        self.surface_card_image = pg.transform.scale(self.card_image, self.rect_image.size)

        self.name_text = Text(
            game,
            (self.rect.topleft[0] + round(CARD_NAME_CENTRE_OFFSET_RATIO[0] * self.size[0]),
             self.rect.topleft[1] + round(CARD_NAME_CENTRE_OFFSET_RATIO[1] * self.size[1])),
            Anchor.CENTRE,
            _(card_info.name),
            self.size[0] // 10)

        self.description_text = Text(
            game,
            (self.rect.topleft[0] + round(CARD_DESCRIPTION_CENTRE_OFFSET_RATIO[0] * self.size[0]),
             self.rect.topleft[1] + round(CARD_DESCRIPTION_CENTRE_OFFSET_RATIO[1] * self.size[1])),
            Anchor.CENTRE,
            _(self.card_info.description),
            self.size[0] // 15)

        if self.card_type == "TaskCard":
            self.clock_text = Text(
                self.game,
                (self.rect.topleft[0] + round(CARD_CLOCK_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_CLOCK_CENTRE_OFFSET_RATIO[1] * self.size[1])),
                Anchor.CENTRE,
                _(str(self.game_obj.get_task_info(self.card_info.task).deadline)),
                self.size[0] // 8)

            self.award_text = Text(
                self.game,
                (self.rect.topleft[0] + round(CARD_AWARD_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_AWARD_CENTRE_OFFSET_RATIO[1] * self.size[1])),
                Anchor.CENTRE,
                _(str(self.game_obj.get_task_info(self.card_info.task).award)),
                self.size[0] // 8)

            self.penalty_text = Text(
                self.game,
                (self.rect.topleft[0] + round(CARD_PENALTY_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_PENALTY_CENTRE_OFFSET_RATIO[1] * self.size[1])),
                Anchor.CENTRE,
                _(str(self.game_obj.get_task_info(self.card_info.task).penalty)),
                self.size[0] // 8)

            self.progress_text = Text(
                self.game,
                (self.rect.topleft[0] + round(CARD_PROGGRESS_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_PROGGRESS_CENTRE_OFFSET_RATIO[1] * self.size[1])),
                Anchor.CENTRE,
                _("0 / " + str(self.game_obj.get_task_info(self.card_info.task).difficulty)),
                self.size[0] // 8)

    def update(self):
        """Do nothing. Dummy."""
        pass

    def draw(self):
        """Draw the card and its elements."""
        self.game.canvas.blit(self.surface_card_image, self.rect_image)
        self.game.canvas.blit(self.surface_card_type_image, self.rect)
        self.name_text.draw()
        if self.card_type == "TaskCard":
            self.clock_text.draw()
            self.award_text.draw()
            self.penalty_text.draw()
            self.progress_text.draw()
        self.description_text.draw()

    def move_to(self, pos: Point):
        """Move card to new position."""
        self.pos = pos
        anchor_rect(self.rect, self.pos, self.anchor)
        image_pos = rect_anchor_pos(self.rect, Anchor.TOP_LEFT)
        image_pos = (image_pos[0] + round(self.size[0] * CARD_IMAGE_OFFSET_RATIO[0]),
                     image_pos[1] + round(self.size[1] * CARD_IMAGE_OFFSET_RATIO[1]))
        anchor_rect(self.rect_image, image_pos, Anchor.TOP_LEFT)

        self.name_text.change(
            pos=(self.rect.topleft[0] + round(CARD_NAME_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_NAME_CENTRE_OFFSET_RATIO[1] * self.size[1])))
        self.description_text.change(
            pos=(self.rect.topleft[0] + round(CARD_DESCRIPTION_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                 self.rect.topleft[1] + round(CARD_DESCRIPTION_CENTRE_OFFSET_RATIO[1] * self.size[1])))
        if self.card_type == "TaskCard":
            self.clock_text.change(
                pos=(self.rect.topleft[0] + round(CARD_CLOCK_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                     self.rect.topleft[1] + round(CARD_CLOCK_CENTRE_OFFSET_RATIO[1] * self.size[1])))
            self.award_text.change(
                pos=(self.rect.topleft[0] + round(CARD_AWARD_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                     self.rect.topleft[1] + round(CARD_AWARD_CENTRE_OFFSET_RATIO[1] * self.size[1])))
            self.penalty_text.change(
                pos=(self.rect.topleft[0] + round(CARD_PENALTY_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                     self.rect.topleft[1] + round(CARD_PENALTY_CENTRE_OFFSET_RATIO[1] * self.size[1])))
            self.progress_text.change(
                pos=(self.rect.topleft[0] + round(CARD_PROGGRESS_CENTRE_OFFSET_RATIO[0] * self.size[0]),
                     self.rect.topleft[1] + round(CARD_PROGGRESS_CENTRE_OFFSET_RATIO[1] * self.size[1])))

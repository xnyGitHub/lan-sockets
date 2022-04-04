"""View class for MVC"""  # pylint: disable=redefined-builtin,no-member,no-self-use
import os
import pygame
from src.chess.engine.event import EventManager, Event, QuitEvent, TickEvent, Highlight, ThreadQuitEvent, ViewUpdate
from src.chess.engine.game import GameEngine
from src.utils import flush_print_default, invert_move
import math


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

print = flush_print_default(print)


class View:
    """Pygame View class"""

    WIDTH = HEIGHT = 512  # Heigh and width of the board
    RIGHT_PANEL = 256
    DIMENSION = 8  # This will cause 8 squares to be print on the board
    SIZE = HEIGHT / DIMENSION  # Dimensions of the square

    GREEN: tuple = (119, 149, 86)  # Off Green colour
    WHITE: tuple = (235, 235, 208)  # Off White Color

    def __init__(self, event_manager: EventManager, gamemodel: GameEngine) -> None:
        self.event_manager = event_manager
        self.gamemodel: GameEngine = gamemodel
        self.event_manager.register_listener(self)
        self.screen: pygame.surface.Surface
        self.images: dict = {}
        self.initialised: bool = self.initialise()
        self.current_click: tuple = (None, None)
        self.check_status: dict = {}

    def notify(self, event: Event) -> None:
        """Notify"""
        if isinstance(event, Highlight):
            self.current_click = event.square

        if isinstance(event, TickEvent):
            self.render()

        if isinstance(event, QuitEvent):
            self.initialised = False
            pygame.quit()

        if isinstance(event, ViewUpdate):
            check_status = event.check_update

            if check_status:
                self.check_status = check_status
            else:
                self.check_status = {}

        if isinstance(event, ThreadQuitEvent):
            game_over = pygame.event.Event(pygame.USEREVENT + 1)
            pygame.event.post(game_over)

    def render(self) -> None:
        """Render"""

        if not self.initialised:
            return
        self.draw_board()
        self.draw_move_log()

        if self.check_status:
            self.highlight_check()

        if self.current_click[0] is not None:  # Check if the user has selected a square
            self.highlight_square()  # Draw highlighed square

        pygame.display.flip()

    def draw_board(self) -> None:
        """Render the board"""
        board: list = self.gamemodel.board
        colors: list = [View.WHITE, View.GREEN]

        for row in range(View.DIMENSION):
            for col in range(View.DIMENSION):
                color = colors[((row + col) % 2)]

                pygame.draw.rect(
                    self.screen, color, pygame.Rect(col * View.SIZE, row * View.SIZE, View.SIZE, View.SIZE)
                )
                # fmt: off
                piece = board[row][col]
                if piece != "--":
                    image = self.images[piece]
                    self.screen.blit(image,pygame.Rect(col * View.SIZE,row * View.SIZE,View.SIZE,View.SIZE,))
                # fmt: on

    def draw_move_log(self) -> None:
        font = pygame.font.Font("freesansbold.ttf", 14)
        position = [544, 672]
        height = font.get_height()

        txt_surface = font.render("White", True, View.WHITE, pygame.SRCALPHA)
        self.screen.blit(txt_surface, (544, 5))

        txt_surface = font.render("Black", True, View.WHITE, pygame.SRCALPHA)
        self.screen.blit(txt_surface, (672, 5))

        seperator = font.render("|", True, View.WHITE, pygame.SRCALPHA)
        for count, text in enumerate(self.gamemodel.move_log):
            txt_surface = font.render(text, True, View.WHITE, pygame.SRCALPHA)
            self.screen.blit(txt_surface, (position[count % 2], 20 + (height * (math.floor(count / 2)))))
            self.screen.blit(seperator, (630, 20 + (height * (math.floor(count / 2)))))

    def highlight_square(self) -> None:
        """Highlight the square that a user clicks on, also show possible moves if its their piece"""
        highlight: pygame.Surface = self.create_highlight("blue")
        cords: str = "".join(str(point) for point in self.current_click)

        self.screen.blit(highlight, (self.current_click[0] * View.SIZE, self.current_click[1] * View.SIZE))
        for move in self.gamemodel.moves:
            if cords == move.split(":")[0]:
                self.screen.blit(
                    highlight, (int(move.split(":")[1][0]) * View.SIZE, int(move.split(":")[1][1]) * View.SIZE)
                )

    def highlight_check(self) -> None:
        """Highlight the pieces if a king is in check"""

        red_highlight: pygame.Surface = self.create_highlight("red")
        green_highlight: pygame.Surface = self.create_highlight("green")

        king_loc = self.check_status["king_location"]
        attacking_pieces = self.check_status["attacking_pieces"]

        if self.gamemodel.color == "black":
            king_loc = invert_move(king_loc)
            attacking_pieces = list(map(invert_move, attacking_pieces))

        self.screen.blit(green_highlight, (int(king_loc[0]) * View.SIZE, int(king_loc[1]) * View.SIZE))
        for pieces in attacking_pieces:
            self.screen.blit(red_highlight, (int(pieces[0]) * View.SIZE, int(pieces[1]) * View.SIZE))

    def load_images(self) -> None:
        """Load the images into a dictionary"""
        # fmt: off
        pieces = ["wP","wR","wN","wB","wQ","wK","bP","bN","bQ","bR","bB","bK",]
        # fmt: on
        for piece in pieces:
            self.images[piece] = pygame.image.load("src/chess/assets/images/" + piece + ".png")

    def create_highlight(self, color: str) -> pygame.Surface:
        """Create a highlight pygame object"""
        highlight = pygame.Surface((View.SIZE, View.SIZE))
        highlight.set_alpha(75)
        highlight.fill(pygame.Color(color))

        return highlight

    def initialise(self) -> bool:
        """Create and initialise a pygame instance"""
        pygame.init()
        pygame.display.set_caption("Chess Engine")
        self.screen = pygame.display.set_mode((512 + View.RIGHT_PANEL, 512))
        self.load_images()
        return True

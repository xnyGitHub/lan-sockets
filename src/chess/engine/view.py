"""View class for MVC"""  # pylint: disable=redefined-builtin,no-member,no-self-use
import os
import math
import pygame
from src.chess.engine.event import (
    EventManager,
    Event,
    QuitEvent,
    TickEvent,
    Highlight,
    ThreadQuitEvent,
    ViewUpdate,
    UpdateEvent,
)
from src.chess.engine.game import GameEngine
from src.utils import flush_print_default, invert_move


os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

print = flush_print_default(print)


class View:
    """Pygame View class"""

    WIDTH = HEIGHT = 512  # Heigh and width of the board
    RIGHT_PANEL = 256
    TOP_PANEL = BOT_PANEL = 50
    DIMENSION = 8  # This will cause 8 squares to be print on the board
    SIZE = HEIGHT / DIMENSION  # Dimensions of the square

    GREEN: tuple = (119, 149, 86)  # Off Green colour
    WHITE: tuple = (235, 235, 208)  # Off White Color

    IMAGE_LOCATION = (10,10)

    TOP_USERNAME_LOCATION = (50,5)
    BOT_USERNAME_LOCATION = (50,567)

    TOP_IMAGE_LOCATION = (5,5)
    BOT_IMAGE_LOCATION = (5,567)

    SOUNDS: dict = {}
    IMAGES: dict = {}
    OUTLINED_IMAGES: dict = {}

    def __init__(self, event_manager: EventManager, gamemodel: GameEngine) -> None:
        self.event_manager = event_manager
        self.gamemodel: GameEngine = gamemodel
        self.event_manager.register_listener(self)
        self.screen: pygame.surface.Surface
        self.initialised: bool = self.initialise()
        self.current_click: tuple = (None, None)
        self.check_status: dict = {}

        self.sound_played = False

    def notify(self, event: Event) -> None:
        """Notify"""
        if isinstance(event, Highlight):
            self.current_click = event.square

        if isinstance(event, TickEvent):
            self.render()

        if isinstance(event, QuitEvent):
            self.initialised = False
            pygame.quit()

        if isinstance(event, UpdateEvent):
            self.sound_played = False

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
        self.screen.fill((38, 37, 33))
        self.draw_board()
        self.draw_move_log()
        self.draw_file_and_rank()
        self.draw_username_and_captured_pieces()

        if self.sound_played is not True:
            self.play_sounds()
            self.sound_played = True

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
                    self.screen, color, pygame.Rect(col * View.SIZE, View.TOP_PANEL + row * View.SIZE, View.SIZE, View.SIZE)
                )
                # fmt: off
                piece = board[row][col]
                if piece != "--":
                    image = View.IMAGES[piece]
                    self.screen.blit(image,pygame.Rect(col * View.SIZE, View.TOP_PANEL + row * View.SIZE,View.SIZE,View.SIZE,))
                # fmt: on

    def draw_move_log(self) -> None:
        """Draw the move log onto the screen"""
        font = pygame.font.Font("freesansbold.ttf", 14)
        position = [544, 672]
        height = font.get_height()

        txt_surface = font.render("White", True, pygame.Color("white"), pygame.SRCALPHA)
        self.screen.blit(txt_surface, (544, 5))

        txt_surface = font.render("Black", True, pygame.Color("white"), pygame.SRCALPHA)
        self.screen.blit(txt_surface, (672, 5))

        seperator = font.render("|", True, pygame.Color("white"), pygame.SRCALPHA)
        for count, text in enumerate(self.gamemodel.move_log):
            txt_surface = font.render(text, True, pygame.Color("white"), pygame.SRCALPHA)
            self.screen.blit(txt_surface, (position[count % 2], 20 + (height * (math.floor(count / 2)))))
            self.screen.blit(seperator, (630, 20 + (height * (math.floor(count / 2)))))

    def draw_file_and_rank(self) -> None:
        """Draw the rank and file onto the screen"""
        font = pygame.font.Font("freesansbold.ttf", 12)
        ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]
        files = ["a", "b", "c", "d", "e", "f", "g", "h"]
        if self.gamemodel.color == "black":
            ranks = ranks[::-1]
            files = files[::-1]

        for count in range(View.DIMENSION):  # Loop through each rank
            rank = font.render(ranks[count], True, pygame.Color("Black"))
            self.screen.blit(rank, pygame.Rect(500, View.TOP_PANEL + count * View.SIZE + 5, View.SIZE, View.SIZE))

            file = font.render(files[count], True, pygame.Color("Black"))
            self.screen.blit(file, pygame.Rect(count * View.SIZE + 2, View.TOP_PANEL + 500, View.SIZE, View.SIZE))

    def draw_username_and_captured_pieces(self) -> None:
        font = pygame.font.Font('freesansbold.ttf', 14)
        white: str = "Michael"
        black: str = "Joshua"

        white_text = font.render(white, True, View.WHITE, pygame.SRCALPHA)
        black_text = font.render(black, True, View.WHITE, pygame.SRCALPHA)

        black_king = View.IMAGES['bK']
        black_king = pygame.transform.scale(black_king,(40,40))
        white_king = View.IMAGES['wK']
        white_king = pygame.transform.scale(white_king,(40,40))

        pygame.draw.rect(self.screen, View.WHITE, pygame.Rect(5, 5, 40, 40))
        pygame.draw.rect(self.screen, View.WHITE, pygame.Rect(5, 567, 40, 40))

        if self.gamemodel.color == "black":
            self.screen.blit(white_text, View.TOP_USERNAME_LOCATION)
            self.screen.blit(black_text, View.BOT_USERNAME_LOCATION)
            self.screen.blit(white_king, View.TOP_IMAGE_LOCATION)
            self.screen.blit(black_king, View.BOT_IMAGE_LOCATION)
        else:
            self.screen.blit(white_text, View.BOT_USERNAME_LOCATION)
            self.screen.blit(black_text, View.TOP_USERNAME_LOCATION)
            self.screen.blit(black_king, View.TOP_IMAGE_LOCATION)
            self.screen.blit(white_king, View.BOT_IMAGE_LOCATION)


        if self.gamemodel.captured_pieces.get('white'):
            white_pieces = self.gamemodel.captured_pieces['white']
            last_piece: str = ""
            gap = 0
            for count, piece in enumerate(white_pieces):
                if piece != last_piece:
                    last_piece = piece
                    gap += 1
                image = View.IMAGES[piece]
                image = pygame.transform.scale(image, (30, 30))
                if self.gamemodel.color == "black":
                    self.screen.blit(image,(25 + (gap *20 )+ count*5,20))
                else:
                    self.screen.blit(image,(25 + (gap *20 )+ count*5,582))

        if self.gamemodel.captured_pieces.get('black'):
            black_pieces = self.gamemodel.captured_pieces['black']
            last_piece: str = ""
            gap = 0
            for count, piece in enumerate(black_pieces):
                if piece != last_piece:
                    last_piece = piece
                    gap += 1
                image = View.OUTLINED_IMAGES[piece]
                image = pygame.transform.scale(image, (30, 30))
                if self.gamemodel.color == "black":
                    self.screen.blit(image,(25 + (gap *20 ) +count*5,582))
                else:
                    self.screen.blit(image,(25 + (gap *20 ) +count*5,20))

    def highlight_square(self) -> None:
        """Highlight the square that a user clicks on, also show possible moves if its their piece"""
        highlight: pygame.Surface = self.create_highlight("blue")
        cords: str = "".join(str(point) for point in self.current_click)

        self.screen.blit(highlight, (self.current_click[0] * View.SIZE, View.TOP_PANEL + self.current_click[1] * View.SIZE))
        for move in self.gamemodel.moves:
            if cords == move.split(":")[0]:
                self.screen.blit(
                    highlight, (int(move.split(":")[1][0]) * View.SIZE, View.TOP_PANEL + int(move.split(":")[1][1]) * View.SIZE)
                )

    def play_sounds(self) -> None:
        """Play the sound based on the last move"""
        if not self.gamemodel.move_log:
            return
        latest_move = self.gamemodel.move_log[-1]

        if "#" in latest_move:
            pygame.mixer.music.load(View.SOUNDS["Gameover"])
            pygame.mixer.music.play()
        elif "+" in latest_move:
            pygame.mixer.music.load(View.SOUNDS["Check"])
            pygame.mixer.music.play()
        elif latest_move in ("0-0", "0-0-0"):
            pygame.mixer.music.load(View.SOUNDS["Castle"])
            pygame.mixer.music.play()
        elif "x" in latest_move:
            pygame.mixer.music.load(View.SOUNDS["Capture"])
            pygame.mixer.music.play()
        else:
            pygame.mixer.music.load(View.SOUNDS["Move"])
            pygame.mixer.music.play()

    def highlight_check(self) -> None:
        """Highlight the pieces if a king is in check"""

        red_highlight: pygame.Surface = self.create_highlight("red")
        green_highlight: pygame.Surface = self.create_highlight("green")

        king_loc = self.check_status["king_location"]
        attacking_pieces = self.check_status["attacking_pieces"]

        if self.gamemodel.color == "black":
            king_loc = invert_move(king_loc)
            attacking_pieces = list(map(invert_move, attacking_pieces))

        self.screen.blit(green_highlight, (int(king_loc[0]) * View.SIZE, View.TOP_PANEL + int(king_loc[1]) * View.SIZE))
        for pieces in attacking_pieces:
            self.screen.blit(red_highlight, (int(pieces[0]) * View.SIZE, View.TOP_PANEL +  int(pieces[1]) * View.SIZE))

    def load_images(self) -> None:
        """Load the images into a dictionary"""
        # fmt: off
        pieces = ["wP","wR","wN","wB","wQ","wK","bP","bN","bQ","bR","bB","bK",]
        outlined_pieces = ["bP","bN","bQ","bR","bB","bK"]
        # fmt: on
        for piece in pieces:
            View.IMAGES[piece] = pygame.image.load("src/chess/assets/images/" + piece + ".png")

        for piece in outlined_pieces:
            View.OUTLINED_IMAGES[piece] = pygame.image.load("src/chess/assets/images/outlined/" + piece + ".png")


    def load_sounds(self) -> None:
        """Load the sounds"""
        View.SOUNDS["Move"] = "src/chess/assets/sounds/piece_move.ogg"
        View.SOUNDS["Capture"] = "src/chess/assets/sounds/piece_capture.ogg"
        View.SOUNDS["Check"] = "src/chess/assets/sounds/piece_check.ogg"
        View.SOUNDS["Gameover"] = "src/chess/assets/sounds/game_over.ogg"
        View.SOUNDS["Castle"] = "src/chess/assets/sounds/castle.ogg"

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
        self.screen = pygame.display.set_mode((512 + View.RIGHT_PANEL, View.TOP_PANEL + 512 + View.BOT_PANEL))
        self.load_images()
        self.load_sounds()
        return True

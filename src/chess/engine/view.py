from src.chess.engine.event import EventManager, QuitEvent, TickEvent, UpdateEvent
from src.chess.engine.game import GameEngine
import pygame

class View:

    WIDTH = HEIGHT = 512  # Heigh and width of the board
    DIMENSION = 8  # This will cause 8 squares to be print on the board
    SQSIZE = HEIGHT / DIMENSION  # Dimensions of the square

    GREEN: tuple = (119, 149, 86) # Off Green colour
    WHITE: tuple = (235, 235, 208) # Off White Color

    def __init__(self,event_manager: EventManager, gamemodel: GameEngine):
        self.event_manager = event_manager
        self.gamemodel = gamemodel
        self.event_manager.register_listener(self)
        self.screen: pygame.Surface = None
        self.images: dict = {}
        self.initialise()

    def notify(self, event):
        """Notify"""
        if isinstance(event, TickEvent):
            self.render()
        if isinstance(event, QuitEvent):
            self.initialised = False
            pygame.quit()  # pylint: disable=no-member

    def render(self):
        """Render"""
        self.draw_board()
        pygame.display.flip()


    def draw_board(self):
        """Render the board"""
        board: list = self.gamemodel.board
        colors: list = [View.WHITE, View.GREEN]

        for row in range(View.DIMENSION):
            for col in range(View.DIMENSION):
                color = colors[((row + col) % 2)]

                pygame.draw.rect(
                    self.screen,
                    color,
                    pygame.Rect(col * View.SQSIZE, row * View.SQSIZE, View.SQSIZE, View.SQSIZE),)

                piece = board[row][col]
                if piece != "--":
                    self.screen.blit(
                        self.images[piece],
                        pygame.Rect(col * View.SQSIZE,row * View.SQSIZE,View.SQSIZE,View.SQSIZE,),)

    def load_images(self):
        """Load the images into a dictionary"""
        pieces = ["wP","wR","wN","wB","wQ","wK","bP","bN","bQ","bR","bB","bK",]
        for piece in pieces:
            self.images[piece] = pygame.image.load("src/chess/assets/images/" + piece + ".png")

    def initialise(self):
        """Create and initialise a pygame instance"""
        pygame.init()
        pygame.display.set_caption("Chess Engine")
        self.screen: pygame.Surface = pygame.display.set_mode((512, 512))
        self.load_images()
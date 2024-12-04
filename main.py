from DataClasses import Pieces
from DataClasses.Images import imageResources as Images
from DataClasses.Board import Board
from MovementManger import GetMovements
from MovementManger import IsCheckMate
import settings
import pygame


class ChessBoard:
    def __init__(self, screen: pygame.display, useDefaultBoard: bool = True, board: list[list[str]] = None):
        """
        Initialize a new ChessBoard object.

        Parameters:
        screen (pygame.display): The Pygame display to draw the board on.

        Initializes a new Board object and starts the game loop.
        """

        self.screen: pygame.display = screen
        self.board: Board = Board()
        if useDefaultBoard:
            self.board.generateDefaultBoard()
        else:
            if board:
                self.board.board = board
            else:
                raise ValueError("No board provided")
        self.SelectedCoords: tuple = (-1, -1)
        self.PossiblePositions: list = []

        self.CurrentTurn = "White"
        pygame.init()
        self.moveAudio = pygame.mixer.Sound("res/audio/moveAudio.mp3")
        print("Starting game")

        self.RunGame()

    def IsCheckMate(self, Color: str):
        # will check if the king is gone
        
        for Y in self.board:
            for X in self.board[Y]:
                if self.board[Y][X].Type == "King" and self.board[Y][X].Color == Color:
                    return False
    def draw(self):
        # will set the background to the board image
        """
        Draws the chess board and pieces on the screen.

        This function sets the background to the board image and overlays any selected
        pieces with a semi-transparent cyan square. It iterates over each slot on the
        board, rendering each piece at its respective position.

        The function assumes that `self.SelectedCoords` contains the coordinates of the
        selected piece, and that the board object can determine if a piece exists at a
        given coordinate and retrieve the piece image.

        :return: None
        """
        self.screen.fill((255, 255, 255))
        self.screen.blit(pygame.image.load(Images.Board), (0, 0))
        """font = pygame.font.Font('freesansbold.ttf', 32)
        # will draw debug postions using the size of each cube
        for i in range(settings.BoardSize[0]):
            for j in range(settings.BoardSize[1]):
                text = font.render(str((i, j)), True, (0, 0, 0))
                self.screen.blit(text, (i*settings.SlotSize, j*settings.SlotSize))"""
        for y in range(settings.BoardSize[0]):
            for x in range(settings.BoardSize[1]):
                
                if (x, y) in self.PossiblePositions:
                    # Draw a smaller green circle with opacity for possible moves
                    center_x = x * settings.SlotSize + settings.SlotSize // 2
                    center_y = y * settings.SlotSize + settings.SlotSize // 2
                    radius = settings.SlotSize // 4  # Make the indicator 1/4 of the slot size
                    pygame.draw.circle(
                        self.screen,
                        (0, 255, 0, 128),  # Green with opacity
                        (center_x, center_y),
                        radius
                    )
                
                if self.SelectedCoords == (x, y):
                    # Draw a subtle highlight for the selected piece
                    pygame.draw.rect(
                        self.screen,
                        (135, 206, 235, 80),  # Light sky blue with lower opacity
                        (
                            x * settings.SlotSize,
                            y * settings.SlotSize,
                            settings.SlotSize,
                            settings.SlotSize,
                        ),
                    )
                if self.board.isPiece(x, y):
                    piece = self.board.getPiece(x, y)
                    if piece == None:
                        continue
                    self.screen.blit(
                        pygame.image.load(piece.Image),
                        (x * settings.SlotSize, y * settings.SlotSize),
                    )

    def RunGame(self):
        """
        Runs the main game loop for the chess application.

        This method continuously checks for events, such as quitting the game or mouse clicks.
        It updates the selected piece coordinates based on mouse clicks and redraws the board
        if necessary. The game loop runs indefinitely, refreshing the display at 24 frames per second.

        :return: None
        """
        self.draw()
        clock = pygame.time.Clock()
        Updated = False
        while True:
            Updated = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    x = int(pos[0] // settings.SlotSize)
                    y = int(pos[1] // settings.SlotSize)
                    print(x, y)
                    piece: Pieces.PieceImage = self.board.getPiece(x, y)
                    
                    if (x,y) in self.PossiblePositions:
                        print("Moving piece")
                        if self.board.getPiece(self.SelectedCoords[0], self.SelectedCoords[1]) == None:
                            continue
                        SelectedPiece = self.board.getPiece(self.SelectedCoords[0], self.SelectedCoords[1])
                        
                        if SelectedPiece.Color == self.CurrentTurn:
                            self.board.movePiece(self.SelectedCoords[0], self.SelectedCoords[1], x, y)
                            # will play the audio named moveAudio.mp3 in res/audio
                            
                            self.moveAudio.play()
                            
                            self.SelectedCoords = (-1, -1)
                            self.PossiblePositions = []
                            
                            checkmate = IsCheckMate(self.board, self.CurrentTurn)
                            if checkmate:
                                print("Checkmate")
                                pygame.quit()
                                exit()
                            
                            self.CurrentTurn = "White" if self.CurrentTurn == "Black" else "Black"

                            continue
                            
                    if piece != None:
                        # print(piece.name)
                        if piece.Color != self.CurrentTurn:
                            continue
                        self.SelectedCoords = (x, y)
                        
                        try:
                            self.PossiblePositions = GetMovements(x, y, self.board)
                        except NotImplementedError:
                            print(
                                f"Piece {piece.Name} moves has not been implemented yet"
                            )
                            self.PossiblePositions = []
                    else:
                        # print("No piece")
                        self.SelectedCoords = (-1, -1)
                        self.PossiblePositions = []
                if not Updated:
                    self.draw()
                    pygame.display.update()
                    pygame.display.set_caption(
                                f"Chess - {self.CurrentTurn} Turn"
                            )
                    Updated = True
                    
            clock.tick(24)


screen = pygame.display.set_mode(settings.ScreenSize)

# Custom board setup for checkmate in one move
checkmate_board = [
    ['-', '-', 'WQ', '-', 'BK', '-', '-', '-'],  # Black king on e8
    ['-', '-', '-', '-', '-', 'BP', 'BP', '-'],  # Black pawns on f7, g7
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', 'WQ', '-', '-', '-', '-'],
    ['-', '-', '-', '-', '-', '-', '-', '-'],  # White queen on d3
    ['-', '-', '-', '-', '-', '-', '-', '-'],
    ['-', '-', '-', '-', 'WK', '-', '-', '-'],  # White king on e1
]

ChessBoard(screen, useDefaultBoard=False, board=checkmate_board)

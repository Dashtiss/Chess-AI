from DataClasses import Pieces
from DataClasses.Images import imageResources as Images
from DataClasses.Board import Board
from MovementManger import GetMovements
import settings
import pygame


class ChessBoard:
    def __init__(self, screen: pygame.display):
        """
        Initialize a new ChessBoard object.

        Parameters:
        screen (pygame.display): The Pygame display to draw the board on.

        Initializes a new Board object and starts the game loop.
        """

        self.screen: pygame.display = screen
        self.board: Board = Board()
        self.board.generateDefaultBoard()
        self.SelectedCoords: tuple = (-1, -1)
        self.PossiblePositions: list = []

        self.CurrentTurn = "White"
        pygame.init()

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
                    pygame.draw.rect(
                        self.screen,
                        (255, 0, 0, 128),
                        (
                            x * settings.SlotSize,
                            y * settings.SlotSize,
                            settings.SlotSize,
                            settings.SlotSize,
                        ),
                    )
                
                if self.SelectedCoords == (x, y):
                    # will put a cyan square with a 50% opacity over the selected piece
                    pygame.draw.rect(
                        self.screen,
                        (0, 255, 255, 128),
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
                            self.SelectedCoords = (-1, -1)
                            self.PossiblePositions = []
                            
                            checkmate = self.IsCheckMate("White" if self.CurrentTurn == "Black" else "Black")
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

ChessBoard(screen)

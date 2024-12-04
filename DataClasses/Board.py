# Board Class
from . import Pieces
from copy import deepcopy
class Board(list):
    def __init__(self):
        """
        Initializes a new Board object.

        The board is an 8x8 grid and is initially empty, with all pieces represented as '-'.
        """
        super().__init__()
        self.board = [
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-']
        ]
        self.OriginalBoard = deepcopy(self.board)
        
        self.LastMove: tuple[tuple[int, int], tuple[int, int]] = ((-1, -1), (-1, -1))
        
    def copy(self):
        board_copy = Board()
        for y in range(8):
            for x in range(8):
                if self.isPiece(x, y):
                    board_copy.setPiece(x, y, self.getPiece(x, y))
        return board_copy
        
    def isPiece(self, x: int, y: int):
        """
        Check if there is a piece at the given coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.

        Returns:
        bool: True if there is a piece at the specified coordinates, False otherwise.
        """
        
        #print(x, y)
        try:
            return self.board[y][x] != '-'
        except IndexError:
            return False
    
    def getPiece(self, x: int, y: int) -> Pieces.PieceImage | None:
        """
        Get a piece from the board at the given coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.

        Returns:
        Pieces.PieceImage | None: The piece at the specified coordinates, or None if there is no piece.
        """
        
        try:
            if self.board[y][x] == '-':
                return None
            return Pieces.pieces[self.board[y][x]]
        except IndexError:
            return None
    
    def setPiece(self, x: int, y: int, piece: str | Pieces.PieceImage) -> None:
        """
        Place a piece on the board at the specified coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.
        piece (str | Pieces.PieceImage): The piece to place on the board.

        Returns:
        None
        """
        if isinstance(piece, str):
            if piece in Pieces.pieces.keys():
                self.board[y][x] = piece
            else:
                self.board[y][x] = '-'
        elif isinstance(piece, Pieces.PieceImage):
            # If it's a PieceImage, store its name (like 'WK', 'BP', etc.)
            self.board[y][x] = piece.Name
        else:
            self.board[y][x] = '-'
            
        
    
    def removePiece(self, x: int, y: int):
        """
        Removes a piece from the board at the specified coordinates.

        Parameters:
        y (int): The y-coordinate (column) on the board.
        """
        #print(x, y)
        self.board[y][x] = '-'
        
    def printBoard(self):
        """
        Prints the current state of the board to the console.
        """
        
        for row in self.board:
            print(row, sep=" ", )
            
    def generateDefaultBoard(self):
        """
        Generate a default chess board.

        The default board is an 8x8 grid. The first row is the black pieces, the second row is the black pawns,
        the third through sixth rows are empty, the seventh row is the white pawns, and the eighth row is the white
        pieces. The pieces are represented as the following strings: 'BR', 'BK', 'BB', 'BQ', 'BP', 'WR', 'WK', 'WB',
        'WQ', 'WP'.

        :return: None
        """
        self.board = [
            ['BR', 'BN', 'BB', 'BQ', 'BK', 'BB', 'BN', 'BR'],
            ['BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP'],
            ['WR', 'WN', 'WB', 'WQ', 'WK', 'WB', 'WN', 'WR'],
        ]
        self.OriginalBoard = deepcopy(self.board)
    
    def movePiece(self, x1: int, y1: int, x2: int, y2: int):
        piece = self.getPiece(x1, y1)
        self.setPiece(x2, y2, piece.Name)
        self.removePiece(x1, y1)
        self.previous_board = self.copy()  # Keep track of the previous board state

    def undoMove(self):
        self.board = self.previous_board.board  # Restore the previous board state
        self.previous_board = None  # Clear the previous board state

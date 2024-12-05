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
        self.previous_states = []  # Stack of previous board states
        self.LastMove: tuple[tuple[int, int], tuple[int, int]] = ((-1, -1), (-1, -1))
        # Track if kings and rooks have moved for castling
        self.moved_pieces = {
            'WK': False,  # White King
            'BK': False,  # Black King
            'WR1': False, # White Rook (queenside)
            'WR2': False, # White Rook (kingside)
            'BR1': False, # Black Rook (queenside)
            'BR2': False  # Black Rook (kingside)
        }
        
    def copy(self):
        """Create a deep copy of the current board state."""
        board_copy = Board()
        board_copy.board = deepcopy(self.board)
        board_copy.moved_pieces = deepcopy(self.moved_pieces)
        board_copy.LastMove = self.LastMove
        return board_copy
        
    def isPiece(self, x: int, y: int) -> bool:
        """
        Check if there is a piece at the given coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.

        Returns:
        bool: True if there is a piece at the specified coordinates, False otherwise.
        """
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
            piece_name = self.board[y][x]
            if piece_name == '-':
                return None
            return Pieces.pieces[piece_name]
        except (IndexError, KeyError):
            return None
    
    def setPiece(self, x: int, y: int, piece: Pieces.PieceImage):
        """
        Set a piece at the given coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.
        piece (PieceImage): The piece to set at the coordinates.
        """
        self.board[y][x] = piece.Name if piece else '-'
        
        # Track piece movements for castling
        if piece and piece.Type == "King":
            if piece.Color == "White":
                self.moved_pieces['WK'] = True
            else:
                self.moved_pieces['BK'] = True
        elif piece and piece.Type == "Rook":
            if piece.Color == "White":
                if x == 0:  # Queenside rook
                    self.moved_pieces['WR1'] = True
                elif x == 7:  # Kingside rook
                    self.moved_pieces['WR2'] = True
            else:
                if x == 0:  # Queenside rook
                    self.moved_pieces['BR1'] = True
                elif x == 7:  # Kingside rook
                    self.moved_pieces['BR2'] = True
    
    def removePiece(self, x: int, y: int):
        """
        Remove a piece from the given coordinates.

        Parameters:
        x (int): The x-coordinate (row) on the board.
        y (int): The y-coordinate (column) on the board.
        """
        self.board[y][x] = '-'
        
    def handleCastling(self, from_x: int, from_y: int, to_x: int, to_y: int):
        """
        Handle castling move by moving both the king and the rook.
        Returns True if castling was performed, False otherwise.
        """
        # Check if this is a castling move
        if self.getPiece(from_x, from_y).Type != "King":
            return False
            
        # Determine if this is a castling move based on the king's movement
        if abs(to_x - from_x) != 2 or from_y != to_y:
            return False
            
        # Handle kingside castling
        if to_x == 6:
            rook = self.getPiece(7, from_y)
            if rook and rook.Type == "Rook":
                # Move the rook
                self.setPiece(5, from_y, rook)
                self.removePiece(7, from_y)
                return True
                
        # Handle queenside castling
        elif to_x == 2:
            rook = self.getPiece(0, from_y)
            if rook and rook.Type == "Rook":
                # Move the rook
                self.setPiece(3, from_y, rook)
                self.removePiece(0, from_y)
                return True
                
        return False
    
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
        self.setPiece(x2, y2, piece)
        self.removePiece(x1, y1)
        self.previous_states.append(self.copy())  # Keep track of the previous board state

    def undoMove(self):
        if self.previous_states:
            self.board = self.previous_states.pop().board  # Restore the previous board state

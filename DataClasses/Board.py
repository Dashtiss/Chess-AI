# Board Class
from typing import List, Tuple, Dict, Optional
from . import Pieces
from copy import deepcopy

class Board:
    def __init__(self):
        """
        Initializes a new Board object.
        The board is an 8x8 grid and is initially empty, with all pieces represented as '-'.
        """
        self.board: List[List[str]] = [
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-']
        ]
        self.OriginalBoard: List[List[str]] = deepcopy(self.board)
        self.previous_states: List['Board'] = []  # Stack of previous board states
        self.LastMove: Tuple[Tuple[int, int], Tuple[int, int]] = ((-1, -1), (-1, -1))
        self.en_passant_target: Optional[Tuple[int, int]] = None  # Square where en passant capture is possible
        
        # Track if kings and rooks have moved for castling
        self.moved_pieces: Dict[str, bool] = {
            'WK': False,  # White King
            'BK': False,  # Black King
            'WR1': False, # White Rook (queenside)
            'WR2': False, # White Rook (kingside)
            'BR1': False, # Black Rook (queenside)
            'BR2': False  # Black Rook (kingside)
        }
        
    def copy(self) -> 'Board':
        """Create a deep copy of the current board state."""
        board_copy = Board()
        board_copy.board = deepcopy(self.board)
        board_copy.moved_pieces = deepcopy(self.moved_pieces)
        board_copy.LastMove = self.LastMove
        board_copy.en_passant_target = self.en_passant_target
        return board_copy
        
    def isPiece(self, x: int, y: int) -> bool:
        """Check if there is a piece at the given coordinates."""
        try:
            return self.board[y][x] != '-'
        except IndexError:
            return False
    
    def getPiece(self, x: int, y: int) -> Optional[Pieces.PieceImage]:
        """Get a piece from the board at the given coordinates."""
        try:
            piece_name = self.board[y][x]
            if piece_name == '-':
                return None
            return Pieces.pieces[piece_name]
        except (IndexError, KeyError):
            return None
    
    def setPiece(self, x: int, y: int, piece: Optional[Pieces.PieceImage], from_pos: Optional[Tuple[int, int]] = None) -> None:
        """Set a piece at the given coordinates."""
        if not (0 <= x < 8 and 0 <= y < 8):
            return
            
        self.board[y][x] = piece.Name if piece else '-'
        
        # Update en passant target if this is a pawn's double move
        if piece and piece.Type == Pieces.PieceType.PAWN and from_pos:
            from_x, from_y = from_pos
            if abs(y - from_y) == 2:  # Double pawn move
                # Set en passant target to the square the pawn passed through
                self.en_passant_target = (x, (from_y + y) // 2)
            else:
                self.en_passant_target = None
        elif not from_pos:
            self.en_passant_target = None
        
        # Track piece movements for castling
        if piece:
            if piece.Type == Pieces.PieceType.KING:
                if piece.Color == Pieces.PieceColor.WHITE:
                    self.moved_pieces['WK'] = True
                else:
                    self.moved_pieces['BK'] = True
            elif piece.Type == Pieces.PieceType.ROOK:
                if piece.Color == Pieces.PieceColor.WHITE:
                    if x == 0:  # Queenside rook
                        self.moved_pieces['WR1'] = True
                    elif x == 7:  # Kingside rook
                        self.moved_pieces['WR2'] = True
                else:
                    if x == 0:  # Queenside rook
                        self.moved_pieces['BR1'] = True
                    elif x == 7:  # Kingside rook
                        self.moved_pieces['BR2'] = True
    
    def removePiece(self, x: int, y: int) -> None:
        """Remove a piece from the given coordinates."""
        if not (0 <= x < 8 and 0 <= y < 8):
            return
        self.board[y][x] = '-'
        
    def handleCastling(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Handle castling move by moving both the king and the rook."""
        piece = self.getPiece(from_x, from_y)
        if not piece or piece.Type != Pieces.PieceType.KING:
            return False
            
        # Determine if this is a castling move based on the king's movement
        if abs(to_x - from_x) != 2 or from_y != to_y:
            return False
            
        # Handle kingside castling
        if to_x == 6:
            rook = self.getPiece(7, from_y)
            if rook and rook.Type == Pieces.PieceType.ROOK:
                # Move the rook
                self.setPiece(5, from_y, rook)
                self.removePiece(7, from_y)
                return True
                
        # Handle queenside castling
        elif to_x == 2:
            rook = self.getPiece(0, from_y)
            if rook and rook.Type == Pieces.PieceType.ROOK:
                # Move the rook
                self.setPiece(3, from_y, rook)
                self.removePiece(0, from_y)
                return True
                
        return False
    
    def printBoard(self) -> None:
        """Print the current state of the board to the console."""
        for row in self.board:
            print(row)
            
    def generateDefaultBoard(self) -> None:
        """Generate a default chess board."""
        # Initialize an empty board
        self.board = [
            ['BR', 'BN', 'BB', 'BQ', 'BK', 'BB', 'BN', 'BR'],
            ['BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP', 'BP'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['-', '-', '-', '-', '-', '-', '-', '-'],
            ['WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP', 'WP'],
            ['WR', 'WN', 'WB', 'WQ', 'WK', 'WB', 'WN', 'WR']
        ]
        # Save initial state
        self.OriginalBoard = deepcopy(self.board)
        print("Board initialized with pieces:")  # Debug print
        self.printBoard()  # Debug print

    def movePiece(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Move a piece from one position to another."""
        if not (0 <= x1 < 8 and 0 <= y1 < 8 and 0 <= x2 < 8 and 0 <= y2 < 8):
            print(f"Invalid move coordinates: ({x1}, {y1}) -> ({x2}, {y2})")  # Debug print
            return
            
        piece = self.getPiece(x1, y1)
        if piece:
            print(f"Moving {piece.Type.value} from ({x1}, {y1}) to ({x2}, {y2})")  # Debug print
            # Save the current state
            self.previous_states.append(self.copy())
            # Update the board
            self.setPiece(x2, y2, piece, (x1, y1))
            self.removePiece(x1, y1)
            # Update last move
            self.LastMove = ((x1, y1), (x2, y2))
            print("Board after move:")  # Debug print
            self.printBoard()  # Debug print
        else:
            print(f"No piece found at ({x1}, {y1})")  # Debug print

    def undoMove(self) -> None:
        """Undo the last move if possible."""
        if self.previous_states:
            previous = self.previous_states.pop()
            self.board = previous.board
            self.moved_pieces = previous.moved_pieces
            self.LastMove = previous.LastMove
            self.en_passant_target = previous.en_passant_target

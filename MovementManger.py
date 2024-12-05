from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum
from DataClasses.Board import Board
from DataClasses.Pieces import PieceType, PieceImage

@dataclass
class MoveContext:
    """Context for move validation and generation"""
    board: Board
    from_pos: Tuple[int, int]
    color: str
    cache: Dict[str, Set[Tuple[int, int]]] = None
    
    def __post_init__(self):
        if self.cache is None:
            self.cache = {}

def is_valid_position(x: int, y: int) -> bool:
    """Check if a position is within the board boundaries"""
    return 0 <= x <= 7 and 0 <= y <= 7

def get_straight_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible straight moves (horizontal and vertical)"""
    moves = set()
    x, y = ctx.from_pos
    
    # Check all four directions
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        curr_x, curr_y = x + dx, y + dy
        while is_valid_position(curr_x, curr_y):
            target = ctx.board.getPiece(curr_x, curr_y)
            if not target:
                moves.add((curr_x, curr_y))
            else:
                if target.Color.value != ctx.color:
                    moves.add((curr_x, curr_y))
                break
            curr_x, curr_y = curr_x + dx, curr_y + dy
    
    return moves

def get_diagonal_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible diagonal moves"""
    moves = set()
    x, y = ctx.from_pos
    
    # Check all four diagonal directions
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in directions:
        curr_x, curr_y = x + dx, y + dy
        while is_valid_position(curr_x, curr_y):
            target = ctx.board.getPiece(curr_x, curr_y)
            if not target:
                moves.add((curr_x, curr_y))
            else:
                if target.Color.value != ctx.color:
                    moves.add((curr_x, curr_y))
                break
            curr_x, curr_y = curr_x + dx, curr_y + dy
    
    return moves

def get_pawn_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible pawn moves"""
    moves = set()
    x, y = ctx.from_pos
    
    # Direction is -1 for White (moving up the board) and 1 for Black (moving down)
    direction = -1 if ctx.color == "White" else 1
    start_row = 6 if ctx.color == "White" else 1
    
    # Forward move
    new_y = y + direction
    if 0 <= new_y < 8:
        # Single step forward
        if not ctx.board.isPiece(x, new_y):
            moves.add((x, new_y))
            # Double step from starting position
            if y == start_row and not ctx.board.isPiece(x, y + 2 * direction):
                moves.add((x, y + 2 * direction))
    
    # Diagonal captures
    for dx in [-1, 1]:
        new_x = x + dx
        new_y = y + direction
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            # Normal capture
            target = ctx.board.getPiece(new_x, new_y)
            if target and target.Color.value != ctx.color:
                moves.add((new_x, new_y))
            # En passant capture
            elif ctx.board.en_passant_target == (new_x, new_y):
                moves.add((new_x, new_y))
    
    return moves

def get_knight_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible knight moves"""
    moves = set()
    x, y = ctx.from_pos
    
    knight_moves = [
        (x + 2, y + 1), (x + 2, y - 1),
        (x - 2, y + 1), (x - 2, y - 1),
        (x + 1, y + 2), (x + 1, y - 2),
        (x - 1, y + 2), (x - 1, y - 2)
    ]
    
    for move_x, move_y in knight_moves:
        if is_valid_position(move_x, move_y):
            target = ctx.board.getPiece(move_x, move_y)
            if not target or target.Color.value != ctx.color:
                moves.add((move_x, move_y))
    
    return moves

def get_king_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible king moves including castling"""
    moves = set()
    x, y = ctx.from_pos
    
    # Normal king moves
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < 8 and 0 <= new_y < 8:
                target = ctx.board.getPiece(new_x, new_y)
                if not target or target.Color.value != ctx.color:
                    moves.add((new_x, new_y))
    
    # Castling moves
    if not ctx.board.moved_pieces.get(f"{ctx.color[0]}K", False):  # King hasn't moved
        # Kingside castling
        if not ctx.board.moved_pieces.get(f"{ctx.color[0]}R2", False):  # Kingside rook hasn't moved
            if not any(ctx.board.isPiece(x, y) for x in [5, 6]):  # Path is clear
                moves.add((6, y))
        
        # Queenside castling
        if not ctx.board.moved_pieces.get(f"{ctx.color[0]}R1", False):  # Queenside rook hasn't moved
            if not any(ctx.board.isPiece(x, y) for x in [1, 2, 3]):  # Path is clear
                moves.add((2, y))
    
    return moves

def get_queen_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible queen moves (combination of straight and diagonal)"""
    return get_straight_moves(ctx) | get_diagonal_moves(ctx)

def get_bishop_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible bishop moves"""
    return get_diagonal_moves(ctx)

def get_rook_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible rook moves"""
    moves = set()
    x, y = ctx.from_pos
    
    # Check all four directions
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        while 0 <= new_x < 8 and 0 <= new_y < 8:
            target = ctx.board.getPiece(new_x, new_y)
            if not target:
                moves.add((new_x, new_y))
            elif target.Color.value != ctx.color:
                moves.add((new_x, new_y))
                break
            else:
                break
            new_x, new_y = new_x + dx, new_y + dy
    
    return moves

def get_bishop_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible bishop moves"""
    moves = set()
    x, y = ctx.from_pos
    
    # Check all four diagonal directions
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        while 0 <= new_x < 8 and 0 <= new_y < 8:
            target = ctx.board.getPiece(new_x, new_y)
            if not target:
                moves.add((new_x, new_y))
            elif target.Color.value != ctx.color:
                moves.add((new_x, new_y))
                break
            else:
                break
            new_x, new_y = new_x + dx, new_y + dy
    
    return moves

def get_queen_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible queen moves (combination of rook and bishop moves)"""
    return get_rook_moves(ctx) | get_bishop_moves(ctx)

def get_knight_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible knight moves"""
    moves = set()
    x, y = ctx.from_pos
    
    # All possible knight moves
    knight_moves = [
        (x + 2, y + 1), (x + 2, y - 1),
        (x - 2, y + 1), (x - 2, y - 1),
        (x + 1, y + 2), (x + 1, y - 2),
        (x - 1, y + 2), (x - 1, y - 2)
    ]
    
    # Filter valid moves
    for new_x, new_y in knight_moves:
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            target = ctx.board.getPiece(new_x, new_y)
            if not target or target.Color.value != ctx.color:
                moves.add((new_x, new_y))
    
    return moves

def get_piece_moves(board: Board, x: int, y: int, check_king_safety=True) -> Set[Tuple[int, int]]:
    """Get all possible moves for a piece at the given position"""
    piece = board.getPiece(x, y)
    if not piece:
        return set()
    
    ctx = MoveContext(board=board, from_pos=(x, y), color=piece.Color.value)
    moves = set()

    # Get raw moves based on piece type
    if piece.Type == PieceType.PAWN:
        moves = get_pawn_moves(ctx)
    elif piece.Type == PieceType.ROOK:
        moves = get_straight_moves(ctx)
    elif piece.Type == PieceType.KNIGHT:
        moves = get_knight_moves(ctx)
    elif piece.Type == PieceType.BISHOP:
        moves = get_diagonal_moves(ctx)
    elif piece.Type == PieceType.QUEEN:
        moves = get_straight_moves(ctx) | get_diagonal_moves(ctx)
    elif piece.Type == PieceType.KING:
        moves = get_king_moves(ctx)

    # Filter moves that would leave king in check
    if check_king_safety:
        valid_moves = set()
        for move in moves:
            # Create temporary board state
            temp_board = board.copy()
            temp_board.movePiece((x, y), move)
            
            # Check if king would be in check after move
            if not is_king_in_check(temp_board, piece.Color.value, check_king_moves=False):
                valid_moves.add(move)
        moves = valid_moves

    return moves

def is_square_attacked(board: Board, pos: Tuple[int, int], attacking_color: str, check_king_moves=True) -> bool:
    """Check if a square is under attack by any piece of the given color"""
    for x in range(8):
        for y in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color.value == attacking_color:
                # Skip checking king moves when checking for king attacks to prevent infinite recursion
                if not check_king_moves and piece.Type == PieceType.KING:
                    continue
                    
                ctx = MoveContext(board, (x, y), piece.Color.value)
                moves = get_piece_moves(board, x, y, check_king_safety=False)
                if pos in moves:
                    return True
    return False

def is_king_in_check(board: Board, color: str, check_king_moves=True) -> bool:
    """Check if the king of the given color is in check"""
    # Find king position
    king_pos = None
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Type == PieceType.KING and piece.Color.value == color:
                king_pos = (x, y)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False
    
    # Check if any opponent piece can attack the king
    opponent_color = "Black" if color == "White" else "White"
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color.value == opponent_color:
                # Get attacking moves without checking king safety to avoid recursion
                moves = get_piece_moves(board, x, y, check_king_safety=False)
                if king_pos in moves:
                    return True
    
    return False

def GetMovements(board: Board, x: int, y: int) -> List[Tuple[int, int]]:
    """Legacy function for compatibility - returns a list of valid moves for a piece"""
    moves = get_piece_moves(board, x, y)
    print(f"Calculating moves for piece at ({x}, {y})")  # Debug print
    print(f"Found {len(moves)} possible moves: {moves}")  # Debug print
    return list(moves)  # Convert set to list for compatibility

def IsCheckMate(board: Board, current_player_color: str) -> bool:
    """Check if the current player is in checkmate"""
    # We check if the current player is in checkmate
    return is_checkmate(board, current_player_color)

def is_checkmate(board: Board, color: str) -> bool:
    """Check if a player is in checkmate"""
    # First check if the king is in check
    if not is_king_in_check(board, color):
        return False
    
    # Try all possible moves for all pieces of the player in check
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color.value == color:
                moves = get_piece_moves(board, x, y)
                for move_x, move_y in moves:
                    # Make a copy of the board and try the move
                    board_copy = board.copy()
                    target_piece = board_copy.getPiece(move_x, move_y)
                    moving_piece = board_copy.getPiece(x, y)
                    
                    # Try the move
                    board_copy.setPiece(move_x, move_y, moving_piece)
                    board_copy.removePiece(x, y)
                    
                    # If after this move the king is not in check, it's not checkmate
                    if not is_king_in_check(board_copy, color):
                        return False
                    
                    # Restore the captured piece if there was one
                    if target_piece:
                        board_copy.setPiece(move_x, move_y, target_piece)
    
    # If we've tried all moves and none get us out of check, it's checkmate
    return True

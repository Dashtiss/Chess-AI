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
                if target.Color != ctx.color:
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
                if target.Color != ctx.color:
                    moves.add((curr_x, curr_y))
                break
            curr_x, curr_y = curr_x + dx, curr_y + dy
    
    return moves

def get_pawn_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible pawn moves"""
    moves = set()
    x, y = ctx.from_pos
    direction = -1 if ctx.color == "White" else 1
    start_row = 6 if ctx.color == "White" else 1
    
    # Forward move
    if is_valid_position(x, y + direction) and not ctx.board.isPiece(x, y + direction):
        moves.add((x, y + direction))
        # Double move from starting position
        if y == start_row and not ctx.board.isPiece(x, y + 2 * direction):
            moves.add((x, y + 2 * direction))
    
    # Diagonal captures
    for dx in [-1, 1]:
        capture_x = x + dx
        capture_y = y + direction
        if is_valid_position(capture_x, capture_y):
            target = ctx.board.getPiece(capture_x, capture_y)
            if target and target.Color != ctx.color:
                moves.add((capture_x, capture_y))
    
    return moves

def get_knight_moves(ctx: MoveContext) -> Set[Tuple[int, int]]:
    """Get all possible knight moves"""
    moves = set()
    x, y = ctx.from_pos
    
    knight_moves = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]
    
    for dx, dy in knight_moves:
        new_x, new_y = x + dx, y + dy
        if is_valid_position(new_x, new_y):
            target = ctx.board.getPiece(new_x, new_y)
            if not target or target.Color != ctx.color:
                moves.add((new_x, new_y))
    
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
            if is_valid_position(new_x, new_y):
                target = ctx.board.getPiece(new_x, new_y)
                if not target or target.Color != ctx.color:
                    moves.add((new_x, new_y))
    
    # Castling moves
    if not ctx.board.moved_pieces[f"{ctx.color[0]}K"]:
        # Kingside castling
        if not ctx.board.moved_pieces[f"{ctx.color[0]}R2"]:
            if not any(ctx.board.isPiece(x, y) for x in [5, 6]):
                if not is_king_in_check(ctx.board, ctx.color) and \
                   not is_square_attacked(ctx.board, (5, y), "Black" if ctx.color == "White" else "White"):
                    moves.add((6, y))
        
        # Queenside castling
        if not ctx.board.moved_pieces[f"{ctx.color[0]}R1"]:
            if not any(ctx.board.isPiece(x, y) for x in [1, 2, 3]):
                if not is_king_in_check(ctx.board, ctx.color) and \
                   not is_square_attacked(ctx.board, (3, y), "Black" if ctx.color == "White" else "White"):
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
    return get_straight_moves(ctx)

PIECE_MOVE_FUNCTIONS = {
    PieceType.Pawn: get_pawn_moves,
    PieceType.Knight: get_knight_moves,
    PieceType.Bishop: get_bishop_moves,
    PieceType.Rook: get_rook_moves,
    PieceType.Queen: get_queen_moves,
    PieceType.King: get_king_moves
}

def get_piece_moves(board: Board, x: int, y: int) -> Set[Tuple[int, int]]:
    """Get all possible moves for a piece at the given position"""
    piece = board.getPiece(x, y)
    if not piece:
        return set()
    
    ctx = MoveContext(board=board, from_pos=(x, y), color=piece.Color)
    return PIECE_MOVE_FUNCTIONS[piece.Type](ctx)

def is_square_attacked(board: Board, pos: Tuple[int, int], attacking_color: str) -> bool:
    """Check if a square is under attack by any piece of the given color"""
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == attacking_color:
                if pos in get_piece_moves(board, x, y):
                    return True
    return False

def is_king_in_check(board: Board, color: str) -> bool:
    """Check if a king is in check"""
    # Find king position
    king_pos = None
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Type == PieceType.King and piece.Color == color:
                king_pos = (x, y)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False
    
    # Check if king is under attack
    opponent_color = "Black" if color == "White" else "White"
    return is_square_attacked(board, king_pos, opponent_color)

def is_checkmate(board: Board, color: str) -> bool:
    """Check if a player is in checkmate"""
    if not is_king_in_check(board, color):
        return False
    
    # Try all possible moves for all pieces
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == color:
                for move in get_piece_moves(board, x, y):
                    # Try the move
                    board_copy = board.copy()
                    board_copy.movePiece(x, y, *move)
                    if not is_king_in_check(board_copy, color):
                        return False
    
    return True

def GetMovements(board: Board, x: int, y: int) -> List[Tuple[int, int]]:
    """Legacy function for compatibility"""
    return list(get_piece_moves(board, x, y))

def IsCheckMate(board: Board, current_player_color: str) -> bool:
    """Legacy function for compatibility"""
    opponent_color = "Black" if current_player_color == "White" else "White"
    return is_checkmate(board, opponent_color)

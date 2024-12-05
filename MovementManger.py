# manages where a piece can move too

from DataClasses.Board import Board
from DataClasses.Pieces import PieceImage, PieceType

def GetPawnMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a pawn at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the pawn on the board.
    y (int): The y-coordinate (row) of the pawn on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the pawn can move to.
    """
    
    piece: PieceImage = board.getPiece(x, y)
    PossibleMovements: list[tuple[int, int]] = []

    if piece.Color == "White":
        # if the pawn is white
        if y > 0:
            # check if the space in front of the pawn is empty
            if not board.isPiece(x, y - 1):
                PossibleMovements.append((x, y - 1))
            # check if the space diagonally up and to the left of the pawn is occupied by an opponent
            if x > 0 and board.isPiece(x - 1, y - 1) and board.getPiece(x - 1, y - 1).Color == "Black":
                PossibleMovements.append((x - 1, y - 1))
            # check if the space diagonally up and to the right of the pawn is occupied by an opponent
            if x < 7 and board.isPiece(x + 1, y - 1) and board.getPiece(x + 1, y - 1).Color == "Black":
                PossibleMovements.append((x + 1, y - 1))
        # if this is the pawn's first move, it can move two spaces
        if board.OriginalBoard[y][x] == board.board[y][x] and y > 1:
            PossibleMovements.append((x, y - 2))
    else:
        # if the pawn is black
        if y < 7:
            # check if the space in front of the pawn is empty
            if not board.isPiece(x, y + 1):
                PossibleMovements.append((x, y + 1))
            # check if the space diagonally down and to the left of the pawn is occupied by an opponent
            if x > 0 and board.isPiece(x - 1, y + 1) and board.getPiece(x - 1, y + 1).Color == "White":
                PossibleMovements.append((x - 1, y + 1))
            # check if the space diagonally down and to the right of the pawn is occupied by an opponent
            if x < 7 and board.isPiece(x + 1, y + 1) and board.getPiece(x + 1, y + 1).Color == "White":
                PossibleMovements.append((x + 1, y + 1))
        # if this is the pawn's first move, it can move two spaces
        if board.OriginalBoard[y][x] == board.board[y][x] and y < 6:
            PossibleMovements.append((x, y + 2))

    return PossibleMovements
    
def GetKnightMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a knight at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the knight on the board.
    y (int): The y-coordinate (row) of the knight on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the knight can move to.
    """
    Piece = board.getPiece(x, y)
    PossibleMovements = []
    # these are the 8 possible moves for a knight
    Moves = [(x + 2, y + 1), (x + 2, y - 1), (x - 2, y + 1), (x - 2, y - 1),
             (x + 1, y + 2), (x + 1, y - 2), (x - 1, y + 2), (x - 1, y - 2)]
    for Move in Moves:
        # check if the move is on the board and there is a piece of a different color
        if 0 <= Move[0] <= 7 and 0 <= Move[1] <= 7:
            target_piece = board.getPiece(Move[0], Move[1])
            if target_piece is None or Piece.Color != target_piece.Color:
                PossibleMovements.append(Move)
    return PossibleMovements

def GetBishopMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a bishop at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the bishop on the board.
    y (int): The y-coordinate (row) of the bishop on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the bishop can move to.

    The method first calculates all possible movements for the bishop by moving in
    the four diagonal directions. It then checks each of these movements to see if
    the movement is blocked by a piece of the same color or if the movement goes
    out of bounds. If the movement is blocked by a piece of the opposite color, the
    movement is added to the list.

    """
    # Get the color of the other player
    Piece = board.getPiece(x, y)
    
    # Initialize a list of possible movements
    PossibleMovements = []
    
    # Iterate over the four diagonal directions
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        X, Y = x, y
        # Move in the direction until we reach the edge of the board
        while True:
            X += dx
            Y += dy
            # Check if the position is off the board
            if not (0 <= X <= 7 and 0 <= Y <= 7):
                break
            # Check if there is a piece at the current position
            if board.isPiece(X, Y):
                # If there is a piece of the opposite color, add it to the list
                if board.getPiece(X, Y).Color != Piece.Color:
                    PossibleMovements.append((X, Y))
                break
            # If there is no piece at the current position, add the position to the list
            PossibleMovements.append((X, Y))
    
    return PossibleMovements

def GetRookMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a rook at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the rook on the board.
    y (int): The y-coordinate (row) of the rook on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the rook can move to.
    """

    # Initialize a list of possible movements
    PossibleMovements = []

    # Iterate over the four cardinal directions
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        X, Y = x, y
        # Move in the direction until we reach the edge of the board
        while True:
            X += dx
            Y += dy
            # Check if the position is off the board
            if not (0 <= X <= 7 and 0 <= Y <= 7):
                break
            # Check if there is a piece at the current position
            if board.isPiece(X, Y):
                # If there is a piece of the opposite color, add it to the list
                if board.getPiece(X, Y).Color != board.getPiece(x, y).Color:
                    PossibleMovements.append((X, Y))
                break
            PossibleMovements.append((X, Y))

    return PossibleMovements

def GetQueenMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a queen at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the queen on the board.
    y (int): The y-coordinate (row) of the queen on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the queen can move to. The queen can move in any of the four cardinal directions
    and the four diagonal directions.
    """
    moves = GetRookMovements(x, y, board) + GetBishopMovements(x, y, board)
    print(f"Queen at ({x}, {y}) can move to: {moves}")
    return moves

def GetKingMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a king at a given position on the board.

    Parameters:
    x (int): The x-coordinate (column) of the king on the board.
    y (int): The y-coordinate (row) of the king on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the king can move to.
    """
    # will check around the king
    PossibleMovements = []
    piece = board.getPiece(x, y)
    print(f"Checking moves for {piece.Color} king at ({x}, {y})")
    
    # Normal king moves
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            X = x + i
            Y = y + j
            if 0 <= X <= 7 and 0 <= Y <= 7:
                target_piece = board.getPiece(X, Y)
                if not board.isPiece(X, Y) or (target_piece and target_piece.Color != piece.Color):
                    PossibleMovements.append((X, Y))
                    print(f"King can move to ({X}, {Y})")
    
    # Check for castling moves
    if piece.Color == "White" and not board.moved_pieces['WK']:
        # Kingside castling
        if not board.moved_pieces['WR2'] and not board.isPiece(5, 7) and not board.isPiece(6, 7):
            PossibleMovements.append((6, 7))  # Castling move
        # Queenside castling
        if not board.moved_pieces['WR1'] and not board.isPiece(1, 7) and not board.isPiece(2, 7) and not board.isPiece(3, 7):
            PossibleMovements.append((2, 7))  # Castling move
    elif piece.Color == "Black" and not board.moved_pieces['BK']:
        # Kingside castling
        if not board.moved_pieces['BR2'] and not board.isPiece(5, 0) and not board.isPiece(6, 0):
            PossibleMovements.append((6, 0))  # Castling move
        # Queenside castling
        if not board.moved_pieces['BR1'] and not board.isPiece(1, 0) and not board.isPiece(2, 0) and not board.isPiece(3, 0):
            PossibleMovements.append((2, 0))  # Castling move
    
    print(f"King's possible moves: {PossibleMovements}")
    return PossibleMovements

def GetMovements(X: int, Y: int, board: Board) -> list[tuple[int, int]]:
    """
    Determine all possible movements for a piece at a given position on the board.

    Parameters:
    X (int): The x-coordinate (column) of the piece on the board.
    Y (int): The y-coordinate (row) of the piece on the board.
    board (Board): The board object containing the current state of the game.

    Returns:
    list[tuple[int, int]]: A list of tuples representing the valid coordinates
    the piece can move to.
    """
    piece = board.getPiece(X, Y)

    if not piece:
        return []
    # Pawn movements
    if piece.Type == PieceType.Pawn:
        return GetPawnMovements(X, Y, board)

    # Knight movements
    elif piece.Type == PieceType.Knight:
        return GetKnightMovements(X, Y, board)

    # Bishop movements
    elif piece.Type == PieceType.Bishop:
        #raise NotImplementedError
        return GetBishopMovements(X, Y, board)

    # Rook movements
    elif piece.Type == PieceType.Rook:
        #raise NotImplementedError
        return GetRookMovements(X, Y, board)

    # Queen movements
    elif piece.Type == PieceType.Queen:
        #raise NotImplementedError
        return GetQueenMovements(X, Y, board)

    # King movements
    elif piece.Type == PieceType.King:
        #raise NotImplementedError
        return GetKingMovements(X, Y, board)
      
    
def is_square_attacked(board: Board, pos: tuple[int, int], attacking_color: str) -> bool:
    """Check if a square is under attack by any piece of the given color."""
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == attacking_color:
                moves = GetMovements(x, y, board)
                if pos in moves:
                    return True
    return False

def is_checkmate(board: Board, player_color: str) -> bool:
    """
    Check if a player is in checkmate.
    
    Args:
        board: Current board state
        player_color: Color of the player to check ("White" or "Black")
    
    Returns:
        bool: True if player is in checkmate, False otherwise
    """
    # Find the king
    king_pos = None
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Type == PieceType.King and piece.Color == player_color:
                king_pos = (x, y)
                break
        if king_pos:
            break
            
    if not king_pos:
        return False  # No king found, invalid board state
        
    # If king is not in check, it's not checkmate
    opponent_color = "Black" if player_color == "White" else "White"
    if not is_square_attacked(board, king_pos, opponent_color):
        return False
        
    # Try each piece's moves to see if any can prevent check
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == player_color:
                moves = GetMovements(x, y, board)
                for move in moves:
                    # Try the move on a copy of the board
                    board_copy = Board()
                    board_copy.board = [row[:] for row in board.board]
                    board_copy.moved_pieces = board.moved_pieces.copy()
                    
                    # Make the move
                    piece_name = board.board[y][x]
                    board_copy.board[y][x] = '-'
                    board_copy.board[move[1]][move[0]] = piece_name
                    
                    # Find king's new position if we moved the king
                    check_pos = move if (x, y) == king_pos else king_pos
                    
                    # If this move prevents check, it's not checkmate
                    if not is_square_attacked(board_copy, check_pos, opponent_color):
                        return False
                        
    # If no moves prevent check, it's checkmate
    return True

def IsCheckMate(board: Board, current_player_color: str) -> bool:
    """
    Determines if the opponent is in checkmate after the current player's move.
    
    Args:
        board: Current board state
        current_player_color: Color of the player who just moved
        
    Returns:
        bool: True if opponent is in checkmate, False otherwise
    """
    opponent_color = "Black" if current_player_color == "White" else "White"
    return is_checkmate(board, opponent_color)

def is_move_legal(board: Board, from_pos: tuple[int, int], to_pos: tuple[int, int], moving_color: str) -> bool:
    """Check if a move is legal by verifying it doesn't leave the king in check."""
    # Make a deep copy of the board
    board_copy = board.copy()
    
    # Make the move on the copy
    piece = board_copy.getPiece(*from_pos)
    board_copy.setPiece(to_pos[0], to_pos[1], piece)
    board_copy.removePiece(from_pos[0], from_pos[1])
    
    # Find the king's position after the move
    king_pos = None
    for y in range(8):
        for x in range(8):
            piece = board_copy.getPiece(x, y)
            if piece and piece.Type == PieceType.King and piece.Color == moving_color:
                king_pos = (x, y)
                break
        if king_pos:
            break
            
    if not king_pos:
        return False  # No king found, invalid move
        
    # Check if the king is under attack after the move
    opponent_color = "Black" if moving_color == "White" else "White"
    return not is_square_attacked(board_copy, king_pos, opponent_color)

def can_escape_checkmate(board: Board, player_color: str, depth: int = 1) -> bool:
    """
    Check if a player can escape checkmate by looking ahead at future moves.
    
    Args:
        board: Current board state
        player_color: Color of the player to check
        depth: How many moves ahead to look (default 1)
    
    Returns:
        bool: True if player can escape checkmate, False otherwise
    """
    # Base case - if we've looked ahead enough moves
    if depth <= 0:
        return not is_square_attacked(board, find_king_pos(board, player_color), 
                                   "Black" if player_color == "White" else "White")
    
    # Try each possible move
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == player_color:
                for move in GetMovements(x, y, board):
                    if is_move_legal(board, (x, y), move, player_color):
                        # Make a copy of the board and try the move
                        board_copy = Board()
                        board_copy.board = [row[:] for row in board.board]
                        board_copy.moved_pieces = board.moved_pieces.copy()
                        
                        # Make the move
                        piece_name = board.board[y][x]
                        board_copy.board[y][x] = '-'
                        board_copy.board[move[1]][move[0]] = piece_name
                        
                        # Check opponent's responses
                        opponent_color = "Black" if player_color == "White" else "White"
                        all_responses_lead_to_mate = True
                        
                        for oy in range(8):
                            for ox in range(8):
                                opiece = board_copy.getPiece(ox, oy)
                                if opiece and opiece.Color == opponent_color:
                                    for omove in GetMovements(ox, oy, board_copy):
                                        if is_move_legal(board_copy, (ox, oy), omove, opponent_color):
                                            # Try opponent's move
                                            board_copy2 = Board()
                                            board_copy2.board = [row[:] for row in board_copy.board]
                                            board_copy2.moved_pieces = board_copy.moved_pieces.copy()
                                            
                                            # Make opponent's move
                                            piece_name = board_copy.board[oy][ox]
                                            board_copy2.board[oy][ox] = '-'
                                            board_copy2.board[omove[1]][omove[0]] = piece_name
                                            
                                            # Recursively check if we can escape after opponent's move
                                            if can_escape_checkmate(board_copy2, player_color, depth - 1):
                                                all_responses_lead_to_mate = False
                                                break
                                if not all_responses_lead_to_mate:
                                    break
                            if not all_responses_lead_to_mate:
                                break
                                
                        if all_responses_lead_to_mate:
                            return False
    return True

def find_king_pos(board: Board, color: str) -> tuple[int, int]:
    """Find the position of a player's king."""
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Type == PieceType.King and piece.Color == color:
                return (x, y)
    return None

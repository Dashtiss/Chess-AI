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
      
    
def IsCheckMate(board: Board, current_player_color: str) -> bool:
    """
    Determines if the opponent is in checkmate after the current player's move.

    :param board: Board object representing the current game state.
    :param current_player_color: "White" or "Black" to indicate the current player.
    :return: True if the opponent is in checkmate, False otherwise.
    """
    # We want to check if the opponent is in checkmate
    player_to_check = "Black" if current_player_color == "White" else "White"
    attacking_color = current_player_color  # The current player is the one attacking

    print(f"\nChecking if {player_to_check} is in checkmate")
    print(f"Current board state:")
    board.printBoard()
    
    # Locate the King
    king_position = None
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Type == PieceType.King and piece.Color == player_to_check:
                king_position = (x, y)
                print(f"Found {player_to_check} king at {king_position}")
                break
        if king_position:
            break

    if not king_position:
        print("No king found, invalid board state.")
        return False

    # Check if the King is under attack
    def is_square_attacked(pos, attacking_color):
        print(f"\nChecking if square {pos} is attacked by {attacking_color}")
        # Check all opponent pieces to see if they can attack the king's position
        for y in range(8):
            for x in range(8):
                piece = board.getPiece(x, y)
                if piece and piece.Color == attacking_color:
                    moves = GetMovements(x, y, board)
                    if pos in moves:
                        print(f"Square {pos} is attacked by {piece.Type} at ({x}, {y})")
                        return True
        print(f"Square {pos} is not attacked")
        return False

    if not is_square_attacked(king_position, attacking_color):
        print(f"{player_to_check} king is not in check.")
        return False

    print(f"\nChecking if {player_to_check} can escape check:")
    # Generate all legal moves and simulate them
    for y in range(8):
        for x in range(8):
            piece = board.getPiece(x, y)
            if piece and piece.Color == player_to_check:
                print(f"\nChecking moves for {piece.Type} at ({x}, {y})")
                possible_moves = GetMovements(x, y, board)
                print(f"Possible moves: {possible_moves}")
                for move in possible_moves:
                    print(f"Simulating move from {(x, y)} to {move}")
                    # Simulate the move
                    board_copy = board.copy()
                    board_copy.movePiece(x, y, *move)
                    new_king_position = king_position if piece.Type != PieceType.King else move
                    if not is_square_attacked(new_king_position, attacking_color):
                        print(f"Move from {(x, y)} to {move} resolves the check.")
                        return False

    print(f"{player_to_check} is in checkmate!")
    return True

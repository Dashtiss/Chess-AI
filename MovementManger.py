# manages where a piece can move too

from DataClasses.Board import Board
from DataClasses.Pieces import PieceImage, PieceType

def GetPawnMovements(x: int,y: int, board: Board) -> list[tuple[int, int]]:
    # will check if the pawn is in its starting location by checking the original board and the current one
    # will check the color 
    piece = board.getPiece(x, y)
    """print(board.board[y][x], board.OriginalBoard[y][x])
    for i in board.OriginalBoard:
        print(i)"""
        
    
    if piece.Color == "White":
        PossibleMovements = []
        if board.OriginalBoard[y][x] == board.board[y][x]:
            PossibleMovements.append((x, y - 2))
        
        # will check if a piece is in the way
        if not board.isPiece(x, y - 1):
            PossibleMovements.append((x, y - 1))
            
        if board.isPiece(x - 1, y - 1):
            PossibleMovements.append((x - 1, y - 1))
            
        if board.isPiece(x + 1, y - 1):
            PossibleMovements.append((x + 1, y - 1))
            
        return PossibleMovements
    else:
        PossibleMovements = []
        if board.OriginalBoard[y][x] == board.board[y][x]:
            PossibleMovements.append((x, y + 2))
        
        # will check if a piece is in the way
        if not board.isPiece(x, y + 1):
            PossibleMovements.append((x, y + 1))
            
        if board.isPiece(x - 1, y + 1):
            PossibleMovements.append((x - 1, y + 1))
            
        if board.isPiece(x + 1, y + 1):
            PossibleMovements.append((x + 1, y + 1))
            
        return PossibleMovements
    
def GetKnightMovements(x: int, y: int, board: Board) -> list[tuple[int, int]]:
    PossibleMovements = []
    # will check all moves if there is no piece is in the way and is a other person piece
    Piece = board.getPiece(x, y)
    print(Piece)
    PossibleMovements.append((x + 2, y + 1))
    PossibleMovements.append((x + 2, y - 1))
    PossibleMovements.append((x - 2, y + 1))
    PossibleMovements.append((x - 2, y - 1))
    PossibleMovements.append((x + 1, y + 2))
    PossibleMovements.append((x + 1, y - 2))
    PossibleMovements.append((x - 1, y + 2))
    PossibleMovements.append((x - 1, y - 2))
    
    for Move in PossibleMovements:
        try:
            BoardPiece = board.getPiece(Move[0], Move[1])
            if BoardPiece and BoardPiece.Color == Piece.Color:
                PossibleMovements.remove(Move)
        except IndexError:
            PossibleMovements.remove(Move)
    
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
    
    if piece.Type == PieceType.Pawn:
        return GetPawnMovements(X, Y, board)
    elif piece.Type == PieceType.Knight:
        return GetKnightMovements(X, Y, board)
    elif piece.Type == PieceType.Bishop:
        raise NotImplementedError
        return GetBishopMovements(X, Y, board)
    elif piece.Type == PieceType.Rook:
        raise NotImplementedError
        return GetRookMovements(X, Y, board)
    elif piece.Type == PieceType.Queen:
        raise NotImplementedError
        return GetQueenMovements(X, Y, board)
    elif piece.Type == PieceType.King:
        raise NotImplementedError
        return GetKingMovements(X, Y, board)
        
    
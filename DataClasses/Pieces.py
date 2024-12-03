from .Images import imageResources
from dataclasses import dataclass
import os




@dataclass
class pieceNames:
    WK: str = "White King"
    WQ: str = "White Queen"
    WB: str = "White Bishop"
    WN: str = "White Knight"
    WR: str = "White Rook"
    WP: str = "White Pawn"
    BK: str = "Black King"
    BQ: str = "Black Queen"
    BB: str = "Black Bishop"
    BN: str = "Black Knight"
    BR: str = "Black Rook"
    BP: str = "Black Pawn"
    
@dataclass
class PieceType:
    King: str = "King"
    Queen: str = "Queen"
    Bishop: str = "Bishop"
    Knight: str = "Knight"
    Rook: str = "Rook"
    Pawn: str = "Pawn"
    
@dataclass
class PieceImage:
    Name: str | pieceNames
    Image: str
    Type: str | PieceType
    Color: str
    
pieces: dict[str, PieceImage] = {}
pieceOrder = {
    "WK": PieceType.King, 
    "WQ": PieceType.Queen, 
    "WB": PieceType.Bishop, 
    "WN": PieceType.Knight,
    "WR": PieceType.Rook, 
    "WP": PieceType.Pawn, 
    "BK": PieceType.King, 
    "BQ": PieceType.Queen, 
    "BB": PieceType.Bishop, 
    "BN": PieceType.Knight,
    "BR": PieceType.Rook, 
    "BP": PieceType.Pawn
}

print("Making pieces")
import re

Place = (0, 0)

# Function to extract the number from the filename
def extract_number(filename):
    match = re.search(r'Piece_(\d+)\.png', filename)
    return int(match.group(1)) if match else float('inf')  # Default to infinity if no number is found

# Sort files by the numeric value in their names
files = sorted(os.listdir("res/ChessPieces"), key=extract_number)

for i, file in enumerate(files):
    if file.endswith(".png"):
        if list(pieceOrder.keys())[i].startswith("W"):
            
            piece = PieceImage(
                Name=list(pieceOrder.keys())[i],
                Image=os.path.join("res/ChessPieces", file),
                Type=list(pieceOrder.values())[i],
                Color="White"
            )
            pieces[list(pieceOrder.keys())[i]] = piece
        elif list(pieceOrder.keys())[i].startswith("B"):
            piece = PieceImage(
                Name=list(pieceOrder.keys())[i],
                Image=os.path.join("res/ChessPieces", file),
                Type=list(pieceOrder.values())[i],
                Color="Black"
            )
            pieces[list(pieceOrder.keys())[i]] = piece


print(pieces)
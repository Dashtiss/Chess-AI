from .Images import ImageResources
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Union, Final
import os

class PieceColor(Enum):
    WHITE = "White"
    BLACK = "Black"

class PieceNames(Enum):
    WK = "White King"
    WQ = "White Queen"
    WB = "White Bishop"
    WN = "White Knight"
    WR = "White Rook"
    WP = "White Pawn"
    BK = "Black King"
    BQ = "Black Queen"
    BB = "Black Bishop"
    BN = "Black Knight"
    BR = "Black Rook"
    BP = "Black Pawn"

class PieceType(Enum):
    KING = "King"
    QUEEN = "Queen"
    BISHOP = "Bishop"
    KNIGHT = "Knight"
    ROOK = "Rook"
    PAWN = "Pawn"

@dataclass
class PieceImage:
    Name: str  # The piece identifier (e.g., "WK", "BP")
    Image: str  # Path to the image file
    Type: PieceType  # The type of piece
    Color: PieceColor  # The color of the piece

# Dictionary mapping piece identifiers to their PieceImage objects
pieces: Dict[str, PieceImage] = {}

# Mapping of piece identifiers to their types
pieceOrder: Final[Dict[str, PieceType]] = {
    "WK": PieceType.KING,
    "WQ": PieceType.QUEEN,
    "WB": PieceType.BISHOP,
    "WN": PieceType.KNIGHT,
    "WR": PieceType.ROOK,
    "WP": PieceType.PAWN,
    "BK": PieceType.KING,
    "BQ": PieceType.QUEEN,
    "BB": PieceType.BISHOP,
    "BN": PieceType.KNIGHT,
    "BR": PieceType.ROOK,
    "BP": PieceType.PAWN
}

import re

# Function to extract the number from the filename
def extract_number(filename: str) -> int:
    match = re.search(r'Piece_(\d+)\.png', filename)
    return int(match.group(1)) if match else float('inf')

# Sort files by the numeric value in their names
files = sorted(os.listdir("res/ChessPieces"), key=extract_number)

for i, file in enumerate(files):
    if file.endswith(".png"):
        piece_key = list(pieceOrder.keys())[i]
        piece_color = PieceColor.WHITE if piece_key.startswith("W") else PieceColor.BLACK
        
        piece = PieceImage(
            Name=piece_key,
            Image=os.path.join("res/ChessPieces", file),
            Type=pieceOrder[piece_key],
            Color=piece_color
        )
        pieces[piece_key] = piece
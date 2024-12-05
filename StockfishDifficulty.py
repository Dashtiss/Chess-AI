from enum import Enum, auto

class StockfishDifficulty(Enum):
    """Difficulty levels for the Stockfish chess engine"""
    EASY = auto()    # Lower depth, skill level, and time
    NORMAL = auto()  # Medium depth and skill level
    HARD = auto()    # Maximum depth and skill level

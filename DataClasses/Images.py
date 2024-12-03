from dataclasses import dataclass
import os


@dataclass
class imageResources:
    Icon: str = os.path.join("res", "icon.png")
    Board: str = os.path.join("res", "board.png")
    Pieces: str = os.path.join("res", "piece.png")

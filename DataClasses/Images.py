from enum import Enum
import os


class ImageResources(Enum):
    """Enum containing paths to image resources"""
    ICON = os.path.join("res", "icon.png")
    BOARD = os.path.join("res", "board.png")
    PIECES = os.path.join("res", "piece.png")

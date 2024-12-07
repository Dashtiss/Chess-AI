from enum import Enum
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class ImageResources(Enum):
    """Enum containing paths to image resources"""
    ICON = resource_path(os.path.join("res", "icon.png"))
    BOARD = resource_path(os.path.join("res", "board.png"))
    PIECES = resource_path(os.path.join("res", "piece.png"))

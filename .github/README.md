**Chess AI Project**
======================

**Overview**
------------

This project is a chess artificial intelligence designed to play chess against human opponents. The AI uses a combination of algorithms and techniques to make moves and respond to opponent moves.

**Features**
------------

*   Plays chess against human opponents
*   Uses a combination of algorithms and techniques to make moves
*   Supports various chess variants (e.g. standard, blitz, etc.)
*   Allows for customization of AI difficulty level

**Requirements**
---------------

*   Python 3.12
*   All requerments listed in the `requirements.txt` file

**Installation**
---------------

1.  Clone the repository: `git clone https://github.com/Dashtiss/Chess-AI.git`
2.  (OPTIONAL) Create a virtual environment: `python -m venv venv` 
3.  Install dependencies: `pip install -r requirements.txt`
4.  Run the AI: `python main.py`

**Usage**
-----

1.  Run the AI: `python main.py`
2.  Make a move by specifying the move in standard algebraic notation (e.g. "e4")
3.  The AI will respond with its move

**API Documentation**
--------------------

### `chess_ai.py`

*   `removePiece(x: int, y: int)`: Removes a piece from the board at the specified coordinates.
*   `makeMove(move: str)`: Makes a move on the board.
*   `getResponse()`: Returns the AI's response to the current board state.

**Contributing**
------------

Contributions are welcome! Please submit a pull request with your changes.

**License**
-------

This project is licensed under the MIT License. See `LICENSE` for details.

**Acknowledgments**
---------------

*   The Pygame team for their library.
*   All the open source projects used in this project.
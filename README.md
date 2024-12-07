# Chess AI

A sophisticated Python-based chess game with a modern graphical interface built using Pygame. This project implements a complete chess game with all standard rules and piece movements, featuring a clean and intuitive user interface.

## Features
- Complete chess game implementation with all standard piece movements
- Interactive graphical interface built with Pygame
- Real-time move validation and legal move highlighting
- Visual indicators for possible moves and piece selection
- Checkmate detection and game-ending logic
- Game state tracking and move history
- Undo move functionality (using Backspace)
- Time tracking for both players
- Game history saving with detailed move logs
- Support for special moves:
  - Castling (Kingside and Queenside)
  - Pawn promotion

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Dashtiss/Chess-AI.git
cd chess-ai
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Building Executables

### For macOS
1. Make sure you have Python and pip installed
2. Run the build script:
```bash
chmod +x build.sh  # Make the script executable
./build.sh
```
The macOS app will be created in the `dist` directory as `ChessAI.app`

### For Windows
1. Make sure you have Python and pip installed
2. Run the build script:
```bash
build_windows.bat
```
The Windows executable will be created in the `dist` directory as `ChessAI.exe`

### Running from Source
If you prefer to run from source instead of building:
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Run the game:
```bash
python main.py
```

## Running the Game
```bash
python main.py
```

## How to Play
1. Click on a piece to select it
2. Green circles will appear showing all possible legal moves
3. Click on a highlighted square to move the piece
4. Use Backspace to undo your last move
5. Press ESC to quit the game

## Controls
- Left Mouse Click: Select and move pieces
- Backspace: Undo last move
- ESC: Exit game

## Project Structure
- `main.py`: Main game loop and UI handling
- `MovementManger.py`: Chess move validation and piece movement logic
- `DataClasses/`:
  - `Board.py`: Chess board state management
  - `Pieces.py`: Chess piece definitions and properties
- `GameInfoMenu.py`: Game information display and time tracking
- `settings.py`: Game configuration settings

## Future Features
- AI opponent implementation with multiple difficulty levels
- Opening book integration for AI gameplay
- Custom theme support
- Save/Load game functionality
- Move suggestion system
- Chess puzzle mode
- Rating system for players
- Tournament mode
- Analysis board with move evaluation
- Integration with chess engines (e.g., Stockfish)

## Requirements
- Python 3.7+
- Pygame 2.5.0+
- Additional requirements listed in requirements.txt

## License
MIT License - See LICENSE file for details

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

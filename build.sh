#!/bin/bash

# Create backups directory if it doesn't exist
mkdir -p backups

# Backup previous build if it exists
if [ -d "dist/ChessAI.app" ]; then
    echo "Backing up previous build..."
    backup_name="ChessAI_$(date +%Y%m%d_%H%M%S).app"
    cp -r "dist/ChessAI.app" "backups/$backup_name"
fi

# Clean previous builds
rm -rf build dist *.spec

# Activate virtual environment
source .venv/bin/activate

# Install requirements if needed
python -m pip install -r requirements.txt

# Convert PNG to ICNS for macOS (if needed)
if [ ! -f "res/icon.icns" ]; then
    mkdir -p res/icon.iconset
    sips -z 16 16   res/icon.png --out res/icon.iconset/icon_16x16.png
    sips -z 32 32   res/icon.png --out res/icon.iconset/icon_16x16@2x.png
    sips -z 32 32   res/icon.png --out res/icon.iconset/icon_32x32.png
    sips -z 64 64   res/icon.png --out res/icon.iconset/icon_32x32@2x.png
    sips -z 128 128 res/icon.png --out res/icon.iconset/icon_128x128.png
    sips -z 256 256 res/icon.png --out res/icon.iconset/icon_128x128@2x.png
    sips -z 256 256 res/icon.png --out res/icon.iconset/icon_256x256.png
    sips -z 512 512 res/icon.png --out res/icon.iconset/icon_256x256@2x.png
    sips -z 512 512 res/icon.png --out res/icon.iconset/icon_512x512.png
    sips -z 1024 1024 res/icon.png --out res/icon.iconset/icon_512x512@2x.png
    iconutil -c icns res/icon.iconset
    rm -rf res/icon.iconset
fi

# Create the app bundle using PyInstaller
python -m PyInstaller --clean \
    --name="ChessAI" \
    --windowed \
    --icon="res/icon.icns" \
    --add-data "res:res" \
    --add-data "DataClasses:DataClasses" \
    --add-binary "res/icon.png:res" \
    --add-binary "res/board.png:res" \
    --add-binary "res/pieces.png:res" \
    --add-binary "res/audio/move.mp3:res/audio" \
    --add-binary "res/ChessPieces:res/ChessPieces" \
    --hidden-import chess.engine \
    --hidden-import chess.svg \
    --hidden-import chess.polyglot \
    --hidden-import chess.gaviota \
    --hidden-import chess.syzygy \
    --hidden-import pygame \
    --hidden-import pygame.mixer \
    --hidden-import StockfishDownloader \
    --hidden-import StockfishDifficulty \
    --collect-all chess \
    --collect-all pygame \
    --osx-bundle-identifier "com.chessai.app" \
    main.py

# Save the spec file to backups
if [ -f "ChessAI.spec" ]; then
    cp ChessAI.spec "backups/ChessAI_$(date +%Y%m%d_%H%M%S).spec"
fi

# Deactivate virtual environment
deactivate

echo "Build complete! The app can be found in the dist folder."
echo "Note: Stockfish will be downloaded automatically on first run."
echo "A backup of the previous build (if any) has been saved to the backups folder."

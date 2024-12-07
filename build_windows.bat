@echo off
echo Cleaning up previous builds...
rmdir /s /q dist
rmdir /s /q build
del /f /q *.spec

echo Installing/upgrading required packages...
python -m pip install --upgrade pip
python -m pip install --upgrade pyinstaller

echo Building the Windows executable...
pyinstaller --noconfirm ^
    --name="ChessAI" ^
    --icon="res/icon.png" ^
    --add-data="res/board.png;res" ^
    --add-data="res/pieces.png;res" ^
    --add-data="res/icon.png;res" ^
    --add-data="res/ChessPieces;res/ChessPieces" ^
    --add-data="res/audio;res/audio" ^
    --hidden-import=pygame ^
    --hidden-import=chess ^
    --hidden-import=chess.engine ^
    --noconsole ^
    --onefile ^
    main.py

echo Checking build status...
if exist "dist\ChessAI.exe" (
    echo Build completed successfully!
) else (
    echo Build failed! The executable was not created.
    exit /b 1
)

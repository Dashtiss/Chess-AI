import os
import sys
import requests
import platform
import time
from tqdm import tqdm

def get_stockfish_url():
    """Get the appropriate Stockfish URL based on the platform"""
    system = platform.system().lower()
    if system == "windows":
        return "https://github.com/Dashtiss/Chess-AI/raw/refs/heads/main/res/Stockfish/stockfish-windows.exe"
    elif system == "darwin":  # macOS
        return "https://github.com/Dashtiss/Chess-AI/raw/refs/heads/main/res/Stockfish/stockfish-macos"
    else:  # Linux
        return "https://raw.githubusercontent.com/brandontisserand/ChessAI/main/Stockfish/stockfish-linux"

def get_stockfish_filename():
    """Get the appropriate Stockfish filename based on the platform"""
    system = platform.system().lower()
    if system == "windows":
        return "stockfish-windows.exe"
    elif system == "darwin":  # macOS
        return "stockfish-macos"
    else:  # Linux
        return "stockfish-linux"

def get_stockfish_dir():
    """Get the directory where Stockfish should be stored"""
    if getattr(sys, 'frozen', False):
        # If running as exe (PyInstaller)
        base_dir = os.path.dirname(sys.executable)
    else:
        # If running as script
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Use user's home directory for persistent storage
    home_dir = os.path.expanduser("~")
    stockfish_dir = os.path.join(home_dir, ".chess_ai", "stockfish")
    os.makedirs(stockfish_dir, exist_ok=True)
    return stockfish_dir

def download_stockfish(callback=None):
    """Download Stockfish from GitHub with progress tracking"""
    url = get_stockfish_url()
    filename = get_stockfish_filename()
    stockfish_dir = get_stockfish_dir()
    target_path = os.path.join(stockfish_dir, filename)
    
    # Skip download if file already exists and is valid
    if os.path.exists(target_path):
        # Verify file permissions
        if platform.system() != "Windows":
            current_perms = os.stat(target_path).st_mode & 0o777
            if current_perms != 0o755:
                os.chmod(target_path, 0o755)
        
        if callback:
            # Show quick progress for cached file
            for progress in range(0, 101, 20):
                callback(progress)
                time.sleep(0.05)
        return target_path
    
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download the file with progress tracking
        with open(target_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
                if callback:
                    callback(100)
            else:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)
                    if callback:
                        progress = int((downloaded / total_size) * 100)
                        callback(progress)
        
        # Set executable permissions on Unix-like systems
        if platform.system() != "Windows":
            os.chmod(target_path, 0o755)
        
        return target_path
    
    except Exception as e:
        print(f"Error downloading Stockfish: {e}")
        if os.path.exists(target_path):
            os.remove(target_path)
        return None

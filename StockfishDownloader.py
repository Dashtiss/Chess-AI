import os
import sys
import requests
import platform
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

def download_stockfish(callback=None):
    """Download Stockfish from GitHub with progress tracking"""
    url = get_stockfish_url()
    filename = get_stockfish_filename()
    
    # Get the directory where the executable is running
    if getattr(sys, 'frozen', False):
        # If running as exe (PyInstaller)
        exe_dir = os.path.dirname(sys.executable)
    else:
        # If running as script
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    
    stockfish_dir = os.path.join(exe_dir, "Stockfish")
    os.makedirs(stockfish_dir, exist_ok=True)
    
    target_path = os.path.join(stockfish_dir, filename)
    
    # Skip download if file already exists
    if os.path.exists(target_path):
        if callback:
            callback(100)  # Indicate completion
        return target_path
    
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))
        
        # Download the file with progress tracking
        with open(target_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
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

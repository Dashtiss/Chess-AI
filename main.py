import os
import sys
import pygame
import chess.engine
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Final, Dict
from datetime import datetime
import time

import settings
from DataClasses.Board import Board
from DataClasses.Pieces import PieceType, PieceImage, pieces
from GameInfoMenu import GameInfo
from MovementManger import GetMovements, IsCheckMate
from StockfishDifficulty import StockfishDifficulty
from MainMenu import MainMenu
from StockfishDownloader import download_stockfish
from LoadingScreen import LoadingScreen
import chess

class GameState(Enum):
    PLAYING = auto()
    CHECKMATE = auto()
    CHECKMATE_MENU = auto()

@dataclass
class GameContext:
    selected_coords: Tuple[int, int] = (-1, -1)
    possible_moves: List[Tuple[int, int]] = field(default_factory=list)
    current_turn: str = "White"
    state: GameState = GameState.PLAYING
    can_undo: bool = False
    move_history: List[dict] = field(default_factory=list)
    winner: str = ""

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int] = (70, 92, 111)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        
    def draw(self, screen: pygame.Surface):
        color = tuple(min(c + 20, 255) for c in self.color) if self.hover else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)  
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class ChessBoard:
    BOARD_SIZE: Final[int] = 8
    
    def __init__(self, use_stockfish: bool = False, stockfish_difficulty: StockfishDifficulty = StockfishDifficulty.NORMAL) -> None:
        self.width: Final[int] = settings.ScreenSize[0] + 300
        self.height: Final[int] = settings.ScreenSize[1]
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess")
        
        self.game_info: GameInfo = GameInfo(
            self.screen,
            settings.ScreenSize[0] + 10,
            10,
            290,
            settings.ScreenSize[1] - 20
        )
        
        self.board: Board = Board()
        self.board.generateDefaultBoard()
        self.game: GameContext = GameContext()
        self.start_time: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.move_audio: pygame.mixer.Sound = pygame.mixer.Sound("res/audio/move.mp3")
        
        self.chess_moves: List[str] = []
        self.chess_board = chess.Board()  
        
        self.piece_images: Dict[str, pygame.Surface] = {}
        for piece_name, piece in pieces.items():
            self.piece_images[piece_name] = pygame.image.load(piece.Image).convert_alpha()
        
        self.board_positions: List[List[Tuple[int, int, int, int]]] = [
            [
                (x * settings.SlotSize, y * settings.SlotSize, 
                 settings.SlotSize, settings.SlotSize)
                for y in range(self.BOARD_SIZE)
            ]
            for x in range(self.BOARD_SIZE)
        ]
        
        self.light_square: Final[Tuple[int, int, int]] = (240, 217, 181)
        self.dark_square: Final[Tuple[int, int, int]] = (181, 136, 99)
        self.move_indicator: Final[Tuple[int, int, int]] = (70, 92, 111)
        self.move_indicator_alpha: Final[Tuple[int, int, int, int]] = (70, 92, 111, 40)
        
        self.use_stockfish = use_stockfish
        self.stockfish_difficulty = stockfish_difficulty
        self.stockfish = None
        self.stockfish_depth = 15
        self.stockfish_time = 1.0
        self.stockfish_init_retries = 3
        
        if use_stockfish:
            self._initialize_stockfish()
            
        self.clock: pygame.time.Clock = pygame.time.Clock()

        button_width = 200
        button_height = 50
        button_spacing = 20
        start_x = (self.width - button_width) // 2
        start_y = (self.height - (2 * button_height + button_spacing)) // 2
        
        self.main_menu_button = Button(start_x, start_y, button_width, button_height, "Main Menu")
        self.quit_button = Button(start_x, start_y + button_height + button_spacing, 
                                button_width, button_height, "Quit Game")

    def _initialize_stockfish(self):
        """Initialize Stockfish engine with retries"""
        for attempt in range(self.stockfish_init_retries):
            try:
                # Get the directory where the executable is running
                if getattr(sys, 'frozen', False):
                    # If running as exe (PyInstaller)
                    exe_dir = os.path.dirname(sys.executable)
                else:
                    # If running as script
                    exe_dir = os.path.dirname(os.path.abspath(__file__))
                
                stockfish_dir = os.path.join(exe_dir, "Stockfish")
                stockfish_path = os.path.join(stockfish_dir, self.get_stockfish_filename())
                print(f"Attempting to initialize Stockfish from: {stockfish_path}")
                
                if not os.path.exists(stockfish_path):
                    print(f"Stockfish not found at: {stockfish_path}")
                    self.use_stockfish = False
                    return
                
                # Make sure Stockfish is executable
                if sys.platform != "win32":
                    try:
                        os.chmod(stockfish_path, 0o755)  # Give execute permission
                    except Exception as e:
                        print(f"Error setting Stockfish permissions: {e}")
                        self.use_stockfish = False
                        return
                
                # Initialize Stockfish with a timeout
                try:
                    self.stockfish = chess.engine.SimpleEngine.popen_uci(
                        stockfish_path,
                        timeout=5.0  # 5 second timeout for initialization
                    )
                    print("Stockfish initialized successfully")
                    self._configure_stockfish_difficulty()
                    return
                except chess.engine.EngineTerminatedError:
                    print("Stockfish engine terminated during initialization")
                    self.stockfish = None
                except TimeoutError:
                    print("Stockfish initialization timed out")
                    self.stockfish = None
                except Exception as e:
                    print(f"Error initializing Stockfish: {e}")
                    self.stockfish = None
                
                if attempt < self.stockfish_init_retries - 1:
                    print(f"Retrying Stockfish initialization (attempt {attempt + 2}/{self.stockfish_init_retries})")
                    time.sleep(1)  # Wait before retrying
            except Exception as e:
                print(f"Unexpected error during Stockfish initialization: {e}")
                if attempt == self.stockfish_init_retries - 1:
                    print("Max retries reached. Disabling Stockfish.")
                    self.use_stockfish = False
                    self.stockfish = None

    def get_stockfish_filename(self):
        if sys.platform == "win32":
            return "stockfish-windows.exe"
        elif sys.platform == "darwin":  
            return "stockfish-macos"
        else:  
            return "stockfish-linux"

    def _reinitialize_stockfish_if_needed(self):
        if self.use_stockfish and self.stockfish is None:
            print("Stockfish engine not initialized, attempting to initialize...")
            self._initialize_stockfish()

    def _get_stockfish_move(self):
        """Get the best move from Stockfish based on current difficulty"""
        if not self.use_stockfish:
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Check if Stockfish needs reinitialization
                self._reinitialize_stockfish_if_needed()
                
                if not self.stockfish:
                    return None

                # Sync board and get current position FEN
                self.chess_board = self._sync_chess_board()
                fen = self.chess_board.fen()
                print(f"Current position FEN: {fen}")
                
                # Set position and get move with time limit
                try:
                    # Use time limit as a form of timeout
                    result = self.stockfish.play(
                        self.chess_board,
                        chess.engine.Limit(
                            depth=self.stockfish_depth,
                            time=min(self.stockfish_time, 10.0)  # Cap at 10 seconds
                        )
                    )
                    
                    if result.move:
                        return result.move
                    
                except chess.engine.EngineTerminatedError:
                    print("Stockfish engine terminated unexpectedly")
                    self.stockfish = None
                    if attempt < max_retries - 1:
                        print(f"Retrying move calculation (attempt {attempt + 2}/{max_retries})")
                        self._reinitialize_stockfish_if_needed()
                        continue
                    
                except Exception as e:
                    print(f"Error during Stockfish move calculation: {e}")
                    if "engine process died" in str(e):
                        self.stockfish = None
                        if attempt < max_retries - 1:
                            print(f"Retrying after engine death (attempt {attempt + 2}/{max_retries})")
                            self._reinitialize_stockfish_if_needed()
                            continue
                
            except Exception as e:
                print(f"Unexpected error getting Stockfish move: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying after error (attempt {attempt + 2}/{max_retries})")
                    time.sleep(1)
                    continue
        
        print("Failed to get Stockfish move after all retries")
        return None

    def _configure_stockfish_difficulty(self):
        if not self.stockfish:
            return

        difficulty_settings = {
            StockfishDifficulty.EASY: {
                'Skill Level': 5,     
                'Hash': 32,           
            },
            StockfishDifficulty.NORMAL: {
                'Skill Level': 10,    
                'Hash': 64,
            },
            StockfishDifficulty.HARD: {
                'Skill Level': 20,    
                'Hash': 128,
            }
        }

        settings = difficulty_settings[self.stockfish_difficulty]
        
        try:
            self.stockfish.configure(settings)
            
            self.stockfish_depth = {
                StockfishDifficulty.EASY: 5,
                StockfishDifficulty.NORMAL: 12,
                StockfishDifficulty.HARD: 20
            }[self.stockfish_difficulty]
            
            self.stockfish_time = {
                StockfishDifficulty.EASY: 0.1,
                StockfishDifficulty.NORMAL: 0.5,
                StockfishDifficulty.HARD: 1.0
            }[self.stockfish_difficulty]
            
        except Exception as e:
            print(f"Error configuring Stockfish difficulty: {e}")

    def _get_board_position(self, x: int, y: int) -> Tuple[int, int, int, int]:
        return self.board_positions[x][y]
    
    def _handle_piece_movement(self, x: int, y: int) -> None:
        if (x, y) in self.game.possible_moves:
            self.board.previous_states.append(self.board.copy())
            
            from_x, from_y = self.game.selected_coords
            moving_piece = self.board.getPiece(from_x, from_y)
            captured_piece = self.board.getPiece(x, y)
            
            is_castling = False
            rook_move = None
            if moving_piece.Type == PieceType.KING:
                if abs(x - from_x) == 2 and y == from_y:
                    is_castling = True
                    if x > from_x:  
                        rook_move = (7, y, 5, y)  
                    else:  
                        rook_move = (0, y, 3, y)  

            move_record = {
                'turn_number': len(self.game.move_history) // 2 + 1,
                'player': self.game.current_turn,
                'piece': moving_piece.Type.value,
                'from': f"({from_x}, {from_y})",
                'to': f"({x}, {y})",
                'captured': captured_piece.Type.value if captured_piece else None,
                'castling': is_castling,
                'time': datetime.now().strftime('%H:%M:%S')
            }
            
            self.board.movePiece(from_x, from_y, x, y)
            
            if is_castling and rook_move:
                rx1, ry1, rx2, ry2 = rook_move
                self.board.movePiece(rx1, ry1, rx2, ry2)
            
            self.move_audio.play()
            
            self.game.move_history.append(move_record)
            
            self.chess_board = self._sync_chess_board()
            
            if IsCheckMate(self.board, self.game.current_turn):
                self.game.state = GameState.CHECKMATE_MENU
                self.game.winner = "Black" if self.game.current_turn == "White" else "White"
                self._save_game_history()
                return
            
            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
            self.game_info.update_turn(self.game.current_turn)
            
            self.game.selected_coords = (-1, -1)
            self.game.possible_moves = []
            
            self.game.can_undo = True
            
            if self.game.current_turn == "Black" and self.use_stockfish and self.game.state == GameState.PLAYING:
                stockfish_move = self._get_stockfish_move()
                if stockfish_move:
                    from_coords, to_coords = self._chess_move_to_coords(stockfish_move)
                    
                    from_x, from_y = from_coords
                    to_x, to_y = to_coords
                    moving_piece = self.board.getPiece(from_x, from_y)
                    captured_piece = self.board.getPiece(to_x, to_y)
                    
                    move_record = {
                        'turn_number': len(self.game.move_history) // 2 + 1,
                        'player': "Black",
                        'piece': moving_piece.Type.value,
                        'from': f"({from_x}, {from_y})",
                        'to': f"({to_x}, {to_y})",
                        'captured': captured_piece.Type.value if captured_piece else None,
                        'time': datetime.now().strftime('%H:%M:%S')
                    }
                    
                    self.board.movePiece(from_x, from_y, to_x, to_y)
                    
                    self.move_audio.play()
                    
                    self.game.move_history.append(move_record)
                    
                    self.chess_board = self._sync_chess_board()
                    
                    if IsCheckMate(self.board, "White"):
                        self.game.state = GameState.CHECKMATE_MENU
                        self.game.winner = "Black"
                        self._save_game_history()
                        return
                    
                    self.game.current_turn = "White"
                    self.game_info.update_turn(self.game.current_turn)
                else:
                    self.game.current_turn = "White"
                    self.game_info.update_turn(self.game.current_turn)
        else:
            self._handle_piece_selection(x, y)

    def _handle_piece_selection(self, x: int, y: int) -> None:
        """Handle selecting a piece on the board."""
        piece = self.board.getPiece(x, y)
        
        # If no piece is currently selected, try to select one
        if self.game.selected_coords == (-1, -1):
            if piece and piece.Color.value == self.game.current_turn:
                self.game.selected_coords = (x, y)
                self.game.possible_moves = GetMovements(self.board, x, y)
                print(f"Selected piece at ({x}, {y}), found {len(self.game.possible_moves)} possible moves")
            else:
                print(f"Invalid selection: {'no piece' if not piece else 'wrong color'}")
        # If a piece is already selected, try to move it
        else:
            if (x, y) in self.game.possible_moves:
                self._handle_piece_movement(x, y)
            elif piece and piece.Color.value == self.game.current_turn:
                # Select new piece
                self.game.selected_coords = (x, y)
                self.game.possible_moves = GetMovements(self.board, x, y)
                print(f"Selected new piece at ({x}, {y}), found {len(self.game.possible_moves)} possible moves")
            else:
                # Clear selection
                self.game.selected_coords = (-1, -1)
                self.game.possible_moves = []
                print("Cleared selection")

    def _handle_piece_move(self, x: int, y: int) -> None:
        """Handle moving a piece on the board."""
        if not self.game.selected_coords:
            return

        selected_piece = self.board.getPiece(self.game.selected_coords[0], self.game.selected_coords[1])
        if not selected_piece:
            return

        # Check if this is an en passant capture
        if (selected_piece.Type == PieceType.PAWN and 
            (x, y) == self.board.en_passant_target):
            # Remove the captured pawn
            capture_y = self.game.selected_coords[1]  # Same rank as attacking pawn
            self.board.removePiece(x, capture_y)

        # Move the piece
        if self.board.movePiece(self.game.selected_coords[0], self.game.selected_coords[1], x, y):
            print(f"Moving {selected_piece.Type} from {self.game.selected_coords} to ({x}, {y})")
            
            # Clear selection and possible moves
            self.game.selected_coords = (-1, -1)
            self.game.possible_moves = []
            
            # Switch turns
            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
            
            # If AI mode is enabled and it's AI's turn
            if self.game.current_turn == "Black" and self.use_stockfish and self.game.state == GameState.PLAYING:
                stockfish_move = self._get_stockfish_move()
                if stockfish_move:
                    from_coords, to_coords = self._chess_move_to_coords(stockfish_move)
                    
                    from_x, from_y = from_coords
                    to_x, to_y = to_coords
                    moving_piece = self.board.getPiece(from_x, from_y)
                    captured_piece = self.board.getPiece(to_x, to_y)
                    
                    move_record = {
                        'turn_number': len(self.game.move_history) // 2 + 1,
                        'player': "Black",
                        'piece': moving_piece.Type.value,
                        'from': f"({from_x}, {from_y})",
                        'to': f"({to_x}, {to_y})",
                        'captured': captured_piece.Type.value if captured_piece else None,
                        'time': datetime.now().strftime('%H:%M:%S')
                    }
                    
                    self.board.movePiece(from_x, from_y, to_x, to_y)
                    
                    self.move_audio.play()
                    
                    self.game.move_history.append(move_record)
                    
                    self.chess_board = self._sync_chess_board()
                    
                    if IsCheckMate(self.board, "White"):
                        self.game.state = GameState.CHECKMATE_MENU
                        self.game.winner = "Black"
                        self._save_game_history()
                        return
                    
                    self.game.current_turn = "White"
                    self.game_info.update_turn(self.game.current_turn)
                else:
                    self.game.current_turn = "White"
                    self.game_info.update_turn(self.game.current_turn)

    def _sync_chess_board(self) -> chess.Board:
        board = chess.Board()
        board.clear()  
        
        piece_map = {
            PieceType.PAWN: chess.PAWN,
            PieceType.KNIGHT: chess.KNIGHT,
            PieceType.BISHOP: chess.BISHOP,
            PieceType.ROOK: chess.ROOK,
            PieceType.QUEEN: chess.QUEEN,
            PieceType.KING: chess.KING
        }
        
        print("\nCurrent board state:")  
        self.board.printBoard()  
        
        print("\nSyncing board state:")  
        for y in range(8):
            for x in range(8):
                piece = self.board.getPiece(x, y)
                if piece:
                    square = chess.square(x, 7 - y)  
                    color = chess.WHITE if piece.Color.value == "White" else chess.BLACK
                    piece_type = piece_map[piece.Type]
                    board.set_piece_at(square, chess.Piece(piece_type, color))
                    print(f"Placed {piece.Color.value} {piece.Type.value} at ({x}, {y}) -> square {square}")  
        
        board.turn = chess.BLACK if self.game.current_turn == "Black" else chess.WHITE  
        
        print("\nFinal chess board state:")
        print(board)
        print(f"Final FEN: {board.fen()}")  
        
        return board

    def _chess_move_to_coords(self, move: chess.Move) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        from_square = move.from_square
        to_square = move.to_square
        
        from_x = chess.square_file(from_square)
        from_y = 7 - chess.square_rank(from_square)  
        to_x = chess.square_file(to_square)
        to_y = 7 - chess.square_rank(to_square)  
        
        return ((from_x, from_y), (to_x, to_y))

    def _get_stockfish_notation(self):
        moves_text = ""
        for i in range(0, len(self.chess_moves), 2):
            move_number = i // 2 + 1
            white_move = self.chess_moves[i]
            black_move = self.chess_moves[i + 1] if i + 1 < len(self.chess_moves) else ""
            
            if black_move:
                moves_text += f"{move_number}. {white_move} {black_move} "
            else:
                moves_text += f"{move_number}. {white_move} "
        
        return moves_text.strip()

    def _get_chess_notation(self, piece, from_pos, to_pos, is_capture=False, is_check=False, is_checkmate=False):
        piece_symbols = {
            'WP': '', 'BP': '',  
            'WN': 'N', 'BN': 'N',  
            'WB': 'B', 'BB': 'B',  
            'WR': 'R', 'BR': 'R',  
            'WQ': 'Q', 'BQ': 'Q',  
            'WK': 'K', 'BK': 'K'   
        }
        
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        piece_symbol = piece_symbols[piece.Name]
        
        to_square = f"{chr(to_x + 97)}{8-to_y}"
        
        notation = ""
        if piece_symbol:  
            notation += piece_symbol
        elif is_capture:  
            notation += f"{chr(from_x + 97)}"
            
        if is_capture:
            notation += "x"
            
        notation += to_square
        
        if is_check:
            notation += "+"
        if is_checkmate:
            notation += "#"
            
        return notation

    def _handle_white_move(self, notation):
        pass

    def _handle_promotion(self, x: int, y: int, new_piece: PieceImage) -> None:
        self.board.setPiece(x, y, new_piece)
        self.move_audio.play()
        
        if self.game.move_history:
            self.game.move_history[-1]['promotion'] = new_piece.Name

        self.game.selected_coords = (-1, -1)
        self.game.possible_moves = []

        if IsCheckMate(self.board, self.game.current_turn):
            self.game.state = GameState.CHECKMATE_MENU
            self._save_game_history()
        else:
            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
            self.game_info.update_turn(self.game.current_turn)

    def _handle_events(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
            
        if self.game.state == GameState.CHECKMATE_MENU:
            if self.main_menu_button.handle_event(event):
                return False  
            elif self.quit_button.handle_event(event):
                sys.exit()
            return True
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_x, mouse_y = event.pos
            board_x = mouse_x // settings.SlotSize
            board_y = mouse_y // settings.SlotSize
            
            if 0 <= board_x < 8 and 0 <= board_y < 8:
                if self.game.selected_coords == (-1, -1):
                    self._handle_piece_selection(board_x, board_y)
                else:
                    self._handle_piece_movement(board_x, board_y)
        
        return True

    def draw(self) -> None:
        self.screen.fill((255, 255, 255))
        
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                rect = self._get_board_position(x, y)
                color = self.light_square if (x + y) % 2 == 0 else self.dark_square
                pygame.draw.rect(self.screen, color, rect)

                piece = self.board.getPiece(x, y)
                if piece:
                    piece_img = self.piece_images[piece.Name]
                    self.screen.blit(piece_img, rect)

        if self.game.selected_coords != (-1, -1):
            for move_x, move_y in self.game.possible_moves:
                rect = self._get_board_position(move_x, move_y)
                circle_x = rect[0] + rect[2] // 2
                circle_y = rect[1] + rect[3] // 2
                circle_radius = rect[2] // 4
                
                pygame.draw.circle(
                    self.screen,
                    self.move_indicator,
                    (circle_x, circle_y),
                    circle_radius,
                    2
                )
        
        self.game_info.draw()
        
        if self.game.state == GameState.CHECKMATE_MENU:
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 74)
            text = f"Checkmate! {self.game.winner} wins!"
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(text_surface, text_rect)
            
            self.main_menu_button.draw(self.screen)
            self.quit_button.draw(self.screen)
        
        pygame.display.flip()

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                if not self._handle_events(event):  
                    running = False
            
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
    
    def cleanup(self):
        """Clean up resources before exit"""
        if self.stockfish:
            try:
                self.stockfish.quit(timeout=2.0)  # Add timeout to quit command
            except Exception as e:
                print(f"Error cleaning up Stockfish: {e}")
                try:
                    # Force terminate if quit fails
                    self.stockfish.close()
                except:
                    pass
            self.stockfish = None

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(settings.ScreenSize)
    pygame.display.set_caption("Chess AI")

    while True:
        menu = MainMenu(screen)
        game_settings = menu.run()
        
        if game_settings is None:  
            break
            
        if game_settings.use_stockfish:
            loading_screen = LoadingScreen(settings.ScreenSize)
            
            def progress_callback(progress):
                loading_screen.update(progress)
            
            stockfish_path = download_stockfish(progress_callback)
            
            if not stockfish_path:
                print("Failed to download Stockfish. AI opponent will be disabled.")
                game_settings.use_stockfish = False
        
        game = ChessBoard(
            use_stockfish=game_settings.use_stockfish,
            stockfish_difficulty=game_settings.stockfish_difficulty
        )
        
        running = True
        clock = pygame.time.Clock()
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:  
                        running = False
                if not game._handle_events(event):  
                    running = False
            
            game.draw()
            pygame.display.flip()
            clock.tick(60)
            
            if game.game.state == GameState.CHECKMATE_MENU:
                pygame.time.wait(2000)
                running = False
        
        game.cleanup()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
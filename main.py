import pygame
import settings
from DataClasses.Board import Board
from MovementManger import *
from DataClasses.Pieces import pieces
from typing import List, Tuple, Dict, Optional, Final
from enum import Enum, auto
from dataclasses import dataclass, field
from GameInfoMenu import GameInfo
import os
from datetime import datetime

class GameState(Enum):
    PLAYING = auto()
    CHECKMATE = auto()

@dataclass
class GameContext:
    selected_coords: Tuple[int, int] = (-1, -1)
    possible_moves: List[Tuple[int, int]] = field(default_factory=list)
    current_turn: str = "White"
    state: GameState = GameState.PLAYING
    can_undo: bool = False
    move_history: List[dict] = field(default_factory=list)

class ChessBoard:
    # Class constants
    BOARD_SIZE: Final[int] = 8
    
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        
        # Initialize display with extra width for game info
        self.width: Final[int] = settings.ScreenSize[0] + 300
        self.height: Final[int] = settings.ScreenSize[1]
        self.screen: pygame.Surface = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chess")
        
        # Initialize game info panel
        self.game_info: GameInfo = GameInfo(
            self.screen,
            settings.ScreenSize[0] + 10,
            10,
            280,
            self.height - 20
        )
        
        self.board: Board = Board()
        self.board.generateDefaultBoard()
        self.game: GameContext = GameContext()
        self.start_time: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Initialize the move sound
        self.move_audio: pygame.mixer.Sound = pygame.mixer.Sound("res/audio/move.mp3")
        
        # Load and cache piece images
        self.piece_images: Dict[str, pygame.Surface] = {}
        for piece_name, piece in pieces.items():
            self.piece_images[piece_name] = pygame.image.load(piece.Image).convert_alpha()
        
        # Pre-calculate board positions
        self.board_positions: List[List[Tuple[int, int, int, int]]] = [
            [
                (x * settings.SlotSize, y * settings.SlotSize, 
                 settings.SlotSize, settings.SlotSize)
                for y in range(self.BOARD_SIZE)
            ]
            for x in range(self.BOARD_SIZE)
        ]
        
        # Cache colors
        self.light_square: Final[Tuple[int, int, int]] = (240, 217, 181)
        self.dark_square: Final[Tuple[int, int, int]] = (181, 136, 99)
        self.move_indicator: Final[Tuple[int, int, int]] = (70, 92, 111)
        self.move_indicator_alpha: Final[Tuple[int, int, int, int]] = (70, 92, 111, 40)
        
        # Create clock for consistent frame rate
        self.clock: pygame.time.Clock = pygame.time.Clock()
    
    def _get_board_position(self, x: int, y: int) -> Tuple[int, int, int, int]:
        """Get pre-calculated board position."""
        return self.board_positions[x][y]
    
    def _handle_piece_movement(self, x: int, y: int) -> None:
        """Handle the movement of a piece to the given coordinates."""
        if (x, y) not in self.game.possible_moves:
            return

        from_x, from_y = self.game.selected_coords
        moving_piece = self.board.getPiece(from_x, from_y)
        target_piece = self.board.getPiece(x, y)
        
        if not moving_piece or moving_piece.Color != self.game.current_turn:
            return

        # Save current state before making the move
        self.board.previous_states.append(self.board.copy())
        self.game_info.save_time_state()
        self.game.can_undo = True

        # Record the move in history
        move_record = {
            'turn_number': len(self.game.move_history) // 2 + 1,
            'player': self.game.current_turn,
            'piece': moving_piece.Name,
            'from': f"{chr(from_x + 97)}{8-from_y}",  # Convert to chess notation (e.g., 'e2')
            'to': f"{chr(x + 97)}{8-y}",
            'captured': target_piece.Name if target_piece else None,
            'time': datetime.now().strftime("%H:%M:%S")
        }
        self.game.move_history.append(move_record)

        # Check if we're capturing a king
        if target_piece and target_piece.Name.endswith("King"):
            self.game.state = GameState.CHECKMATE
            # Execute the capture
            self.board.setPiece(x, y, moving_piece)
            self.board.removePiece(from_x, from_y)
            self.board.LastMove = (self.game.selected_coords, (x, y))
            self.move_audio.play()
            self._save_game_history()
            return

        # Execute the move
        self.board.handleCastling(from_x, from_y, x, y)
        self.board.setPiece(x, y, moving_piece)
        self.board.removePiece(from_x, from_y)
        self.board.LastMove = (self.game.selected_coords, (x, y))
        
        # Reset selection and play sound
        self.game.selected_coords = (-1, -1)
        self.game.possible_moves = []
        self.move_audio.play()

        # Check game state and switch turns
        if IsCheckMate(self.board, self.game.current_turn):
            self.game.state = GameState.CHECKMATE
            self._save_game_history()
        else:
            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
            self.game_info.update_turn(self.game.current_turn)

    def _handle_piece_selection(self, x: int, y: int) -> None:
        """Handle the selection of a piece at the given coordinates."""
        piece = self.board.getPiece(x, y)
        if piece and piece.Color == self.game.current_turn:
            self.game.selected_coords = (x, y)
            self.game.possible_moves = GetMovements(self.board, x, y)
        else:
            self.game.selected_coords = (-1, -1)
            self.game.possible_moves = []

    def _save_game_history(self) -> None:
        """Save the game history to a file."""
        # Create games directory if it doesn't exist
        os.makedirs('games', exist_ok=True)
        
        # Generate filename with timestamp
        filename = f"games/chess_game_{self.start_time}.txt"
        
        with open(filename, 'w') as f:
            f.write("Chess Game History\n")
            f.write("=================\n\n")
            f.write(f"Game started at: {self.start_time}\n")
            f.write(f"Game ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Moves:\n")
            f.write("-----\n\n")
            
            for move in self.game.move_history:
                move_str = f"{move['turn_number']}. {move['player']} - "
                move_str += f"{move['piece']} {move['from']} → {move['to']}"
                if move['captured']:
                    move_str += f" (captured {move['captured']})"
                move_str += f" at {move['time']}"
                f.write(move_str + "\n")
            
            f.write("\nGame Result: ")
            if self.game.state == GameState.CHECKMATE:
                winner = "Black" if self.game.current_turn == "White" else "White"
                f.write(f"Checkmate! {winner} wins!")
            else:
                f.write("Game ended without checkmate")

    def draw(self) -> None:
        """Draw the complete game state."""
        self.screen.fill((255, 255, 255))
        
        # Draw the chess board
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                color = self.light_square if (x + y) % 2 == 0 else self.dark_square
                pygame.draw.rect(self.screen, color, self._get_board_position(x, y))
        
        # Draw possible moves as circles
        for x, y in self.game.possible_moves:
            # Calculate circle position (center of tile)
            circle_x = x * settings.SlotSize + settings.SlotSize // 2
            circle_y = y * settings.SlotSize + settings.SlotSize // 2
            circle_radius = settings.SlotSize // 4
            
            # Draw outer circle
            pygame.draw.circle(
                self.screen,
                self.move_indicator,
                (circle_x, circle_y),
                circle_radius,
                width=3
            )
            
            # Draw inner circle with transparency
            s = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                self.move_indicator_alpha,
                (circle_radius, circle_radius),
                circle_radius
            )
            self.screen.blit(s, (circle_x - circle_radius, circle_y - circle_radius))
        
        # Draw pieces
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                piece = self.board.getPiece(x, y)
                if piece:
                    self.screen.blit(
                        self.piece_images[piece.Name],
                        self._get_board_position(x, y)[:2]  # Only need x, y coordinates
                    )
        
        # Draw game info
        self.game_info.update()
        self.game_info.draw()
        
        pygame.display.flip()

    def _handle_events(self) -> bool:
        """Handle game events. Returns False if the game should exit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_game_history()  # Save game when window is closed
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and self.game.state == GameState.PLAYING:
                    if self.game.can_undo and len(self.board.previous_states) > 0:
                        # Restore previous board state
                        self.board = self.board.previous_states.pop()
                        # Restore previous time state
                        if self.game_info.undo_time():
                            # Switch turns back
                            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
                            self.game_info.update_turn(self.game.current_turn)
                            # Reset selection
                            self.game.selected_coords = (-1, -1)
                            self.game.possible_moves = []
                        
                        self.game.can_undo = len(self.board.previous_states) > 0
                
                # Add escape key to quit
                if event.key == pygame.K_ESCAPE:
                    self._save_game_history()  # Save game when ESC is pressed
                    return False
                
            if event.type == pygame.MOUSEBUTTONDOWN and self.game.state == GameState.PLAYING:
                x = int(pygame.mouse.get_pos()[0] // settings.SlotSize)
                y = int(pygame.mouse.get_pos()[1] // settings.SlotSize)
                
                if 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE:  # Validate click is on board
                    if (x, y) in self.game.possible_moves:
                        self._handle_piece_movement(x, y)
                    else:
                        self._handle_piece_selection(x, y)
                    
        return True

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        try:
            while running:
                running = self._handle_events()
                self.draw()
                self.clock.tick(60)  # Limit to 60 FPS
        except KeyboardInterrupt:
            # print("\nGame stopped by user.")
            self._save_game_history()  # Save game on Ctrl+C
        except Exception as e:
            # print(f"\nUnexpected error: {e}")
            self._save_game_history()  # Save game on any error
        finally:
            try:
                self._save_game_history()  # Final attempt to save game
            except:
                # print("Could not save game history")
                pass
            pygame.quit()

def main() -> None:
    try:
        game = ChessBoard()
        game.run()
    except KeyboardInterrupt:
        # print("\nGame stopped during initialization.")
        pass
    except Exception as e:
        # print(f"\nUnexpected error: {e}")
        pass
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
import pygame
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Tuple, Optional, Dict, Callable, Final
from DataClasses.Pieces import PieceType, PieceImage, pieces, PieceColor

class MenuColor(Enum):
    """Colors used in the game info menu"""
    BG = (44, 62, 80)  # Dark blue
    TEXT = (255, 255, 255)  # White
    BORDER = (52, 73, 94)  # Lighter blue
    BUTTON = (41, 128, 185)  # Light blue
    BUTTON_HOVER = (52, 152, 219)  # Lighter blue for hover
    CHECKMATE = (231, 76, 60)  # Red color for checkmate

class GameInfo:
    def __init__(self, screen: pygame.Surface, x: int, y: int, width: int, height: int):
        """Initialize the game info menu"""
        self.screen: pygame.Surface = screen
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        
        # Colors
        self.BG_COLOR: Final[Tuple[int, int, int]] = MenuColor.BG.value
        self.TEXT_COLOR: Final[Tuple[int, int, int]] = MenuColor.TEXT.value
        self.BORDER_COLOR: Final[Tuple[int, int, int]] = MenuColor.BORDER.value
        self.BUTTON_COLOR: Final[Tuple[int, int, int]] = MenuColor.BUTTON.value
        self.BUTTON_HOVER_COLOR: Final[Tuple[int, int, int]] = MenuColor.BUTTON_HOVER.value
        self.CHECKMATE_COLOR: Final[Tuple[int, int, int]] = MenuColor.CHECKMATE.value
        
        # Font
        self.font_large: pygame.font.Font = pygame.font.SysFont('Arial', 28, bold=True)
        self.font_small: pygame.font.Font = pygame.font.SysFont('Arial', 20)
        
        # Initialize game state
        self.current_turn: str = "White"
        self.start_ticks: int = pygame.time.get_ticks()
        self.white_time: float = 0.0
        self.black_time: float = 0.0
        self.last_update: float = pygame.time.get_ticks() / 1000.0
        
        # Game state
        self.is_checkmate: bool = False
        self.winner: Optional[str] = None
        
        # Time history for undo
        self.white_time_history: List[float] = []
        self.black_time_history: List[float] = []

        # Promotion UI
        self.showing_promotion: bool = False
        self.promotion_color: PieceColor = PieceColor.WHITE
        self.promotion_callback: Optional[Callable[[PieceImage], None]] = None
        self.promotion_buttons: List[Dict[str, any]] = []
        self.piece_images: Dict[str, pygame.Surface] = {}
        self._init_promotion_buttons()
        self._load_piece_images()

    def _load_piece_images(self) -> None:
        """Load and cache piece images"""
        for piece_name, piece in pieces.items():
            try:
                image = pygame.image.load(piece.Image).convert_alpha()
                image = pygame.transform.scale(image, (40, 40))  # Scale for the promotion UI
                self.piece_images[piece_name] = image
            except pygame.error as e:
                print(f"Error loading piece image {piece.Image}: {e}")

    def _init_promotion_buttons(self) -> None:
        """Initialize the promotion piece selection buttons"""
        button_width = 50
        button_height = 50
        spacing = 10
        start_x = self.x + (self.width - (4 * button_width + 3 * spacing)) // 2
        y = self.y + self.height // 2 - button_height // 2

        promotion_pieces = ["Q", "R", "B", "N"]
        for i, piece_type in enumerate(promotion_pieces):
            x = start_x + i * (button_width + spacing)
            self.promotion_buttons.append({
                "rect": pygame.Rect(x, y, button_width, button_height),
                "piece_type": piece_type,
                "hovered": False
            })

    def show_promotion_ui(self, color: str, callback: Callable[[PieceImage], None]) -> None:
        """Show the pawn promotion UI"""
        self.showing_promotion = True
        self.promotion_color = PieceColor.WHITE if color == "White" else PieceColor.BLACK
        self.promotion_callback = callback

    def handle_promotion_click(self, pos: Tuple[int, int]) -> bool:
        """Handle clicks in the promotion UI"""
        if not self.showing_promotion:
            return False

        for button in self.promotion_buttons:
            if button["rect"].collidepoint(pos):
                piece_prefix = "W" if self.promotion_color == PieceColor.WHITE else "B"
                piece_key = f"{piece_prefix}{button['piece_type']}"
                if self.promotion_callback and piece_key in pieces:
                    self.promotion_callback(pieces[piece_key])
                    self.showing_promotion = False
                    self.promotion_callback = None
                return True
        return False

    def update_turn(self, turn: str) -> None:
        """Update the current turn"""
        self.current_turn = turn
        current_time = pygame.time.get_ticks() / 1000.0
        time_delta = current_time - self.last_update
        
        # Update the appropriate player's time
        if self.current_turn == "White":
            self.black_time += time_delta
        else:
            self.white_time += time_delta
            
        self.last_update = current_time

    def save_time_state(self) -> None:
        """Save the current time state for undo"""
        self.white_time_history.append(self.white_time)
        self.black_time_history.append(self.black_time)

    def undo_time_state(self) -> None:
        """Restore the previous time state"""
        if self.white_time_history and self.black_time_history:
            self.white_time = self.white_time_history.pop()
            self.black_time = self.black_time_history.pop()

    def set_checkmate(self, winner: str) -> None:
        """Set the checkmate state and winner"""
        self.is_checkmate = True
        self.winner = winner

    def draw(self) -> None:
        """Draw the game info menu"""
        # Draw background
        pygame.draw.rect(self.screen, self.BG_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (self.x, self.y, self.width, self.height), 2)

        # Draw turn indicator
        turn_text = self.font_large.render(f"Turn: {self.current_turn}", True, self.TEXT_COLOR)
        self.screen.blit(turn_text, (self.x + 10, self.y + 10))

        # Draw times
        white_time_text = self.font_small.render(f"White Time: {int(self.white_time)}s", True, self.TEXT_COLOR)
        black_time_text = self.font_small.render(f"Black Time: {int(self.black_time)}s", True, self.TEXT_COLOR)
        self.screen.blit(white_time_text, (self.x + 10, self.y + 50))
        self.screen.blit(black_time_text, (self.x + 10, self.y + 80))

        # Draw checkmate message if game is over
        if self.is_checkmate:
            checkmate_text = self.font_large.render(f"Checkmate! {self.winner} wins!", True, self.CHECKMATE_COLOR)
            text_rect = checkmate_text.get_rect(center=(self.x + self.width//2, self.y + 150))
            self.screen.blit(checkmate_text, text_rect)

        # Draw promotion UI if active
        if self.showing_promotion:
            self._draw_promotion_ui()

    def _draw_promotion_ui(self) -> None:
        """Draw the pawn promotion UI"""
        # Draw semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (self.x, self.y))

        # Draw promotion text
        text = self.font_large.render("Choose promotion piece:", True, self.TEXT_COLOR)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + self.height//2 - 50))
        self.screen.blit(text, text_rect)

        # Draw piece buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.promotion_buttons:
            color = self.BUTTON_HOVER_COLOR if button["rect"].collidepoint(mouse_pos) else self.BUTTON_COLOR
            pygame.draw.rect(self.screen, color, button["rect"])
            pygame.draw.rect(self.screen, self.BORDER_COLOR, button["rect"], 2)
            
            piece_prefix = "W" if self.promotion_color == PieceColor.WHITE else "B"
            piece_key = f"{piece_prefix}{button['piece_type']}"
            if piece_key in self.piece_images:
                image_rect = self.piece_images[piece_key].get_rect(center=button["rect"].center)
                self.screen.blit(self.piece_images[piece_key], image_rect)

    def update(self) -> None:
        """Update game times"""
        if self.is_checkmate:
            return
            
        current_time = pygame.time.get_ticks() / 1000.0
        elapsed = current_time - self.last_update
        self.last_update = current_time
        
        # Update player time
        if self.current_turn == "White":
            self.white_time += elapsed
        else:
            self.black_time += elapsed

    def update_button_hover(self, pos: Tuple[int, int]) -> None:
        """Update button hover states"""
        for button in self.promotion_buttons:
            button["hovered"] = button["rect"].collidepoint(pos)

    def _render_text(self, text: str, font: pygame.font.Font, y_pos: int) -> None:
        """Render text centered at given y position"""
        text_surface = font.render(text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + y_pos))
        self.screen.blit(text_surface, text_rect)
    
    def _draw_game_info(self) -> None:
        """Draw the regular game information"""
        # Render turn
        self._render_text(f"Current Turn: {self.current_turn}", self.font_large, 30)
        
        # Render game time
        game_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        self._render_text(f"Game Time: {minutes:02d}:{seconds:02d}", self.font_small, 70)
        
        # If checkmate, show winner message in time area
        if self.is_checkmate and self.winner:
            # Draw checkmate message in red
            checkmate_surface = self.font_large.render("CHECKMATE!", True, self.CHECKMATE_COLOR)
            checkmate_rect = checkmate_surface.get_rect(center=(self.x + self.width // 2, self.y + 100))
            self.screen.blit(checkmate_surface, checkmate_rect)
            
            # Draw winner message
            winner_surface = self.font_large.render(f"{self.winner} wins!", True, self.TEXT_COLOR)
            winner_rect = winner_surface.get_rect(center=(self.x + self.width // 2, self.y + 130))
            self.screen.blit(winner_surface, winner_rect)
            
            self._render_text("Close window to exit", self.font_small, 160)
        else:
            # Render player times
            w_minutes = int(self.white_time // 60)
            w_seconds = int(self.white_time % 60)
            self._render_text(f"White Time: {w_minutes:02d}:{w_seconds:02d}", self.font_small, 100)
            
            b_minutes = int(self.black_time // 60)
            b_seconds = int(self.black_time % 60)
            self._render_text(f"Black Time: {b_minutes:02d}:{b_seconds:02d}", self.font_small, 130)

import pygame
from datetime import datetime, timedelta
from typing import List, Tuple

class GameInfo:
    def __init__(self, screen, x, y, width, height):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Colors
        self.BG_COLOR = (44, 62, 80)  # Dark blue
        self.TEXT_COLOR = (255, 255, 255)  # White
        self.BORDER_COLOR = (52, 73, 94)  # Lighter blue
        
        # Font
        self.font_large = pygame.font.SysFont('Arial', 24)
        self.font_small = pygame.font.SysFont('Arial', 20)
        
        # Initialize game state
        self.current_turn = "White"
        self.start_ticks = pygame.time.get_ticks()
        self.white_time = 0.0  # Store time in seconds
        self.black_time = 0.0
        self.last_update = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        
        # Time history for undo
        self.white_time_history: List[float] = []
        self.black_time_history: List[float] = []
    
    def _render_text(self, text, font, y_pos):
        """Render text centered at given y position"""
        text_surface = font.render(text, True, self.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + y_pos))
        self.screen.blit(text_surface, text_rect)
    
    def update(self):
        """Update game times"""
        current_time = pygame.time.get_ticks() / 1000.0  # Get current time in seconds
        delta = current_time - self.last_update
        self.last_update = current_time
        
        # Update player time
        if self.current_turn == "White":
            self.white_time += delta
        else:
            self.black_time += delta
    
    def save_time_state(self):
        """Save current time state for undo"""
        self.white_time_history.append(self.white_time)
        self.black_time_history.append(self.black_time)
    
    def undo_time(self) -> bool:
        """Restore previous time state. Returns True if successful."""
        if not self.white_time_history or not self.black_time_history:
            return False
            
        self.white_time = self.white_time_history.pop()
        self.black_time = self.black_time_history.pop()
        return True
    
    def draw(self):
        """Draw the game info panel"""
        # Draw background and border
        pygame.draw.rect(self.screen, self.BG_COLOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, self.BORDER_COLOR, (self.x, self.y, self.width, self.height), 2)
        
        # Render turn
        self._render_text(f"Current Turn: {self.current_turn}", self.font_large, 30)
        
        # Render game time
        game_time = (pygame.time.get_ticks() - self.start_ticks) / 1000.0
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        self._render_text(f"Game Time: {minutes:02d}:{seconds:02d}", self.font_small, 70)
        
        # Render player times
        w_minutes = int(self.white_time // 60)
        w_seconds = int(self.white_time % 60)
        self._render_text(f"White Time: {w_minutes:02d}:{w_seconds:02d}", self.font_small, 100)
        
        b_minutes = int(self.black_time // 60)
        b_seconds = int(self.black_time % 60)
        self._render_text(f"Black Time: {b_minutes:02d}:{b_seconds:02d}", self.font_small, 130)
    
    def update_turn(self, turn: str):
        """Update the current turn"""
        self.current_turn = turn

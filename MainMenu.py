import pygame
import sys
import math
import random
from enum import Enum, auto
from typing import Dict, Optional, Tuple, List, Callable
from dataclasses import dataclass
import settings
from StockfishDifficulty import StockfishDifficulty

class MenuState(Enum):
    MAIN = auto()
    SETTINGS = auto()
    PLAYING = auto()

class ButtonState(Enum):
    NORMAL = auto()
    HOVER = auto()
    SELECTED = auto()

@dataclass
class GameSettings:
    use_stockfish: bool = True
    stockfish_difficulty: StockfishDifficulty = StockfishDifficulty.NORMAL
    screen_size: Tuple[int, int] = (640, 640)
    board_size: Tuple[int, int] = (8, 8)
    slot_size: int = 80

class MenuColors:
    BG = (28, 40, 51)  # Dark blue background
    BG_ACCENT = (41, 58, 74)  # Slightly lighter blue for accents
    BUTTON = (52, 152, 219)  # Light blue
    BUTTON_HOVER = (41, 128, 185)  # Darker blue
    BUTTON_SELECTED = (46, 204, 113)  # Green
    TEXT = (236, 240, 241)  # Almost white
    BORDER = (52, 73, 94)  # Border blue
    TITLE_GRADIENT_START = (52, 152, 219)  # Light blue
    TITLE_GRADIENT_END = (46, 204, 113)  # Green

class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable[[], None]):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.state = ButtonState.NORMAL
        self.font = pygame.font.SysFont('Arial', 24)
        self.hover_scale = 1.0
        self.target_scale = 1.0
        self.original_rect = pygame.Rect(rect)

    def update(self, dt: float) -> None:
        # Smooth hover animation
        scale_diff = self.target_scale - self.hover_scale
        if abs(scale_diff) > 0.001:
            self.hover_scale += scale_diff * dt * 10
        
        # Update rect size and position based on scale
        center = self.original_rect.center
        self.rect.width = int(self.original_rect.width * self.hover_scale)
        self.rect.height = int(self.original_rect.height * self.hover_scale)
        self.rect.center = center

    def draw(self, screen: pygame.Surface) -> None:
        # Get color based on state
        if self.state == ButtonState.SELECTED:
            color = MenuColors.BUTTON_SELECTED
        elif self.state == ButtonState.HOVER:
            color = MenuColors.BUTTON_HOVER
        else:
            color = MenuColors.BUTTON

        # Draw button with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, MenuColors.BORDER, self.rect, 2, border_radius=10)

        # Draw text with shadow
        shadow_offset = 2
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(self.rect.center[0] + shadow_offset, self.rect.center[1] + shadow_offset))
        screen.blit(text_surface, text_rect)
        
        text_surface = self.font.render(self.text, True, MenuColors.TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            was_hovered = self.state == ButtonState.HOVER
            self.state = ButtonState.HOVER if self.rect.collidepoint(event.pos) else ButtonState.NORMAL
            if self.state == ButtonState.HOVER and not was_hovered:
                self.target_scale = 1.05
            elif self.state == ButtonState.NORMAL and was_hovered:
                self.target_scale = 1.0
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()
                return True
        return False

class Toggle(Button):
    def __init__(self, rect: pygame.Rect, text: str, initial_state: bool, callback: Callable[[bool], None]):
        super().__init__(rect, text, lambda: None)
        self.is_on = initial_state
        self.toggle_callback = callback
        self.state = ButtonState.SELECTED if self.is_on else ButtonState.NORMAL

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        
        # Draw toggle indicator
        indicator_rect = pygame.Rect(
            self.rect.right - 40,
            self.rect.centery - 10,
            20,
            20
        )
        color = MenuColors.BUTTON_SELECTED if self.is_on else MenuColors.BUTTON
        pygame.draw.circle(screen, color, indicator_rect.center, 10)
        pygame.draw.circle(screen, MenuColors.BORDER, indicator_rect.center, 10, 2)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_on = not self.is_on
                self.state = ButtonState.SELECTED if self.is_on else ButtonState.NORMAL
                self.toggle_callback(self.is_on)
                return True
        return super().handle_event(event)

class DifficultyButton(Button):
    def __init__(self, rect: pygame.Rect, callback: Callable[[StockfishDifficulty], None]):
        self.current_difficulty = StockfishDifficulty.NORMAL
        super().__init__(rect, self._get_text(), lambda: None)
        self.difficulty_callback = callback
        self.transition_time = 0
        self.transition_duration = 0.3

    def _get_text(self) -> str:
        return f"Difficulty: {self.current_difficulty.name}"

    def update(self, dt: float) -> None:
        super().update(dt)
        if self.transition_time > 0:
            self.transition_time = max(0, self.transition_time - dt)

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        
        # Draw difficulty indicator
        indicator_color = {
            StockfishDifficulty.EASY: (46, 204, 113),  # Green
            StockfishDifficulty.NORMAL: (241, 196, 15),  # Yellow
            StockfishDifficulty.HARD: (231, 76, 60)  # Red
        }[self.current_difficulty]
        
        indicator_rect = pygame.Rect(
            self.rect.right - 40,
            self.rect.centery - 10,
            20,
            20
        )
        pygame.draw.circle(screen, indicator_color, indicator_rect.center, 10)
        pygame.draw.circle(screen, MenuColors.BORDER, indicator_rect.center, 10, 2)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.transition_time <= 0:
                # Cycle through difficulties
                if self.current_difficulty == StockfishDifficulty.EASY:
                    self.current_difficulty = StockfishDifficulty.NORMAL
                elif self.current_difficulty == StockfishDifficulty.NORMAL:
                    self.current_difficulty = StockfishDifficulty.HARD
                else:
                    self.current_difficulty = StockfishDifficulty.EASY
                
                self.text = self._get_text()
                self.difficulty_callback(self.current_difficulty)
                self.transition_time = self.transition_duration
                return True
        return super().handle_event(event)

class MainMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = MenuState.MAIN
        self.game_settings = GameSettings()
        self.buttons: Dict[MenuState, List[Button]] = self._create_buttons()
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 32)
        self.time = 0
        self.background_pieces: List[Dict] = self._create_background_pieces()

    def _create_background_pieces(self) -> List[Dict]:
        pieces = []
        for _ in range(10):  # Create 10 floating pieces
            pieces.append({
                'pos': [
                    random.randint(0, self.screen.get_width()),
                    random.randint(0, self.screen.get_height())
                ],
                'speed': [random.randint(-30, 30), random.randint(-30, 30)],
                'rotation': random.randint(0, 360),
                'rot_speed': random.randint(-90, 90),
                'size': random.randint(30, 60)
            })
        return pieces

    def _create_buttons(self) -> Dict[MenuState, List[Button]]:
        buttons: Dict[MenuState, List[Button]] = {
            MenuState.MAIN: [],
            MenuState.SETTINGS: []
        }

        # Main menu buttons
        center_x = self.screen.get_width() // 2
        button_width = 250
        button_height = 60
        spacing = 30

        # Play button
        y = self.screen.get_height() // 2
        play_button = Button(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            "Play",
            lambda: setattr(self, 'state', MenuState.PLAYING)
        )
        buttons[MenuState.MAIN].append(play_button)

        # Settings button
        y += button_height + spacing
        settings_button = Button(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            "Settings",
            lambda: setattr(self, 'state', MenuState.SETTINGS)
        )
        buttons[MenuState.MAIN].append(settings_button)

        # Exit button
        y += button_height + spacing
        exit_button = Button(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            "Exit",
            lambda: sys.exit()
        )
        buttons[MenuState.MAIN].append(exit_button)

        # Settings menu buttons
        y = self.screen.get_height() // 2 - button_height
        stockfish_toggle = Toggle(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            "Use Stockfish",
            self.game_settings.use_stockfish,
            lambda state: setattr(self.game_settings, 'use_stockfish', state)
        )
        buttons[MenuState.SETTINGS].append(stockfish_toggle)

        # Single difficulty button that cycles through options
        y += button_height + spacing
        difficulty_button = DifficultyButton(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            lambda diff: setattr(self.game_settings, 'stockfish_difficulty', diff)
        )
        buttons[MenuState.SETTINGS].append(difficulty_button)

        # Back button
        y += button_height + spacing
        back_button = Button(
            pygame.Rect(center_x - button_width//2, y, button_width, button_height),
            "Back",
            lambda: setattr(self, 'state', MenuState.MAIN)
        )
        buttons[MenuState.SETTINGS].append(back_button)

        return buttons

    def _draw_background(self) -> None:
        # Draw dark gradient background
        for y in range(self.screen.get_height()):
            progress = y / self.screen.get_height()
            color = [
                MenuColors.BG[i] + (MenuColors.BG_ACCENT[i] - MenuColors.BG[i]) * progress
                for i in range(3)
            ]
            pygame.draw.line(self.screen, color, (0, y), (self.screen.get_width(), y))

        # Draw floating chess pieces
        for piece in self.background_pieces:
            # Draw piece silhouette
            size = piece['size']
            pos = piece['pos']
            alpha = 30  # Semi-transparent
            piece_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(piece_surface, (*MenuColors.TEXT, alpha), (0, 0, size, size))
            
            # Rotate piece
            rotated_surface = pygame.transform.rotate(piece_surface, piece['rotation'])
            self.screen.blit(rotated_surface, (
                pos[0] - rotated_surface.get_width()//2,
                pos[1] - rotated_surface.get_height()//2
            ))

    def _update_background(self, dt: float) -> None:
        screen_rect = self.screen.get_rect()
        for piece in self.background_pieces:
            # Update position
            piece['pos'][0] += piece['speed'][0] * dt
            piece['pos'][1] += piece['speed'][1] * dt
            piece['rotation'] += piece['rot_speed'] * dt

            # Bounce off screen edges
            if piece['pos'][0] < 0 or piece['pos'][0] > screen_rect.width:
                piece['speed'][0] *= -1
            if piece['pos'][1] < 0 or piece['pos'][1] > screen_rect.height:
                piece['speed'][1] *= -1

    def _draw_title(self) -> None:
        # Draw main title with gradient and shadow
        title_text = "Chess AI"
        shadow_offset = 3
        
        # Draw shadow
        shadow_surface = self.title_font.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow_surface.get_rect(center=(self.screen.get_width()//2 + shadow_offset, 100 + shadow_offset))
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw gradient title
        title_surface = self.title_font.render(title_text, True, MenuColors.TEXT)
        title_rect = title_surface.get_rect(center=(self.screen.get_width()//2, 100))
        
        # Create gradient overlay
        gradient = pygame.Surface(title_surface.get_size(), pygame.SRCALPHA)
        for x in range(gradient.get_width()):
            progress = (math.sin(self.time * 2 + x * 0.05) + 1) / 2
            color = [
                MenuColors.TITLE_GRADIENT_START[i] + 
                (MenuColors.TITLE_GRADIENT_END[i] - MenuColors.TITLE_GRADIENT_START[i]) * progress
                for i in range(3)
            ]
            pygame.draw.line(gradient, (*color, 255), (x, 0), (x, gradient.get_height()))
        
        # Apply gradient
        gradient.blit(title_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.screen.blit(gradient, title_rect)

        # Draw subtitle
        if self.state in [MenuState.MAIN, MenuState.SETTINGS]:
            subtitle_text = "Main Menu" if self.state == MenuState.MAIN else "Settings"
            subtitle_surface = self.subtitle_font.render(subtitle_text, True, MenuColors.TEXT)
            subtitle_rect = subtitle_surface.get_rect(center=(self.screen.get_width()//2, 160))
            self.screen.blit(subtitle_surface, subtitle_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.state in self.buttons:
            for button in self.buttons[self.state]:
                if button.handle_event(event):
                    break

    def draw(self) -> None:
        self._draw_background()
        self._draw_title()

        # Draw buttons for current menu state
        if self.state in self.buttons:
            for button in self.buttons[self.state]:
                button.draw(self.screen)

        pygame.display.flip()

    def update(self, dt: float) -> None:
        self.time += dt
        self._update_background(dt)
        if self.state in self.buttons:
            for button in self.buttons[self.state]:
                button.update(dt)

    def run(self) -> Optional[GameSettings]:
        clock = pygame.time.Clock()
        
        while True:
            dt = clock.tick(60) / 1000.0  # Convert to seconds
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                self.handle_event(event)

            if self.state == MenuState.PLAYING:
                return self.game_settings

            self.update(dt)
            self.draw()

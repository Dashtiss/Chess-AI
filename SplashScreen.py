import pygame
import sys
import os

class SplashScreen:
    def __init__(self, screen_size):
        """Initialize the splash screen"""
        pygame.init()
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Chess AI - Loading...")
        
        # Colors
        self.bg_color = (28, 40, 51)  # Dark blue background
        self.text_color = (236, 240, 241)  # Almost white
        
        # Initialize fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 24)
        
        # Create text surfaces
        self.title_text = self.title_font.render("Chess AI", True, self.text_color)
        self.subtitle_text = self.subtitle_font.render("Loading resources...", True, self.text_color)
        
        # Position text
        self.title_rect = self.title_text.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 - 30))
        self.subtitle_rect = self.subtitle_text.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 + 30))
        
        # Animation variables
        self.dots = ""
        self.dot_timer = 0
        self.dot_interval = 500  # milliseconds
        
    def update(self):
        """Update the splash screen animation"""
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Update loading dots animation
        current_time = pygame.time.get_ticks()
        if current_time - self.dot_timer > self.dot_interval:
            self.dots = "." * ((len(self.dots) + 1) % 4)
            self.subtitle_text = self.subtitle_font.render(f"Loading resources{self.dots}", True, self.text_color)
            self.subtitle_rect = self.subtitle_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 30))
            self.dot_timer = current_time
        
        # Draw everything
        self.screen.fill(self.bg_color)
        self.screen.blit(self.title_text, self.title_rect)
        self.screen.blit(self.subtitle_text, self.subtitle_rect)
        pygame.display.flip()

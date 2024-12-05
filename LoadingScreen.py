import pygame
import sys

class LoadingScreen:
    def __init__(self, screen_size):
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption("Chess - Loading...")
        
        # Colors
        self.bg_color = (40, 40, 40)
        self.bar_border_color = (100, 100, 100)
        self.bar_color = (76, 175, 80)
        self.text_color = (255, 255, 255)
        
        # Progress bar dimensions
        self.bar_width = 400
        self.bar_height = 20
        self.bar_x = (screen_size[0] - self.bar_width) // 2
        self.bar_y = screen_size[1] // 2
        
        # Initialize font
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        
        # Loading text
        self.loading_text = self.font.render("Downloading Stockfish...", True, self.text_color)
        self.text_rect = self.loading_text.get_rect(center=(screen_size[0] // 2, self.bar_y - 50))
        
        # Percentage text
        self.percentage = 0
        self.update_percentage_text()
    
    def update_percentage_text(self):
        self.percentage_text = self.font.render(f"{self.percentage}%", True, self.text_color)
        self.percentage_rect = self.percentage_text.get_rect(center=(self.screen.get_width() // 2, self.bar_y + 50))
    
    def update(self, progress):
        """Update the loading screen with new progress"""
        self.percentage = progress
        self.update_percentage_text()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        # Draw background
        self.screen.fill(self.bg_color)
        
        # Draw loading text
        self.screen.blit(self.loading_text, self.text_rect)
        
        # Draw progress bar border
        pygame.draw.rect(self.screen, self.bar_border_color, 
                        (self.bar_x - 2, self.bar_y - 2, 
                         self.bar_width + 4, self.bar_height + 4))
        
        # Draw progress bar
        progress_width = int(self.bar_width * (progress / 100))
        pygame.draw.rect(self.screen, self.bar_color,
                        (self.bar_x, self.bar_y, progress_width, self.bar_height))
        
        # Draw percentage text
        self.screen.blit(self.percentage_text, self.percentage_rect)
        
        # Update display
        pygame.display.flip()

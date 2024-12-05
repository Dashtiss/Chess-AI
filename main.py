import pygame
import settings
from DataClasses.Board import Board
from DataClasses.Pieces import pieces, PieceImage
from MovementManger import GetMovements, IsCheckMate
from typing import List, Tuple, Dict
from enum import Enum, auto
from dataclasses import dataclass

class GameState(Enum):
    PLAYING = auto()
    CHECKMATE = auto()

@dataclass
class GameContext:
    current_turn: str = "White"
    selected_coords: Tuple[int, int] = (-1, -1)
    possible_moves: List[Tuple[int, int]] = None
    state: GameState = GameState.PLAYING
    can_undo: bool = False
    
    def __post_init__(self):
        if self.possible_moves is None:
            self.possible_moves = []

class ChessBoard:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode(settings.ScreenSize)
        pygame.display.set_caption("Chess")
        
        self.board = Board()
        self.board.generateDefaultBoard()
        self.game = GameContext()
        
        # Initialize the move sound
        self.move_audio = pygame.mixer.Sound("res/audio/move.mp3")
        
        # Load piece images
        self.piece_images: Dict[str, pygame.Surface] = {}
        for piece_name, piece in pieces.items():
            self.piece_images[piece_name] = pygame.image.load(piece.Image)

    def _handle_piece_movement(self, x: int, y: int) -> None:
        """Handle the movement of a piece to the given coordinates."""
        if (x, y) not in self.game.possible_moves:
            return

        from_x, from_y = self.game.selected_coords
        piece = self.board.getPiece(from_x, from_y)
        if not piece or piece.Color != self.game.current_turn:
            return

        # Save current state before making the move
        self.board.previous_states.append(self.board.copy())
        self.game.can_undo = True

        # Execute the move
        self.board.handleCastling(from_x, from_y, x, y)
        self.board.setPiece(x, y, piece)
        self.board.removePiece(from_x, from_y)
        self.board.LastMove = (self.game.selected_coords, (x, y))
        
        # Reset selection and play sound
        self.game.selected_coords = (-1, -1)
        self.game.possible_moves = []
        self.move_audio.play()

        # Check game state and switch turns
        if IsCheckMate(self.board, self.game.current_turn):
            self.game.state = GameState.CHECKMATE
        else:
            self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"

    def _handle_piece_selection(self, x: int, y: int) -> None:
        """Handle the selection of a piece at the given coordinates."""
        piece = self.board.getPiece(x, y)
        if piece and piece.Color == self.game.current_turn:
            self.game.selected_coords = (x, y)
            self.game.possible_moves = GetMovements(x, y, self.board)
        else:
            self.game.selected_coords = (-1, -1)
            self.game.possible_moves = []

    def _draw_board(self) -> None:
        """Draw the chess board."""
        for y in range(settings.BoardSize[1]):
            for x in range(settings.BoardSize[0]):
                color = (240, 217, 181) if (x + y) % 2 == 0 else (181, 136, 99)
                pygame.draw.rect(
                    self.screen,
                    color,
                    (x * settings.SlotSize, y * settings.SlotSize, settings.SlotSize, settings.SlotSize),
                )

    def _draw_move_indicators(self) -> None:
        """Draw indicators for possible moves."""
        if self.game.selected_coords != (-1, -1):
            for move in self.game.possible_moves:
                pygame.draw.circle(
                    self.screen,
                    (100, 100, 100),
                    (move[0] * settings.SlotSize + settings.SlotSize // 2,
                     move[1] * settings.SlotSize + settings.SlotSize // 2),
                    10
                )

    def _draw_pieces(self) -> None:
        """Draw all pieces on the board."""
        for y in range(settings.BoardSize[1]):
            for x in range(settings.BoardSize[0]):
                piece = self.board.getPiece(x, y)
                if piece:
                    self.screen.blit(
                        self.piece_images[piece.Name],
                        (x * settings.SlotSize, y * settings.SlotSize),
                    )

    def _handle_events(self) -> bool:
        """Handle game events. Returns False if the game should exit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                if self.game.can_undo and self.game.state == GameState.PLAYING:
                    self.board.undoMove()
                    self.game.current_turn = "Black" if self.game.current_turn == "White" else "White"
                    self.game.selected_coords = (-1, -1)
                    self.game.possible_moves = []
                    self.game.can_undo = len(self.board.previous_states) > 0
                
            if event.type == pygame.MOUSEBUTTONDOWN and self.game.state == GameState.PLAYING:
                x = int(pygame.mouse.get_pos()[0] // settings.SlotSize)
                y = int(pygame.mouse.get_pos()[1] // settings.SlotSize)
                
                if (x, y) in self.game.possible_moves:
                    self._handle_piece_movement(x, y)
                else:
                    self._handle_piece_selection(x, y)
                    
        return True

    def draw(self) -> None:
        """Draw the complete game state."""
        self._draw_board()
        self._draw_move_indicators()
        self._draw_pieces()
        pygame.display.update()
        pygame.display.set_caption(f"Chess - {self.game.current_turn}'s Turn")

    def run(self) -> None:
        """Run the main game loop."""
        running = True
        while running:
            running = self._handle_events()
            self.draw()
            
        pygame.quit()

def main():
    game = ChessBoard()
    game.run()

if __name__ == "__main__":
    main()
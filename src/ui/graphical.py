"""Pygame-based graphical UI."""
from .base import BaseUI
from ..core.config import Config

class GraphicalUI(BaseUI):
    def __init__(self):
        try:
            import pygame
            self.pygame = pygame
        except ImportError:
            raise RuntimeError(
                "Pygame is required for graphical UI. Install with: pip install pygame"
            )
        self.screen = self.pygame.display.set_mode(
            (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
        )
        self.clock = self.pygame.time.Clock()
        self.running = True

    def main_loop(self, game: 'Game') -> None:
        raise NotImplementedError


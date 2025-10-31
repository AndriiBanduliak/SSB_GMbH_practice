import logging
import sys
import pygame

from . import config as cfg
from .game import Game


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    setup_logging()
    pygame.init()
    try:
        screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        Game(screen).run()
    finally:
        pygame.quit()
        sys.exit()



import os
from typing import Optional

import pygame


def asset_path(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # try assets/ subfolder first
    candidate = os.path.join(base_dir, "..", "assets", filename)
    candidate = os.path.abspath(candidate)
    if os.path.exists(candidate):
        return candidate
    # fallback to project root
    fallback = os.path.join(base_dir, "..", filename)
    return os.path.abspath(fallback)


def load_image(filename: str, *, alpha: bool = False) -> pygame.Surface:
    image = pygame.image.load(asset_path(filename))
    return image.convert_alpha() if alpha else image.convert()



from typing import List, Tuple
import random
import pygame

from . import config as cfg


class Obstacle:
    def __init__(self, screen_height: int, ground_height: int, 
                 color: Tuple[int, int, int], player_max_height: int) -> None:
        self.type: str = "cactus"
        self.passed: bool = False
        self.color: Tuple[int, int, int] = color

        self.width: int = random.randint(cfg.CACTUS_MIN_WIDTH, cfg.CACTUS_MAX_WIDTH)
        cactus_max_height = max(cfg.CACTUS_MIN_HEIGHT + 1, int(player_max_height * 0.8))
        self.height: int = random.randint(cfg.CACTUS_MIN_HEIGHT, cactus_max_height)

        self.rect: pygame.Rect = pygame.Rect(
            cfg.SCREEN_WIDTH,
            screen_height - ground_height - self.height,
            self.width,
            self.height,
        )

        self.arms: List[pygame.Rect] = []
        if random.random() > 0.4:
            arm_height = random.randint(self.height // 3, self.height // 2)
            arm_width = self.width // 3
            arm_y = self.rect.y + self.height // 4
            if random.random() > 0.5:
                self.arms.append(pygame.Rect(self.rect.x - arm_width, arm_y, arm_width, arm_height))
            if random.random() > 0.5:
                self.arms.append(pygame.Rect(self.rect.right, arm_y, arm_width, arm_height))

    def update(self, speed: float) -> None:
        self.rect.x -= speed
        arm_count = len(self.arms)
        if arm_count == 1:
            if self.arms[0].centerx < self.rect.centerx:
                self.arms[0].right = self.rect.left
            else:
                self.arms[0].left = self.rect.right
        elif arm_count == 2:
            self.arms[0].right = self.rect.left
            self.arms[1].left = self.rect.right

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
        for arm in self.arms:
            pygame.draw.rect(surface, self.color, arm)



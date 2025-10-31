from typing import Tuple

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
GROUND_HEIGHT = 50

# Colors
WHITE: Tuple[int, int, int] = (255, 255, 255)
GRAY: Tuple[int, int, int, int] = (128, 128, 128, 180)
BLACK: Tuple[int, int, int] = (0, 0, 0)
GREEN: Tuple[int, int, int] = (0, 180, 0)

# Player
PLAYER_START_X = 80
GRAVITY = 0.9
JUMP_STRENGTH = -18
TARGET_PLAYER_HEIGHT = 120

# Obstacles
CACTUS_MIN_WIDTH = 20
CACTUS_MAX_WIDTH = 40
CACTUS_MIN_HEIGHT = 40

# Game dynamics
INITIAL_GAME_SPEED = 6.0
SPEED_INCREMENT = 0.002
OBSTACLE_SPAWN_RATE_INITIAL = 90
OBSTACLE_SPAWN_RATE_MIN = 40



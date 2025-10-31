from typing import List
import logging
import pygame

from . import config as cfg
from .assets import load_image
from .obstacles import Obstacle


logger = logging.getLogger(__name__)


class Game:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        pygame.display.set_caption("Бегущий Амиго")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)

        background_img = load_image("background.png", alpha=False)
        if background_img.get_height() != cfg.SCREEN_HEIGHT:
            ratio = cfg.SCREEN_HEIGHT / background_img.get_height()
            new_w = int(background_img.get_width() * ratio)
            background_img = pygame.transform.scale(background_img, (new_w, cfg.SCREEN_HEIGHT))
        self.background_img = background_img
        self.bg_width = self.background_img.get_width()

        player_img_original = load_image("character.png", alpha=True)
        scale_factor = cfg.TARGET_PLAYER_HEIGHT / player_img_original.get_height()
        target_player_width = int(player_img_original.get_width() * scale_factor)
        self.player_img = pygame.transform.scale(player_img_original, (target_player_width, cfg.TARGET_PLAYER_HEIGHT))
        self.player_rect_base = self.player_img.get_rect()

        self.reset()

    def reset(self) -> None:
        self.player_rect = self.player_rect_base.copy()
        self.player_rect.bottomleft = (cfg.PLAYER_START_X, cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT)
        self.player_velocity_y: float = 0.0
        self.is_jumping: bool = False

        self.obstacles: List[Obstacle] = []
        self.score: int = 0
        self.game_speed: float = cfg.INITIAL_GAME_SPEED
        self.game_active: bool = True
        self.obstacle_timer: int = 0

        self.bg_x1: float = 0
        self.bg_x2: float = float(self.bg_width)

    def _draw_background(self) -> None:
        self.screen.blit(self.background_img, (int(self.bg_x1), 0))
        self.screen.blit(self.background_img, (int(self.bg_x2), 0))

    def _update_background(self) -> None:
        scroll_speed = self.game_speed * 0.5
        self.bg_x1 -= scroll_speed
        self.bg_x2 -= scroll_speed
        if self.bg_x1 <= -self.bg_width:
            self.bg_x1 = self.bg_x2 + self.bg_width
        if self.bg_x2 <= -self.bg_width:
            self.bg_x2 = self.bg_x1 + self.bg_width

    def _draw_ground(self) -> None:
        ground_surface = pygame.Surface((cfg.SCREEN_WIDTH, cfg.GROUND_HEIGHT), pygame.SRCALPHA)
        ground_surface.fill(cfg.GRAY)
        self.screen.blit(ground_surface, (0, cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT))

    def _spawn_obstacle(self) -> None:
        self.obstacle_timer += 1
        current_spawn_rate = max(cfg.OBSTACLE_SPAWN_RATE_MIN, cfg.OBSTACLE_SPAWN_RATE_INITIAL - int(self.game_speed * 3))
        if self.obstacle_timer > current_spawn_rate and len(self.obstacles) < 3:
            self.obstacle_timer = int(current_spawn_rate * 0.3)
            new_obs = Obstacle(cfg.SCREEN_HEIGHT, cfg.GROUND_HEIGHT, cfg.GREEN, self.player_rect.height)
            can_spawn = True
            if self.obstacles:
                last_obstacle = self.obstacles[-1]
                min_distance = max(250, int(cfg.SCREEN_WIDTH / 1.8 - self.game_speed * 15))
                if last_obstacle.height > int(self.player_rect.height * 0.8 * 0.7):
                    min_distance = int(min_distance * 1.2)
                if new_obs.rect.left < last_obstacle.rect.right + min_distance:
                    can_spawn = False
            if can_spawn:
                self.obstacles.append(new_obs)

    def _move_obstacles(self) -> None:
        new_list: List[Obstacle] = []
        for obs in self.obstacles:
            obs.update(self.game_speed)
            if obs.rect.right > 0:
                new_list.append(obs)
                if not obs.passed and obs.rect.right < self.player_rect.left:
                    obs.passed = True
                    self.score += 10
        self.obstacles = new_list

    def _draw_obstacles(self) -> None:
        for obs in self.obstacles:
            obs.draw(self.screen)

    def _check_collisions(self) -> bool:
        for obs in self.obstacles:
            if self.player_rect.colliderect(obs.rect):
                return True
            for arm in obs.arms:
                if self.player_rect.colliderect(arm):
                    return True
        return False

    def _display_score(self) -> None:
        score_surf = self.font.render(f"Счет: {self.score}", True, cfg.BLACK)
        score_rect = score_surf.get_rect(topright=(cfg.SCREEN_WIDTH - 15, 15))
        self.screen.blit(score_surf, score_rect)

    def _display_game_over(self) -> None:
        overlay = pygame.Surface((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 180))
        self.screen.blit(overlay, (0, 0))

        game_over_surf = self.font.render("¡Ay, caramba! Игра окончена!", True, cfg.BLACK)
        restart_surf = self.font.render("Нажми ПРОБЕЛ для реванша", True, cfg.BLACK)
        final_score_surf = self.font.render(f"Финальный счет: {self.score}", True, cfg.BLACK)
        game_over_rect = game_over_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 3))
        final_score_rect = final_score_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT // 2))
        restart_rect = restart_surf.get_rect(center=(cfg.SCREEN_WIDTH // 2, cfg.SCREEN_HEIGHT * 2 // 3))
        self.screen.blit(game_over_surf, game_over_rect)
        self.screen.blit(final_score_surf, final_score_rect)
        self.screen.blit(restart_surf, restart_rect)

    def _handle_keydown(self, key: int) -> bool:
        if self.game_active:
            if key == pygame.K_SPACE and not self.is_jumping:
                self.player_velocity_y = cfg.JUMP_STRENGTH
                self.is_jumping = True
            elif key == pygame.K_ESCAPE:
                return False
        else:
            if key == pygame.K_SPACE:
                self.reset()
            elif key == pygame.K_ESCAPE:
                return False
        return True

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if not self._handle_keydown(event.key):
                        running = False

            if self.game_active:
                self._update_background()

                self.player_velocity_y += cfg.GRAVITY
                self.player_rect.y += int(self.player_velocity_y)
                if self.player_rect.bottom >= cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT:
                    self.player_rect.bottom = cfg.SCREEN_HEIGHT - cfg.GROUND_HEIGHT
                    self.player_velocity_y = 0
                    self.is_jumping = False

                self._spawn_obstacle()
                self._move_obstacles()
                if self._check_collisions():
                    self.game_active = False

                self.game_speed += cfg.SPEED_INCREMENT

                self._draw_background()
                self._draw_ground()
                self._draw_obstacles()
                self.screen.blit(self.player_img, self.player_rect)
                self._display_score()
            else:
                self._draw_background()
                self._display_game_over()

            pygame.display.flip()
            self.clock.tick(60)



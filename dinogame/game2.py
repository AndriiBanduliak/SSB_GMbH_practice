import pygame
import random
import sys
from enum import Enum, auto
from pathlib import Path

# --- Конфигурация игры ---
class Config:
    SCREEN_WIDTH: int = 800
    SCREEN_HEIGHT: int = 450
    GROUND_HEIGHT: int = 50
    FPS: int = 60

    # Физика
    GRAVITY: float = 2000.0        # пикселей/с^2
    JUMP_STRENGTH: float = -800.0  # пикселей/с
    MAX_JUMP_HEIGHT: float = (JUMP_STRENGTH ** 2) / (2 * GRAVITY)

    # Скорость
    INITIAL_SPEED: float = 400.0   # пикселей/с
    SPEED_INCREMENT: float = 5.0   # пикселей/с каждые 100 очков

    # Интервал спавна
    SPAWN_INTERVAL_MIN: float = 0.8
    SPAWN_INTERVAL_MAX: float = 1.5

    # Препятствия
    CACTUS_MIN_WIDTH: int = 20
    CACTUS_MAX_WIDTH: int = 40
    CACTUS_MIN_HEIGHT: int = 40

    # Пути к ресурсам (по умолчанию скриптовая папка)
    ASSETS_DIR: Path = Path(__file__).parent
    PLAYER_IMG: Path = ASSETS_DIR / "character.png"
    BACKGROUND_IMG: Path = ASSETS_DIR / "background.png"

    # Цвета
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128, 180)
    BLACK = (0, 0, 0)
    GREEN = (0, 180, 0)


class State(Enum):
    RUNNING = auto()
    JUMPING = auto()
    DUCKING = auto()


class Player(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, pos: tuple[int, int]):
        super().__init__()
        # Состояние и связанные изображения
        duck_img = pygame.transform.scale(
            image, (image.get_width(), int(image.get_height() * 0.6))
        )
        jump_img = pygame.transform.rotate(image, -15)
        self.images = {
            State.RUNNING: image,
            State.JUMPING: jump_img,
            State.DUCKING: duck_img
        }
        self.state = State.RUNNING
        self.image = self.images[self.state]
        self.rect = self.image.get_rect(midbottom=pos)
        self.vel_y = 0.0

    def update(self, dt: float) -> None:
        # Гравитация
        self.vel_y += Config.GRAVITY * dt
        self.rect.y += int(self.vel_y * dt)
        # Приземление
        ground_y = Config.SCREEN_HEIGHT - Config.GROUND_HEIGHT
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0.0
            if self.state == State.JUMPING:
                self.change_state(State.RUNNING)
        self.image = self.images[self.state]

    def jump(self) -> None:
        if self.state == State.RUNNING:
            self.vel_y = Config.JUMP_STRENGTH
            self.change_state(State.JUMPING)

    def duck(self, enable: bool) -> None:
        if enable and self.state == State.RUNNING:
            self.change_state(State.DUCKING)
        elif not enable and self.state == State.DUCKING:
            self.change_state(State.RUNNING)

    def change_state(self, new_state: State) -> None:
        bottomleft = self.rect.bottomleft
        self.state = new_state
        self.image = self.images[self.state]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = bottomleft


class Cactus(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        width = random.randint(Config.CACTUS_MIN_WIDTH, Config.CACTUS_MAX_WIDTH)
        max_h = max(int(Config.MAX_JUMP_HEIGHT * 0.9), Config.CACTUS_MIN_HEIGHT)
        height = random.randint(Config.CACTUS_MIN_HEIGHT, max_h)

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, Config.GREEN, self.image.get_rect())
        self.rect = self.image.get_rect(
            midbottom=(Config.SCREEN_WIDTH + width // 2, Config.SCREEN_HEIGHT - Config.GROUND_HEIGHT)
        )

    def update(self, dt: float, speed: float) -> None:
        self.rect.x -= int(speed * dt)
        if self.rect.right < 0:
            self.kill()


class Game:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT))
        pygame.display.set_caption("Бегущий Амиго")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 40)

        # Загрузка ресурсов с поддержкой fallback
        self.bg_img = self.load_image(Config.BACKGROUND_IMG, Config.SCREEN_HEIGHT)
        self.bg_width = self.bg_img.get_width()
        player_img = self.load_image(Config.PLAYER_IMG, 120)

        self.player = Player(player_img, (80, Config.SCREEN_HEIGHT - Config.GROUND_HEIGHT))
        self.sprites = pygame.sprite.Group(self.player)
        self.obstacles = pygame.sprite.Group()

        self.ground = pygame.Surface((Config.SCREEN_WIDTH, Config.GROUND_HEIGHT), pygame.SRCALPHA)
        self.ground.fill(Config.GRAY)

        self.bg_x1, self.bg_x2 = 0, self.bg_width
        self.speed = Config.INITIAL_SPEED
        self.spawn_timer = 0.0
        self.next_spawn = random.uniform(Config.SPAWN_INTERVAL_MIN, Config.SPAWN_INTERVAL_MAX)
        self.score = 0
        self.active = True

    def load_image(self, path: Path, scale_h: int | None = None) -> pygame.Surface:
        file = Path(path)
        # Поиск: сначала указанный путь, затем в папке скрипта
        candidates = [file, Path(__file__).parent / file.name]
        for p in candidates:
            if p.exists():
                try:
                    img = pygame.image.load(str(p)).convert_alpha()
                except pygame.error as e:
                    print(f"Ошибка загрузки {p}: {e}")
                    pygame.quit()
                    sys.exit()
                else:
                    if scale_h and img.get_height() != scale_h:
                        ratio = scale_h / img.get_height()
                        new_w = int(img.get_width() * ratio)
                        img = pygame.transform.scale(img, (new_w, scale_h))
                    return img
        print(f"Файл изображения не найден: {file} или {candidates[1]}")
        pygame.quit()
        sys.exit()

    def run(self) -> None:
        while True:
            dt = self.clock.tick(Config.FPS) / 1000.0
            self.handle_events()
            self.update(dt)
            self.draw()
            pygame.display.flip()

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and self.active:
                    self.player.jump()
                elif event.key == pygame.K_SPACE and not self.active:
                    self.reset()

        keys = pygame.key.get_pressed()
        self.player.duck(keys[pygame.K_DOWN])

    def update(self, dt: float) -> None:
        if not self.active:
            return
        shift = int(self.speed * dt * 0.5)
        self.bg_x1 = (self.bg_x1 - shift) % self.bg_width
        self.bg_x2 = (self.bg_x1 + self.bg_width) % (self.bg_width * 2)

        # Спавн
        self.spawn_timer += dt
        if self.spawn_timer >= self.next_spawn:
            cactus = Cactus()
            self.obstacles.add(cactus)
            self.sprites.add(cactus)
            self.spawn_timer = 0.0
            self.next_spawn = random.uniform(Config.SPAWN_INTERVAL_MIN, Config.SPAWN_INTERVAL_MAX)

        # Обновления спрайтов
        self.player.update(dt)
        for obs in list(self.obstacles):
            obs.update(dt, self.speed)
            if obs.rect.right < self.player.rect.left:
                self.score += 10
                if self.score % 100 == 0:
                    self.speed += Config.SPEED_INCREMENT

        # Проверка коллизий
        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            self.active = False

    def draw(self) -> None:
        if self.active:
            # Фон
            self.screen.blit(self.bg_img, (self.bg_x1 - self.bg_width, 0))
            self.screen.blit(self.bg_img, (self.bg_x1, 0))
            # Земля и спрайты
            self.screen.blit(self.ground, (0, Config.SCREEN_HEIGHT - Config.GROUND_HEIGHT))
            self.sprites.draw(self.screen)
            # Счет
            score_surf = self.font.render(f"Счет: {self.score}", True, Config.BLACK)
            self.screen.blit(score_surf, (Config.SCREEN_WIDTH - score_surf.get_width() - 15, 15))
        else:
            overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 180))
            self.screen.blit(overlay, (0, 0))
            game_over = self.font.render("Игра закончена! Нажми ПРОБЕЛ", True, Config.BLACK)
            your_score = self.font.render(f"Твой счёт: {self.score}", True, Config.BLACK)
            self.screen.blit(game_over, game_over.get_rect(center=(Config.SCREEN_WIDTH/2, Config.SCREEN_HEIGHT/2 - 20)))
            self.screen.blit(your_score, your_score.get_rect(center=(Config.SCREEN_WIDTH/2, Config.SCREEN_HEIGHT/2 + 20)))

    def reset(self) -> None:
        for sprite in list(self.obstacles):
            sprite.kill()
        self.score = 0
        self.speed = Config.INITIAL_SPEED
        self.spawn_timer = 0.0
        self.next_spawn = random.uniform(Config.SPAWN_INTERVAL_MIN, Config.SPAWN_INTERVAL_MAX)
        self.active = True


if __name__ == '__main__':
    Game().run()

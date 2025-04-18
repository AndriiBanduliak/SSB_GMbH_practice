import pygame
import random
import sys

# --- Настройки и константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
GROUND_HEIGHT = 50
FPS = 60

# Физика
GRAVITY = 2000        # пикселей/с^2
JUMP_STRENGTH = -800  # пикселей/с
# Расчет максимальной высоты прыжка: h = v^2 / (2*g)
MAX_JUMP_HEIGHT = (abs(JUMP_STRENGTH) ** 2) / (2 * GRAVITY)

# Цвета
WHITE = (255, 255, 255)
GRAY = (128, 128, 128, 180)
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)

# Параметры препятствий
CACTUS_MIN_WIDTH = 20
CACTUS_MAX_WIDTH = 40
CACTUS_MIN_HEIGHT = 40

# Скорость игры
INITIAL_SPEED = 400   # пикселей/с
SPEED_INCREMENT = 5   # пикселей/с каждые 100 очков

# Интервал спавна (секунды)
SPAWN_INTERVAL_MIN = 0.8
SPAWN_INTERVAL_MAX = 1.5

# Пути к картинкам
PLAYER_IMG_PATH = "character.png"
BACKGROUND_IMG_PATH = "background.png"

class Player(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midbottom=pos)
        self.vel_y = 0
        self.is_jumping = False

    def update(self, dt):
        self.vel_y += GRAVITY * dt
        self.rect.y += self.vel_y * dt
        ground_y = SCREEN_HEIGHT - GROUND_HEIGHT
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vel_y = 0
            self.is_jumping = False

    def jump(self):
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True

class Cactus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
        # Ограничиваем высоту, чтобы всегда быть преодолимой (<= 90% от max jump)
        max_h = int(MAX_JUMP_HEIGHT * 0.9)
        max_h = max(max_h, CACTUS_MIN_HEIGHT)
        self.height = random.randint(CACTUS_MIN_HEIGHT, max_h)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, self.image.get_rect())
        self.rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH + self.width // 2, SCREEN_HEIGHT - GROUND_HEIGHT)
        )
        self.passed = False

    def update(self, dt, speed):
        self.rect.x -= speed * dt


def load_image(path, scale_height=None):
    try:
        img = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Ошибка загрузки {path}: {e}")
        pygame.quit()
        sys.exit()
    if scale_height and img.get_height() != scale_height:
        ratio = scale_height / img.get_height()
        new_w = int(img.get_width() * ratio)
        img = pygame.transform.scale(img, (new_w, scale_height))
    return img


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Бегущий Амиго")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 40)

    bg_img = load_image(BACKGROUND_IMG_PATH, SCREEN_HEIGHT)
    bg_width = bg_img.get_width()
    player_img = load_image(PLAYER_IMG_PATH, 120)

    ground_surf = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT), pygame.SRCALPHA)
    ground_surf.fill(GRAY)

    player = Player(player_img, pos=(80, SCREEN_HEIGHT - GROUND_HEIGHT))
    all_sprites = pygame.sprite.Group(player)
    obstacles = pygame.sprite.Group()

    bg_x1, bg_x2 = 0, bg_width
    game_speed = INITIAL_SPEED
    spawn_timer = 0
    next_spawn = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
    score = 0
    running = True
    game_active = True

    while running:
        dt = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        player.jump()
                    else:
                        # Удаляем все препятствия из групп
                        for cactus in list(obstacles):
                            cactus.kill()
                        spawn_timer = 0
                        next_spawn = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)
                        score = 0
                        game_speed = INITIAL_SPEED
                        game_active = True
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if game_active:
            # Обновление фона (параллакс)
            move = game_speed * dt * 0.5
            bg_x1 -= move
            bg_x2 -= move
            if bg_x1 <= -bg_width:
                bg_x1 = bg_x2 + bg_width
            if bg_x2 <= -bg_width:
                bg_x2 = bg_x1 + bg_width

            # Спавн кактусов
            spawn_timer += dt
            if spawn_timer >= next_spawn:
                cactus = Cactus()
                obstacles.add(cactus)
                all_sprites.add(cactus)
                spawn_timer = 0
                next_spawn = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

            # Обновление и колизии
            player.update(dt)
            for cactus in obstacles:
                cactus.update(dt, game_speed)
                if cactus.rect.right < 0:
                    cactus.kill()
                if not cactus.passed and cactus.rect.right < player.rect.left:
                    cactus.passed = True
                    score += 10
                    if score % 100 == 0:
                        game_speed += SPEED_INCREMENT

            if pygame.sprite.spritecollideany(player, obstacles):
                game_active = False

            # Отрисовка сцены
            screen.blit(bg_img, (int(bg_x1), 0))
            screen.blit(bg_img, (int(bg_x2), 0))
            screen.blit(ground_surf, (0, SCREEN_HEIGHT - GROUND_HEIGHT))
            all_sprites.draw(screen)

            # Отображение счета
            score_surf = font.render(f"Счет: {score}", True, BLACK)
            screen.blit(score_surf, (SCREEN_WIDTH - score_surf.get_width() - 15, 15))
        else:
            # Экран Game Over
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255,255,255,180))
            screen.blit(overlay, (0,0))
            go = font.render("Игра окончена! Нажми ПРОБЕЛ", True, BLACK)
            sc = font.render(f"Твой счет: {score}", True, BLACK)
            screen.blit(go, go.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20)))
            screen.blit(sc, sc.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
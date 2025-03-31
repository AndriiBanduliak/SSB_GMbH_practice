import pygame
import random
import sys
import os

# --- Инициализация Pygame ---
pygame.init()

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
GROUND_HEIGHT = 50

WHITE = (255, 255, 255)
GRAY = (128, 128, 128, 180) # Полупрозрачная земля
BLACK = (0, 0, 0)
GREEN = (0, 180, 0)

# --- Параметры Игрока ---
PLAYER_START_X = 80
GRAVITY = 0.9
JUMP_STRENGTH = -18 # Возможно, придется подстроить под новый размер

# --- Настройка экрана ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Бегущий Амиго с Фону")

# --- Часы и Шрифт ---
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

# --- Загрузка Ассетов ---
try:
    # Загружаем спрайт персонажа
    player_img_original = pygame.image.load("character.png").convert_alpha() # Загружаем в новую переменную
    # Загружаем фон
    background_img = pygame.image.load("background.png").convert()

except pygame.error as e:
    print(f"Ошибка загрузки изображения: {e}")
    print("Убедитесь, что файлы 'character.png' и 'background.png' находятся в той же папке.")
    pygame.quit()
    sys.exit()

# Масштабирование фона под высоту экрана
if background_img.get_height() != SCREEN_HEIGHT:
    print("Масштабирование фона под высоту экрана...")
    bg_ratio = SCREEN_HEIGHT / background_img.get_height()
    new_bg_width = int(background_img.get_width() * bg_ratio)
    background_img = pygame.transform.scale(background_img, (new_bg_width, SCREEN_HEIGHT))
    print(f"Новые размеры фона: {background_img.get_width()}x{SCREEN_HEIGHT}")

BG_WIDTH = background_img.get_width()

# --- Масштабирование спрайта персонажа ---
target_player_height = 120 # <<<--- ЗАДАЙ ЗДЕСЬ ЖЕЛАЕМУЮ ВЫСОТУ ПЕРСОНАЖА
print(f"Оригинальная высота персонажа: {player_img_original.get_height()}")
print(f"Масштабирование персонажа до высоты: {target_player_height}")

scale_factor = target_player_height / player_img_original.get_height()
target_player_width = int(player_img_original.get_width() * scale_factor)

player_img = pygame.transform.scale(player_img_original, (target_player_width, target_player_height))
print(f"Новые размеры персонажа: {player_img.get_width()}x{player_img.get_height()}")

# Получаем Rect из УЖЕ МАСШТАБИРОВАННОГО изображения
PLAYER_RECT_BASE = player_img.get_rect()


# --- Параметры Препятствий (Кактусы) ---
CACTUS_MIN_WIDTH = 20
CACTUS_MAX_WIDTH = 40
CACTUS_MIN_HEIGHT = 40
# Макс. высота кактуса теперь зависит от новой высоты игрока
CACTUS_MAX_HEIGHT = int(target_player_height * 0.8) # Кактус не выше 80% игрока

# --- Параметры Игры ---
INITIAL_GAME_SPEED = 6
SPEED_INCREMENT = 0.002
OBSTACLE_SPAWN_RATE_INITIAL = 90
OBSTACLE_SPAWN_RATE_MIN = 40

# --- Класс для препятствий (Кактусы) ---
class Obstacle:
    def __init__(self):
        self.type = 'cactus'
        self.passed = False

        self.width = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
        # Высоту кактуса делаем зависимой от максимальной
        self.height = random.randint(CACTUS_MIN_HEIGHT, max(CACTUS_MIN_HEIGHT + 1, CACTUS_MAX_HEIGHT)) # +1 на случай если мин=макс

        # Убедимся что кактус не слишком высокий (на всякий случай)
        self.height = min(self.height, PLAYER_RECT_BASE.height - 10)


        self.rect = pygame.Rect(SCREEN_WIDTH,
                                 SCREEN_HEIGHT - GROUND_HEIGHT - self.height,
                                 self.width, self.height)
        self.color = GREEN
        self.arms = []
        if random.random() > 0.4:
            arm_height = random.randint(self.height // 3, self.height // 2)
            arm_width = self.width // 3
            arm_y = self.rect.y + self.height // 4
            if random.random() > 0.5:
                self.arms.append(pygame.Rect(self.rect.x - arm_width, arm_y, arm_width, arm_height))
            if random.random() > 0.5:
                 self.arms.append(pygame.Rect(self.rect.right, arm_y, arm_width, arm_height))

    def update(self, speed):
        self.rect.x -= speed
        # Обновляем положение рук кактуса (если они есть)
        arm_count = len(self.arms)
        if arm_count > 0:
            # Определяем, какая рука левая, какая правая (по X координате)
            if arm_count == 1: # Если только одна рука
                 if self.arms[0].centerx < self.rect.centerx: # Левая рука
                     self.arms[0].right = self.rect.left
                 else: # Правая рука
                     self.arms[0].left = self.rect.right
            elif arm_count == 2: # Если две руки
                 # Предполагаем, что первая в списке - левая, вторая - правая
                 # (Если они добавлялись в таком порядке)
                 self.arms[0].right = self.rect.left
                 self.arms[1].left = self.rect.right


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        for arm in self.arms:
            pygame.draw.rect(surface, self.color, arm)

# --- Игровые переменные ---
def reset_game():
    global player_y, player_velocity_y, is_jumping, player_rect
    global obstacles, score, game_speed, game_active, obstacle_timer
    global bg_x1, bg_x2

    # Y координата теперь считается от низа земли и новой высоты спрайта
    player_rect = PLAYER_RECT_BASE.copy()
    player_rect.bottomleft = (PLAYER_START_X, SCREEN_HEIGHT - GROUND_HEIGHT)
    player_y = player_rect.top # Обновляем player_y на всякий случай

    player_velocity_y = 0
    is_jumping = False

    obstacles = []
    score = 0
    game_speed = INITIAL_GAME_SPEED
    game_active = True
    obstacle_timer = 0

    bg_x1 = 0
    bg_x2 = BG_WIDTH

reset_game()

# --- Функции ---

def draw_background():
    screen.blit(background_img, (int(bg_x1), 0))
    screen.blit(background_img, (int(bg_x2), 0))

def update_background(current_speed):
    global bg_x1, bg_x2
    scroll_speed = current_speed * 0.5
    bg_x1 -= scroll_speed
    bg_x2 -= scroll_speed
    if bg_x1 <= -BG_WIDTH: bg_x1 = bg_x2 + BG_WIDTH
    if bg_x2 <= -BG_WIDTH: bg_x2 = bg_x1 + BG_WIDTH

def draw_ground():
    ground_surface = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT), pygame.SRCALPHA)
    ground_surface.fill(GRAY)
    screen.blit(ground_surface, (0, SCREEN_HEIGHT - GROUND_HEIGHT))

def draw_obstacles():
    for obs in obstacles:
        obs.draw(screen)

def move_obstacles():
    global obstacles, score
    new_obstacles = []
    for obs in obstacles:
        obs.update(game_speed)
        if obs.rect.right > 0:
            new_obstacles.append(obs)
            if not obs.passed and obs.rect.right < player_rect.left:
                obs.passed = True
                score += 10
    obstacles = new_obstacles

def spawn_obstacle():
    global obstacle_timer
    obstacle_timer += 1
    current_spawn_rate = max(OBSTACLE_SPAWN_RATE_MIN, OBSTACLE_SPAWN_RATE_INITIAL - int(game_speed * 3))
    if obstacle_timer > current_spawn_rate and len(obstacles) < 3:
        obstacle_timer = random.randint(0, int(current_spawn_rate * 0.3))
        new_obs = Obstacle()
        can_spawn = True
        if obstacles:
            last_obstacle = obstacles[-1]
            min_distance = max(250, int(SCREEN_WIDTH / 1.8 - game_speed * 15)) # Подстроим дистанцию
            # Увеличим мин дист, если последний кактус был высоким
            if last_obstacle.height > CACTUS_MAX_HEIGHT * 0.7:
                 min_distance *= 1.2

            if new_obs.rect.left < last_obstacle.rect.right + min_distance:
                can_spawn = False
        if can_spawn:
             obstacles.append(new_obs)

def check_collisions():
    for obs in obstacles:
        # Проверка столкновения с основным телом кактуса
        if player_rect.colliderect(obs.rect):
            return True
        # Проверка столкновения с руками кактуса
        if hasattr(obs, 'arms'):
             for arm in obs.arms:
                 # Уменьшим хитбокс рук для лояльности (опционально)
                 # arm_hitbox = arm.inflate(-arm.width * 0.3, -arm.height * 0.3)
                 # if player_rect.colliderect(arm_hitbox):
                 if player_rect.colliderect(arm):
                      return True
    return False

def display_score():
    score_surf = font.render(f"Счет: {score}", True, BLACK)
    score_rect = score_surf.get_rect(topright = (SCREEN_WIDTH - 15, 15))
    screen.blit(score_surf, score_rect)

def display_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, 180))
    screen.blit(overlay, (0,0))

    game_over_surf = font.render("¡Ay, caramba! Игра окончена!", True, BLACK)
    restart_surf = font.render("Нажми ПРОБЕЛ для реванша", True, BLACK)
    final_score_surf = font.render(f"Финальный счет: {score}", True, BLACK)
    game_over_rect = game_over_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    final_score_rect = final_score_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_surf.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
    screen.blit(game_over_surf, game_over_rect)
    screen.blit(final_score_surf, final_score_rect)
    screen.blit(restart_surf, restart_rect)

# --- Основной игровой цикл ---
running = True
while running:
    # --- Обработка событий ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if game_active:
                if event.key == pygame.K_SPACE and not is_jumping:
                    player_velocity_y = JUMP_STRENGTH
                    is_jumping = True
                elif event.key == pygame.K_ESCAPE: running = False
            else: # Game Over
                if event.key == pygame.K_SPACE: reset_game()
                elif event.key == pygame.K_ESCAPE: running = False

    # --- Игровая логика (если игра активна) ---
    if game_active:
        # --- Обновления ---
        update_background(game_speed)
        # Игрок
        player_velocity_y += GRAVITY
        player_rect.y += int(player_velocity_y)
        if player_rect.bottom >= SCREEN_HEIGHT - GROUND_HEIGHT:
            player_rect.bottom = SCREEN_HEIGHT - GROUND_HEIGHT
            player_velocity_y = 0
            is_jumping = False
        # Препятствия
        spawn_obstacle()
        move_obstacles()
        # Столкновения
        if check_collisions(): game_active = False
        # Скорость
        game_speed += SPEED_INCREMENT

        # --- Отрисовка ---
        draw_background()
        draw_ground()
        draw_obstacles()
        screen.blit(player_img, player_rect) # Игрок
        display_score()

    else: # Game Over
        draw_background()
        display_game_over()

    # --- Обновление экрана ---
    pygame.display.flip()
    clock.tick(60)

# --- Завершение ---
pygame.quit()
sys.exit()
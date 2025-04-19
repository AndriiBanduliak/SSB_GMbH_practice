import pygame
import random
import sys
import os # Добавляем для корректной загрузки файлов в некоторых средах

# --- Константы и настройки ---
# Размеры экрана
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 450
GROUND_HEIGHT: int = 50 # Высота "земли" от нижнего края экрана
FPS: int = 60

# Физические параметры
GRAVITY: float = 2000.0        # Ускорение свободного падения (пикселей/с^2)
JUMP_STRENGTH: float = -800.0  # Начальная вертикальная скорость прыжка (пикселей/с)
# Расчет максимальной высоты прыжка (h = v^2 / (2*g))
# Используется для ограничения высоты кактусов
MAX_JUMP_HEIGHT: float = (abs(JUMP_STRENGTH) ** 2) / (2 * GRAVITY)

# Цвета (RGBA - добавлена альфа для прозрачности)
WHITE: tuple[int, int, int] = (255, 255, 255)
GRAY: tuple[int, int, int, int] = (128, 128, 128, 180) # Серый с прозрачностью
BLACK: tuple[int, int, int] = (0, 0, 0)
GREEN: tuple[int, int, int] = (0, 180, 0)

# Параметры препятствий (кактусов)
CACTUS_MIN_WIDTH: int = 20
CACTUS_MAX_WIDTH: int = 40
CACTUS_MIN_HEIGHT: int = 40
CACTUS_MAX_HEIGHT_FACTOR: float = 0.9 # Максимальная высота кактуса в процентах от макс. высоты прыжка

# Скорость игры
INITIAL_SPEED: float = 400.0   # Начальная скорость движения (пикселей/с)
SPEED_INCREMENT: float = 5.0   # На сколько увеличивается скорость каждые 100 очков

# Интервал спавна препятствий (в секундах)
SPAWN_INTERVAL_MIN: float = 0.8
SPAWN_INTERVAL_MAX: float = 1.5

# Пути к ресурсам (картинкам)
# Лучше использовать os.path.join для кроссплатформенности
PLAYER_IMG_PATH: str = os.path.join("assets", "character.png") # Предполагаем папку assets
BACKGROUND_IMG_PATH: str = os.path.join("assets", "background.png") # Предполагаем папку assets
# Убедитесь, что папка 'assets' существует и содержит картинки

# --- Вспомогательные функции ---
def load_image(path: str, scale_height: int | None = None) -> pygame.Surface:
    """Загружает изображение, обрабатывает ошибки и масштабирует его."""
    try:
        img = pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Ошибка загрузки изображения по пути: {path}")
        print(f"Детали ошибки: {e}")
        pygame.quit()
        sys.exit()

    if scale_height is not None:
        if img.get_height() != scale_height:
            ratio = scale_height / img.get_height()
            new_w = int(img.get_width() * ratio)
            img = pygame.transform.scale(img, (new_w, scale_height))

    return img

# --- Классы спрайтов ---
class Player(pygame.sprite.Sprite):
    """Представляет управляемого игрока (бегуна)."""
    def __init__(self, image: pygame.Surface, pos: tuple[int, int]):
        """
        Инициализирует игрока.

        Args:
            image: Поверхность (картинка) игрока.
            pos: Начальная позиция игрока (midbottom).
        """
        super().__init__()
        self.image: pygame.Surface = image
        self.rect: pygame.Rect = self.image.get_rect(midbottom=pos)
        self.vel_y: float = 0.0 # Вертикальная скорость
        self.is_jumping: bool = False

        # Границы земли для коллизии
        self._ground_y: int = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self, dt: float) -> None:
        """
        Обновляет состояние игрока.

        Args:
            dt: Время, прошедшее с последнего кадра в секундах.
        """
        # Применение гравитации
        self.vel_y += GRAVITY * dt
        self.rect.y += self.vel_y * dt

        # Проверка коллизии с землей
        if self.rect.bottom >= self._ground_y:
            self.rect.bottom = self._ground_y
            self.vel_y = 0.0
            self.is_jumping = False

    def jump(self) -> None:
        """Заставляет игрока прыгнуть, если он находится на земле."""
        if not self.is_jumping:
            self.vel_y = JUMP_STRENGTH
            self.is_jumping = True

class Cactus(pygame.sprite.Sprite):
    """Представляет препятствие (кактус)."""
    def __init__(self):
        """Инициализирует кактус со случайным размером."""
        super().__init__()

        # Расчет случайных размеров с учетом ограничений
        self.width: int = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
        # Максимальная высота кактуса ограничена макс. высотой прыжка игрока
        max_possible_h = int(MAX_JUMP_HEIGHT * CACTUS_MAX_HEIGHT_FACTOR)
        max_h = max(max_possible_h, CACTUS_MIN_HEIGHT) # Гарантируем мин. высоту
        self.height: int = random.randint(CACTUS_MIN_HEIGHT, max_h)

        # Создание поверхности для кактуса (просто зеленый прямоугольник)
        self.image: pygame.Surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, self.image.get_rect())

        # Установка начальной позиции (за экраном справа)
        self.rect: pygame.Rect = self.image.get_rect(
            midbottom=(SCREEN_WIDTH + self.width // 2, SCREEN_HEIGHT - GROUND_HEIGHT)
        )
        self.passed: bool = False # Флаг, чтобы отслеживать, прошел ли игрок препятствие

    def update(self, dt: float, speed: float) -> None:
        """
        Обновляет состояние кактуса (перемещает влево).

        Args:
            dt: Время, прошедшее с последнего кадра в секундах.
            speed: Текущая скорость движения игры.
        """
        self.rect.x -= speed * dt
        # Спрайт будет автоматически удален из групп, если его rect.right < 0
        # (проверяется в Game._update)

# --- Класс игры ---
class Game:
    """Основной класс игры 'Бегущий Амиго'."""
    def __init__(self):
        """Инициализирует Pygame, окно, загружает ресурсы и настраивает начальное состояние."""
        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Бегущий Амиго")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.font: pygame.font.Font = pygame.font.Font(None, 40)

        self._load_resources()
        self._setup_game()

        self.running: bool = True # Флаг для основного цикла игры

    def _load_resources(self) -> None:
        """Загружает игровые ресурсы: изображения, поверхности."""
        self.bg_img: pygame.Surface = load_image(BACKGROUND_IMG_PATH, SCREEN_HEIGHT)
        self.bg_width: int = self.bg_img.get_width()
        self.player_img: pygame.Surface = load_image(PLAYER_IMG_PATH, 120)

        # Поверхность земли (полупрозрачный серый прямоугольник)
        self.ground_surf: pygame.Surface = pygame.Surface((SCREEN_WIDTH, GROUND_HEIGHT), pygame.SRCALPHA)
        self.ground_surf.fill(GRAY)

    def _setup_game(self) -> None:
        """Настраивает или сбрасывает начальное состояние игры."""
        # Создание игрока и групп спрайтов
        self.player: Player = Player(self.player_img, pos=(80, SCREEN_HEIGHT - GROUND_HEIGHT))
        # all_sprites содержит все спрайты для отрисовки
        self.all_sprites: pygame.sprite.Group = pygame.sprite.Group(self.player)
        # obstacles содержит только препятствия для коллизии и спавна
        self.obstacles: pygame.sprite.Group = pygame.sprite.Group()

        # Переменные состояния игры
        self.bg_x: float = 0.0 # Позиция фона для прокрутки
        self.game_speed: float = INITIAL_SPEED
        self.score: int = 0
        self.game_active: bool = True # Флаг активной игры (не Game Over)

        # Переменные для спавна препятствий
        self.spawn_timer: float = 0.0
        self.next_spawn_time: float = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

    def _handle_input(self) -> None:
        """Обрабатывает ввод пользователя (события Pygame)."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_active:
                        self.player.jump()
                    else:
                        # Если игра окончена, ПРОБЕЛ перезапускает игру
                        self._restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False # Выход из игры

    def _update(self, dt: float) -> None:
        """
        Обновляет состояние всех игровых элементов.

        Args:
            dt: Время, прошедшее с последнего кадра в секундах.
        """
        if self.game_active:
            # Обновление позиции фона (параллакс эффект)
            # Скорость фона меньше скорости игры
            self.bg_x = (self.bg_x - self.game_speed * dt * 0.5) % self.bg_width

            # Спавн новых препятствий
            self.spawn_timer += dt
            if self.spawn_timer >= self.next_spawn_time:
                self._spawn_obstacle()
                self.spawn_timer = 0.0
                self.next_spawn_time = random.uniform(SPAWN_INTERVAL_MIN, SPAWN_INTERVAL_MAX)

            # Обновление спрайтов
            self.player.update(dt)
            # Передаем скорость кактусам для их движения
            self.obstacles.update(dt, self.game_speed)

            # Удаление вышедших за экран препятствий и начисление очков
            # Итерируемся по копии, чтобы избежать ошибок при удалении из группы
            for cactus in list(self.obstacles):
                 if cactus.rect.right < 0:
                    cactus.kill() # Удаляет спрайт из всех групп, которым он принадлежит
                 # Проверяем, прошел ли игрок кактус (для начисления очков)
                 # Проверка происходит, когда правый край кактуса пересекает левый край игрока
                 if not cactus.passed and cactus.rect.right < self.player.rect.left:
                    cactus.passed = True
                    self.score += 10
                    # Увеличение скорости игры каждые 100 очков
                    if self.score % 100 == 0:
                        self.game_speed += SPEED_INCREMENT

            # Проверка коллизии игрока с препятствиями
            if pygame.sprite.spritecollideany(self.player, self.obstacles):
                self.game_active = False # Конец игры

    def _draw(self) -> None:
        """Отрисовывает все игровые элементы на экране."""
        # Отрисовка фона (рисуем два фона для бесшовной прокрутки)
        self.screen.blit(self.bg_img, (int(self.bg_x - self.bg_width), 0))
        self.screen.blit(self.bg_img, (int(self.bg_x), 0))

        # Отрисовка земли
        self.screen.blit(self.ground_surf, (0, SCREEN_HEIGHT - GROUND_HEIGHT))

        # Отрисовка всех спрайтов (игрока и препятствий)
        self.all_sprites.draw(self.screen)

        # Отрисовка счета
        score_surf = self.font.render(f"Счет: {self.score}", True, BLACK)
        # Размещаем счет в правом верхнем углу с отступом
        score_rect = score_surf.get_rect(topright=(SCREEN_WIDTH - 15, 15))
        self.screen.blit(score_surf, score_rect)

        # Если игра окончена, рисуем экран Game Over поверх всего
        if not self.game_active:
            self._draw_game_over()

        # Обновление всего содержимого экрана
        pygame.display.flip()

    def _spawn_obstacle(self) -> None:
        """Создает новый кактус и добавляет его в группы."""
        cactus = Cactus()
        self.obstacles.add(cactus)
        self.all_sprites.add(cactus) # Добавляем в основную группу для отрисовки

    def _restart_game(self) -> None:
        """Сбрасывает состояние игры до начального."""
        # Очищаем все группы спрайтов
        self.all_sprites.empty()
        self.obstacles.empty()
        # Вызываем _setup_game для создания нового игрока и сброса переменных
        self._setup_game()

    def _draw_game_over(self) -> None:
        """Отрисовывает экран "Игра окончена"."""
        # Создаем полупрозрачный оверлей
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) # Черный с прозрачностью
        self.screen.blit(overlay, (0, 0))

        # Текст "Игра окончена" и счет
        go_text_surf = self.font.render("Игра окончена!", True, WHITE)
        restart_text_surf = self.font.render("Нажми ПРОБЕЛ для перезапуска", True, WHITE)
        score_text_surf = self.font.render(f"Твой финальный счет: {self.score}", True, WHITE)

        # Размещаем текст по центру экрана
        go_rect = go_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        restart_rect = restart_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        score_rect = score_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        self.screen.blit(go_text_surf, go_rect)
        self.screen.blit(restart_text_surf, restart_rect)
        self.screen.blit(score_text_surf, score_rect)


    def run(self) -> None:
        """Запускает основной цикл игры."""
        while self.running:
            # Вычисляем время, прошедшее с последнего кадра (delta time)
            # dt в секундах
            dt = self.clock.tick(FPS) / 1000.0

            self._handle_input()
            self._update(dt)
            self._draw()

        # Выход из Pygame при завершении цикла
        pygame.quit()
        sys.exit()

# --- Точка входа ---
if __name__ == '__main__':
    # Убедитесь, что папка 'assets' существует и содержит character.png и background.png
    if not os.path.exists("assets"):
        print("Ошибка: Папка 'assets' не найдена.")
        print("Создайте папку 'assets' в той же директории, что и скрипт,")
        print("и поместите туда файлы character.png и background.png.")
        sys.exit()

    game = Game()
    game.run()
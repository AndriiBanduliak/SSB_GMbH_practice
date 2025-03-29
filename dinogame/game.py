import pygame
import random
import sys

pygame.init()

# --- Konstanten ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
GROUND_HEIGHT = 50

WHITE = (255, 255, 255)
GRAY = (128, 128, 128)  # Farbe des Bodens
BLACK = (0, 0, 0)       # Hauptfarbe für Zeichnungen
GREEN = (0, 180, 0)     # Farbe für Kakteen
BROWN = (139, 69, 19)   # Farbe für Pterodaktylen

# --- Spielerparameter ---
PLAYER_START_X = 50
PLAYER_START_Y = SCREEN_HEIGHT - GROUND_HEIGHT

PLAYER_RUN_WIDTH = 40
PLAYER_RUN_HEIGHT = 50
PLAYER_LEG_HEIGHT = 15
PLAYER_LEG_WIDTH = 8

PLAYER_DUCK_WIDTH = 55
PLAYER_DUCK_HEIGHT = 30

GRAVITY = 0.8
JUMP_STRENGTH = -16

# --- Hindernisparameter ---
CACTUS_MIN_WIDTH = 15
CACTUS_MAX_WIDTH = 30
CACTUS_MIN_HEIGHT = 30
CACTUS_MAX_HEIGHT = 60

PTERO_WIDTH = 45
PTERO_HEIGHT = 20
PTERO_WING_LENGTH = 20

# --- Spielparameter ---
INITIAL_GAME_SPEED = 5
SPEED_INCREMENT = 0.001
OBSTACLE_SPAWN_RATE_INITIAL = 100
OBSTACLE_SPAWN_RATE_MIN = 40
PTERO_CHANCE = 0.25

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pixel-Dinosaurier v3 (Gezeichnet)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# --- Hindernisklasse ---


class Obstacle:
    def __init__(self, type):
        self.type = type  # 'cactus' oder 'ptero'
        self.passed = False

        if type == 'cactus':
            self.width = random.randint(CACTUS_MIN_WIDTH, CACTUS_MAX_WIDTH)
            self.height = random.randint(CACTUS_MIN_HEIGHT, CACTUS_MAX_HEIGHT)
            self.rect = pygame.Rect(SCREEN_WIDTH,
                                    SCREEN_HEIGHT - GROUND_HEIGHT - self.height,
                                    self.width, self.height)
            self.color = GREEN
            # Добавляем «ветви» кактуса
            self.arms = []
            if random.random() > 0.4:
                arm_height = random.randint(self.height // 3, self.height // 2)
                arm_width = self.width // 3
                arm_y = self.rect.y + self.height // 4
                if random.random() > 0.5:
                    self.arms.append(pygame.Rect(
                        self.rect.x - arm_width, arm_y, arm_width, arm_height))
                if random.random() > 0.5:
                    self.arms.append(pygame.Rect(
                        self.rect.right, arm_y, arm_width, arm_height))
        elif type == 'ptero':
            self.width = PTERO_WIDTH
            self.height = PTERO_HEIGHT
            ptero_height_options = [
                SCREEN_HEIGHT - GROUND_HEIGHT - 80,
                SCREEN_HEIGHT - GROUND_HEIGHT - 55,
                SCREEN_HEIGHT - GROUND_HEIGHT - 110
            ]
            start_y = random.choice(ptero_height_options)
            self.rect = pygame.Rect(
                SCREEN_WIDTH, start_y - self.height, self.width, self.height)
            self.color = BROWN
            self.wing_state = 0  # Für einfache Flügelanimation

    def update(self, speed):
        self.rect.x -= speed
        if self.type == 'cactus':
            for i in range(len(self.arms)):
                if i == 0 and self.arms[i].x < self.rect.x:
                    self.arms[i].right = self.rect.left
                elif i == 1 and self.arms[i].x > self.rect.x:
                    self.arms[i].left = self.rect.right
        elif self.type == 'ptero':
            self.wing_state = (self.wing_state + 1) % 30

    def draw(self, surface):
        if self.type == 'cactus':
            # Zeichne einen stilisierten Kaktus als Polygon
            body_points = [
                (self.rect.centerx - self.width // 4, self.rect.bottom),
                (self.rect.centerx - self.width // 4,
                 self.rect.top + self.height // 3),
                (self.rect.left, self.rect.top + self.height // 3),
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.top),
                (self.rect.right, self.rect.top + self.height // 3),
                (self.rect.centerx + self.width // 4,
                 self.rect.top + self.height // 3),
                (self.rect.centerx + self.width // 4, self.rect.bottom)
            ]
            pygame.draw.polygon(surface, self.color, body_points)
            # Zeichne die Arme
            for arm in self.arms:
                arm_points = [
                    (arm.left, arm.bottom),
                    (arm.left, arm.top),
                    (arm.right, arm.top),
                    (arm.right, arm.bottom)
                ]
                pygame.draw.polygon(surface, self.color, arm_points)
        elif self.type == 'ptero':
            # Zeichne den Körper als Ellipse
            pygame.draw.ellipse(surface, self.color, self.rect)
            wing_offset = PTERO_WING_LENGTH if self.wing_state < 15 else -PTERO_WING_LENGTH
            left_wing = [
                (self.rect.left, self.rect.centery),
                (self.rect.left - self.width, self.rect.centery + wing_offset // 2),
                (self.rect.left, self.rect.centery + wing_offset)
            ]
            right_wing = [
                (self.rect.right, self.rect.centery),
                (self.rect.right + self.width, self.rect.centery + wing_offset // 2),
                (self.rect.right, self.rect.centery + wing_offset)
            ]
            pygame.draw.polygon(surface, self.color, left_wing)
            pygame.draw.polygon(surface, self.color, right_wing)

# --- Spielvariablen ---


def reset_game():
    global player_y, player_velocity_y, is_jumping, is_ducking, player_rect
    global obstacles, score, game_speed, game_active, obstacle_timer, animation_timer

    player_y = PLAYER_START_Y - PLAYER_RUN_HEIGHT
    player_velocity_y = 0
    is_jumping = False
    is_ducking = False
    player_rect = pygame.Rect(PLAYER_START_X, player_y,
                              PLAYER_RUN_WIDTH, PLAYER_RUN_HEIGHT)

    obstacles = []
    score = 0
    game_speed = INITIAL_GAME_SPEED
    game_active = True
    obstacle_timer = 0
    animation_timer = 0


reset_game()


def draw_player():
    """Zeichnet den Dinosaurier basierend auf seinem Zustand"""
    global animation_timer
    player_body_color = BLACK

    if is_ducking:
        # Zeichne einen duckenden Dinosaurier als Polygon
        points = [
            (player_rect.left, player_rect.bottom),
            (player_rect.left, player_rect.top + player_rect.height * 0.5),
            (player_rect.right, player_rect.top + player_rect.height * 0.5),
            (player_rect.right, player_rect.bottom)
        ]
        pygame.draw.polygon(screen, player_body_color, points)
        # Kopf als kleiner Kreis
        pygame.draw.circle(
            screen, WHITE, (player_rect.right - 10, player_rect.top + 10), 3)
    else:
        # Zeichne einen laufenden Dinosaurier als stilisiertes Polygon mit Kopf und Schwanz
        body_points = [
            (player_rect.left, player_rect.bottom),
            (player_rect.left, player_rect.top + player_rect.height * 0.3),
            (player_rect.centerx, player_rect.top),
            (player_rect.right, player_rect.top + player_rect.height * 0.3),
            (player_rect.right, player_rect.bottom)
        ]
        pygame.draw.polygon(screen, player_body_color, body_points)
        # Kopf als Kreis (leicht versetzt)
        head_center = (player_rect.right + 5, player_rect.top + 10)
        pygame.draw.circle(screen, player_body_color, head_center, 8)
        pygame.draw.circle(
            screen, WHITE, (head_center[0] + 3, head_center[1] - 3), 3)


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
    current_spawn_rate = max(OBSTACLE_SPAWN_RATE_MIN,
                             OBSTACLE_SPAWN_RATE_INITIAL - int(game_speed * 4))
    if obstacle_timer > current_spawn_rate and len(obstacles) < 4:
        obstacle_timer = random.randint(0, int(current_spawn_rate * 0.3))
        if random.random() < PTERO_CHANCE and score > 30:
            new_obs = Obstacle('ptero')
        else:
            new_obs = Obstacle('cactus')
        can_spawn = True
        if obstacles:
            last_obstacle = obstacles[-1]
            min_distance = max(200, int(SCREEN_WIDTH / 2.0 - game_speed * 12))
            if new_obs.rect.left < last_obstacle.rect.right + min_distance:
                can_spawn = False
        if can_spawn:
            obstacles.append(new_obs)


def check_collisions():
    for obs in obstacles:
        if player_rect.colliderect(obs.rect):
            if obs.type == 'cactus' and hasattr(obs, 'arms'):
                for arm in obs.arms:
                    if player_rect.colliderect(arm):
                        return True
            return True
    return False


def update_player_state():
    global player_rect, is_jumping
    if is_ducking and not is_jumping:
        player_rect.width = PLAYER_DUCK_WIDTH
        player_rect.height = PLAYER_DUCK_HEIGHT
    else:
        player_rect.width = PLAYER_RUN_WIDTH
        player_rect.height = PLAYER_RUN_HEIGHT
    if not is_jumping:
        player_rect.bottom = PLAYER_START_Y


def display_score():
    score_surf = font.render(f"Punktzahl: {score}", True, BLACK)
    score_rect = score_surf.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    screen.blit(score_surf, score_rect)


def display_game_over():
    screen.fill(WHITE)
    game_over_surf = font.render("SPIEL VORBEI", True, BLACK)
    restart_surf = font.render("Drücke LEERTASTE zum Neustart", True, BLACK)
    final_score_surf = font.render(f"Endpunktzahl: {score}", True, BLACK)
    game_over_rect = game_over_surf.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    final_score_rect = final_score_surf.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_surf.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 2 // 3))
    screen.blit(game_over_surf, game_over_rect)
    screen.blit(final_score_surf, final_score_rect)
    screen.blit(restart_surf, restart_rect)


running = True
while running:
    animation_timer = (animation_timer + 1) % 60

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game_active:
                if event.key == pygame.K_SPACE and not is_jumping and not is_ducking:
                    player_velocity_y = JUMP_STRENGTH
                    is_jumping = True
                elif event.key == pygame.K_DOWN and not is_jumping:
                    is_ducking = True
                    update_player_state()
                elif event.key == pygame.K_ESCAPE:
                    running = False
            else:
                if event.key == pygame.K_SPACE:
                    reset_game()
                elif event.key == pygame.K_ESCAPE:
                    running = False
        if event.type == pygame.KEYUP:
            if game_active:
                if event.key == pygame.K_DOWN and is_ducking:
                    is_ducking = False
                    update_player_state()

    if game_active:
        player_velocity_y += GRAVITY
        player_rect.y += int(player_velocity_y)

        if player_rect.bottom >= PLAYER_START_Y:
            player_rect.bottom = PLAYER_START_Y
            player_velocity_y = 0
            is_jumping = False
            update_player_state()

        if not is_jumping and not is_ducking and player_rect.height != PLAYER_RUN_HEIGHT:
            update_player_state()

        spawn_obstacle()
        move_obstacles()

        if check_collisions():
            game_active = False

        game_speed += SPEED_INCREMENT

        screen.fill(WHITE)
        pygame.draw.rect(screen, GRAY, (0, SCREEN_HEIGHT -
                         GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        draw_obstacles()
        draw_player()
        display_score()
    else:
        display_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

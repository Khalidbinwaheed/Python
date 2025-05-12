# dodger.py
import pygame
import sys
import random

WIDTH, HEIGHT = 600, 800
PLAYER_WIDTH, PLAYER_HEIGHT = 50, 50
OBSTACLE_WIDTH, OBSTACLE_HEIGHT = 40, 40
PLAYER_SPEED = 8
OBSTACLE_SPEED_MIN = 3
OBSTACLE_SPEED_MAX = 7
OBSTACLE_SPAWN_RATE = 40 # Lower means more obstacles (frames between spawns)
SPAWN_RATE_DECREASE = 0.1 # How much the spawn rate decreases over time

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 40)

# --- Game Functions ---
def game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = font.render(f"Game Over! Score: {score}", True, RED)
    restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    waiting = False # Will trigger restart in main loop

# --- Main Game Function ---
def run_game():
    # --- Game State ---
    player = pygame.Rect(WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - PLAYER_HEIGHT - 10, PLAYER_WIDTH, PLAYER_HEIGHT)
    obstacles = [] # List to hold obstacle Rects and their speeds
    score = 0
    spawn_timer = 0
    current_spawn_rate = OBSTACLE_SPAWN_RATE
    game_over = False

    # --- Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_over:
            game_over_screen(score)
            run_game() # Restart game
            return # Exit current instance

        # --- Player Movement ---
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += PLAYER_SPEED

        # --- Obstacle Spawning ---
        spawn_timer += 1
        if spawn_timer >= current_spawn_rate:
            spawn_timer = 0
            obstacle_x = random.randint(0, WIDTH - OBSTACLE_WIDTH)
            obstacle_speed = random.randint(OBSTACLE_SPEED_MIN, OBSTACLE_SPEED_MAX)
            obstacle = {'rect': pygame.Rect(obstacle_x, -OBSTACLE_HEIGHT, OBSTACLE_WIDTH, OBSTACLE_HEIGHT),
                        'speed': obstacle_speed}
            obstacles.append(obstacle)
            # Increase difficulty slightly over time by reducing spawn interval
            current_spawn_rate = max(10, current_spawn_rate - SPAWN_RATE_DECREASE)


        # --- Obstacle Movement & Collision ---
        # Iterate over a copy of the list for safe removal
        for obstacle_data in obstacles[:]:
            obstacle_rect = obstacle_data['rect']
            obstacle_speed = obstacle_data['speed']

            obstacle_rect.y += obstacle_speed

            # Check collision with player
            if player.colliderect(obstacle_rect):
                game_over = True

            # Remove obstacle if it goes off-screen
            if obstacle_rect.top > HEIGHT:
                obstacles.remove(obstacle_data)
                score += 1 # Score for successfully dodging

        # --- Drawing ---
        screen.fill(BLACK)

        # Draw player
        pygame.draw.rect(screen, BLUE, player)

        # Draw obstacles
        for obstacle_data in obstacles:
            pygame.draw.rect(screen, RED, obstacle_data['rect'])

        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Rate ---
        clock.tick(60)

    # --- Cleanup ---
    pygame.quit()
    sys.exit()

# --- Start Game ---
if __name__ == "__main__":
    run_game()
import pygame
import random
import sys
import os # To check for asset files

# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init() # Initialize the mixer for sound

# --- Constants ---
GRID_SIZE = 20
GRID_WIDTH = 30  # Number of grid cells horizontally
GRID_HEIGHT = 20 # Number of grid cells vertically
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE

# Colors (RGB)
WHITE = (255, 255, 255)
GREEN_HEAD = (0, 50, 50)
GREEN_BODY = (0, 50, 0)
RED_APPLE = (200, 0, 0)
BROWN_STEM = (139, 69, 19)
BLACK = (0, 0, 0)
DARK_GRAY_WALL = (50, 50, 50)
GRASS_GREEN_DARK = (34, 139, 34)
GRASS_GREEN_LIGHT = (50, 205, 50)
EYE_COLOR = (255, 255, 255)
PUPIL_COLOR = (0, 0, 0)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Game speed
INITIAL_FPS = 10
FPS_INCREASE_INTERVAL = 5

# Visual tweaks
SNAKE_BORDER_RADIUS = 0.3 # Percentage of GRID_SIZE for rounded corners
FOOD_RADIUS = GRID_SIZE // 2 - 1 # Radius for apple circle
EYE_OFFSET_FACTOR = 0.25 # How far eyes are from center
EYE_RADIUS = GRID_SIZE // 6
PUPIL_RADIUS = GRID_SIZE // 12

# --- Asset Loading ---
# Sound Effects
eat_sound = None
game_over_sound = None
try:
    eat_sound_path = 'eat_sound.wav' # Or .ogg
    if os.path.exists(eat_sound_path):
        eat_sound = pygame.mixer.Sound(eat_sound_path)
    else:
        print(f"Warning: Sound file '{eat_sound_path}' not found.")

    game_over_sound_path = 'game_over_sound.wav' # Or .ogg
    if os.path.exists(game_over_sound_path):
        game_over_sound = pygame.mixer.Sound(game_over_sound_path)
    else:
        print(f"Warning: Sound file '{game_over_sound_path}' not found.")
except pygame.error as e:
    print(f"Error loading sound files: {e}. Sound will be disabled.")
    eat_sound = None
    game_over_sound = None

# Background Texture (Optional)
grass_texture = None
try:
    texture_path = 'grass_tile.png'
    if os.path.exists(texture_path):
        grass_texture = pygame.image.load(texture_path).convert()
        # Ensure tile size matches grid size (optional, but good practice)
        if grass_texture.get_width() != GRID_SIZE or grass_texture.get_height() != GRID_SIZE:
            grass_texture = pygame.transform.scale(grass_texture, (GRID_SIZE, GRID_SIZE))
    else:
        print(f"Info: Background texture '{texture_path}' not found. Using gradient.")
except pygame.error as e:
    print(f"Error loading texture: {e}. Using gradient.")
    grass_texture = None


# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Realistic Snake Game')
clock = pygame.time.Clock()
font_style = pygame.font.SysFont("bahnschrift", 25) # A slightly nicer default font

# --- Helper Functions ---

def draw_background_and_walls():
    """Draws the background (texture or gradient) and walls."""
    # Background
    if grass_texture:
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                screen.blit(grass_texture, (x, y))
    else:
        # Simple gradient background
        for y in range(GRID_HEIGHT):
            # Interpolate color from top (lighter) to bottom (darker)
            ratio = y / GRID_HEIGHT
            color = (
                int(GRASS_GREEN_LIGHT[0] * (1 - ratio) + GRASS_GREEN_DARK[0] * ratio),
                int(GRASS_GREEN_LIGHT[1] * (1 - ratio) + GRASS_GREEN_DARK[1] * ratio),
                int(GRASS_GREEN_LIGHT[2] * (1 - ratio) + GRASS_GREEN_DARK[2] * ratio)
            )
            pygame.draw.rect(screen, color, (0, y * GRID_SIZE, SCREEN_WIDTH, GRID_SIZE))

    # Walls (draw thicker borders) - Adjust grid if you want playable area inside walls
    wall_thickness = GRID_SIZE // 4
    pygame.draw.rect(screen, DARK_GRAY_WALL, (0, 0, SCREEN_WIDTH, wall_thickness)) # Top
    pygame.draw.rect(screen, DARK_GRAY_WALL, (0, SCREEN_HEIGHT - wall_thickness, SCREEN_WIDTH, wall_thickness)) # Bottom
    pygame.draw.rect(screen, DARK_GRAY_WALL, (0, 0, wall_thickness, SCREEN_HEIGHT)) # Left
    pygame.draw.rect(screen, DARK_GRAY_WALL, (SCREEN_WIDTH - wall_thickness, 0, wall_thickness, SCREEN_HEIGHT)) # Right


def draw_snake(snake_list, direction):
    """Draws the snake with rounded segments and eyes."""
    border_int = int(GRID_SIZE * SNAKE_BORDER_RADIUS)

    # Draw head
    if snake_list:
        head_x_grid, head_y_grid = snake_list[0]
        head_rect = pygame.Rect(head_x_grid * GRID_SIZE, head_y_grid * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, GREEN_HEAD, head_rect, border_radius=border_int)

        # Draw Eyes based on direction
        eye_offset_x = int(GRID_SIZE * EYE_OFFSET_FACTOR * direction[1]) # Offset horizontally if moving U/D
        eye_offset_y = int(GRID_SIZE * EYE_OFFSET_FACTOR * direction[0]) # Offset vertically if moving L/R

        # Eye 1 position
        eye1_center_x = head_rect.centerx - eye_offset_x
        eye1_center_y = head_rect.centery + eye_offset_y
        pygame.draw.circle(screen, EYE_COLOR, (eye1_center_x, eye1_center_y), EYE_RADIUS)
        pygame.draw.circle(screen, PUPIL_COLOR, (eye1_center_x, eye1_center_y), PUPIL_RADIUS)

        # Eye 2 position
        eye2_center_x = head_rect.centerx + eye_offset_x
        eye2_center_y = head_rect.centery - eye_offset_y
        pygame.draw.circle(screen, EYE_COLOR, (eye2_center_x, eye2_center_y), EYE_RADIUS)
        pygame.draw.circle(screen, PUPIL_COLOR, (eye2_center_x, eye2_center_y), PUPIL_RADIUS)


    # Draw body
    for segment in snake_list[1:]:
        segment_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, GREEN_BODY, segment_rect, border_radius=border_int)

def draw_food(food_pos):
    """Draws the food item (apple)."""
    food_center_x = food_pos[0] * GRID_SIZE + GRID_SIZE // 2
    food_center_y = food_pos[1] * GRID_SIZE + GRID_SIZE // 2
    # Apple body
    pygame.draw.circle(screen, RED_APPLE, (food_center_x, food_center_y), FOOD_RADIUS)
    # Stem
    stem_start = (food_center_x, food_center_y - FOOD_RADIUS + 2)
    stem_end = (food_center_x + 2, food_center_y - FOOD_RADIUS - 4)
    pygame.draw.line(screen, BROWN_STEM, stem_start, stem_end, 2)


def place_food(snake_list):
    """Generates a random position for the food, avoiding snake and walls."""
    while True:
        # Keep food away from the very edge (walls)
        x = random.randrange(1, GRID_WIDTH - 1)
        y = random.randrange(1, GRID_HEIGHT - 1)
        food_pos = (x, y)
        if food_pos not in snake_list:
            return food_pos

def display_score(score):
    """Renders and displays the current score."""
    score_text = font_style.render(f"Score: {score}", True, WHITE)
    # Position score top-right, offset from wall
    score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - GRID_SIZE, GRID_SIZE // 2))
    screen.blit(score_text, score_rect)

def message(msg, color, y_displace=0):
    """Displays a centered message on the screen."""
    mesg = font_style.render(msg, True, color)
    mesg_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_displace))
    screen.blit(mesg, mesg_rect)

# --- Game Loop Function ---
def game_loop():
    game_over = False
    game_close = False

    # Initial snake position (start away from walls)
    snake_x = GRID_WIDTH // 2
    snake_y = GRID_HEIGHT // 2
    snake_list = [(snake_x, snake_y)]
    snake_length = 1

    direction = RIGHT
    change_to = direction

    food_pos = place_food(snake_list)

    score = 0
    current_fps = INITIAL_FPS

    # --- Main Game Loop ---
    while not game_over:

        # --- Game Over Screen ---
        while game_close:
            screen.fill(BLACK) # Clear screen for message
            message("You Lost! Press C-Play Again or Q-Quit", RED_APPLE, -50)
            display_score(score)
            pygame.display.update()

            if game_over_sound:
                # Play only once when entering game over screen
                if not pygame.mixer.get_busy(): # Avoid overlapping plays if loop is fast
                    game_over_sound.play()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        game_loop() # Restart

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                # Buffer direction change
                if (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != RIGHT:
                    change_to = LEFT
                elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != LEFT:
                    change_to = RIGHT
                elif (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != DOWN:
                    change_to = UP
                elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != UP:
                    change_to = DOWN
                elif event.key == pygame.K_ESCAPE:
                     game_over = True

        # Apply buffered direction change
        direction = change_to

        # --- Update Snake Position ---
        snake_x += direction[0]
        snake_y += direction[1]

        # --- Collision Detection ---
        # Wall collision (adjusting for visual walls)
        if snake_x >= GRID_WIDTH -1 or snake_x < 1 or snake_y >= GRID_HEIGHT - 1 or snake_y < 1:
             game_close = True

        snake_head = (snake_x, snake_y)

        # Self collision
        if snake_head in snake_list[1:]:
             game_close = True

        # --- Update Snake Body ---
        snake_list.insert(0, snake_head)

        # Food collision
        if snake_head == food_pos:
            if eat_sound:
                eat_sound.play()
            score += 1
            snake_length += 1
            food_pos = place_food(snake_list)
            if score % FPS_INCREASE_INTERVAL == 0 and score > 0:
                current_fps += 1
        else:
            if len(snake_list) > snake_length:
                snake_list.pop()

        # --- Drawing ---
        draw_background_and_walls() # Draw background and walls first
        draw_snake(snake_list, direction) # Pass direction for eyes
        draw_food(food_pos)
        display_score(score)

        # --- Update Display ---
        pygame.display.flip() # More efficient update than update() for full screen changes

        # --- Control Speed ---
        clock.tick(current_fps)

    # --- Quit ---
    pygame.mixer.quit() # Clean up mixer
    pygame.quit()
    sys.exit()

# --- Run the Game ---
if __name__ == "__main__":
    game_loop()
# dodger_pro.py
import pygame
import sys
import random
import os # To help locate assets

# --- Constants ---
WIDTH, HEIGHT = 600, 800
PLAYER_SPEED = 8
OBSTACLE_SPEED_MIN = 3
OBSTACLE_SPEED_MAX = 8 # Slightly increased max speed
OBSTACLE_SPAWN_RATE = 50 # Start a bit slower spawn
SPAWN_RATE_DECREASE = 0.08 # Slower decrease initially
SPEED_INCREASE_RATE = 0.01 # How much min/max speed increases per obstacle dodged

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# --- Asset Loading ---
# Helper function to load images safely
def load_image(name):
    fullname = os.path.join(os.path.dirname(__file__), name)
    try:
        image = pygame.image.load(fullname)
        # Use convert_alpha() for images with transparency (like PNGs)
        if image.get_alpha():
            image = image.convert_alpha()
        else:
            image = image.convert()
    except pygame.error as message:
        print(f"Cannot load image: {name}")
        raise SystemExit(message)
    return image, image.get_rect()

# Helper function to load sounds safely
def load_sound(name):
    # DummySound class to handle cases where sound module isn't available
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    fullname = os.path.join(os.path.dirname(__file__), name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error as message:
        print(f"Cannot load sound: {name}")
        # Don't raise SystemExit, just return the dummy sound
        sound = NoneSound()
    return sound


# --- Initialization ---
pygame.init()
# Initialize mixer for sound (optional, but good practice)
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodger Pro")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 74)
font_small = pygame.font.Font(None, 40)

# --- Load Assets ---
try:
    player_image, _ = load_image("player.png") # We only need the image surface here
    obstacle_image, _ = load_image("obstacle.png")
    background_image, background_rect = load_image("background.png")

    # Scale background if it's not the right width (optional, maintain aspect ratio)
    # background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    # background_rect = background_image.get_rect() # Update rect if scaled

    # Sound (Optional)
    collision_sound = load_sound("collision.wav")
    # Load background music separately
    music_path = os.path.join(os.path.dirname(__file__), "background_music.ogg")
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5) # Adjust volume (0.0 to 1.0)
        pygame.mixer.music.play(loops=-1) # Loop indefinitely
    except pygame.error as message:
        print(f"Cannot load music: background_music.ogg - {message}")
        # Game can continue without music

except SystemExit: # Catch exit from load_image
    pygame.quit()
    sys.exit()
except FileNotFoundError as e:
     print(f"Error: Asset file not found - {e}. Make sure image/sound files are in the same directory.")
     pygame.quit()
     sys.exit()


# --- Game Objects ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() # Initialize the parent Sprite class
        self.image = player_image # Use the loaded image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += PLAYER_SPEED

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, speed_min, speed_max):
        super().__init__()
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -self.rect.height) # Start off screen
        self.speed = random.randint(speed_min, speed_max)

    def update(self):
        self.rect.y += self.speed
        # Remove sprite if it goes off the bottom of the screen
        if self.rect.top > HEIGHT:
            self.kill() # Removes the sprite from all groups it belongs to

    def draw(self, surface):
        surface.blit(self.image, self.rect)


# --- Game Functions ---
def draw_text(surface, text, font, color, center_pos):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = center_pos
    surface.blit(text_surface, text_rect)

def show_start_screen():
    screen.blit(background_image, background_rect) # Draw background
    draw_text(screen, "DODGER PRO!", font_large, WHITE, (WIDTH // 2, HEIGHT // 4))
    draw_text(screen, "Use Left/Right Arrows to Move", font_small, WHITE, (WIDTH // 2, HEIGHT // 2))
    draw_text(screen, "Dodge the falling objects!", font_small, WHITE, (WIDTH // 2, HEIGHT // 2 + 50))
    draw_text(screen, "Press any key to start", font_small, RED, (WIDTH // 2, HEIGHT * 3 / 4))
    pygame.display.flip()
    wait_for_key()

def show_game_over_screen(score):
    screen.blit(background_image, background_rect) # Draw background
    draw_text(screen, "GAME OVER", font_large, RED, (WIDTH // 2, HEIGHT // 4))
    draw_text(screen, f"Score: {score}", font_small, WHITE, (WIDTH // 2, HEIGHT // 2))
    draw_text(screen, "Press R to Restart or Q to Quit", font_small, WHITE, (WIDTH // 2, HEIGHT * 3 / 4))
    pygame.display.flip()

    waiting = True
    while waiting:
        clock.tick(60) # Keep clock ticking even while waiting
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


def wait_for_key():
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP: # Wait for key release
                waiting = False


# --- Main Game Function ---
def run_game():
    # --- Game State ---
    player = Player()
    # Using Sprite Groups for easier management and collision detection
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    all_sprites.add(player)

    score = 0
    spawn_timer = 0
    current_spawn_rate = OBSTACLE_SPAWN_RATE
    current_speed_min = OBSTACLE_SPEED_MIN
    current_speed_max = OBSTACLE_SPEED_MAX

    # Background Scrolling variables
    bg_y1 = 0
    bg_y2 = -background_rect.height # Position the second background right above the first
    bg_speed = 2 # How fast the background scrolls

    game_state = "START" # Initial game state

    # --- Game Loop ---
    running = True
    while running:
        # --- Timing ---
        clock.tick(60) # Limit frame rate

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_state == "GAME_OVER" and event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_q:
                     running = False
                 if event.key == pygame.K_r:
                     # Simply return to let the main loop restart the game
                     return


        # --- State Machine ---
        if game_state == "START":
            show_start_screen()
            game_state = "PLAYING"
            # Reset game variables when starting/restarting
            player = Player()
            all_sprites = pygame.sprite.Group()
            obstacles = pygame.sprite.Group()
            all_sprites.add(player)
            score = 0
            spawn_timer = 0
            current_spawn_rate = OBSTACLE_SPAWN_RATE
            current_speed_min = OBSTACLE_SPEED_MIN
            current_speed_max = OBSTACLE_SPEED_MAX
            bg_y1 = 0
            bg_y2 = -background_rect.height


        elif game_state == "PLAYING":
            # --- Updates ---
            all_sprites.update() # Calls update() on all sprites in the group (Player)
            obstacles.update()   # Calls update() on all obstacles

            # --- Obstacle Spawning ---
            spawn_timer += 1
            if spawn_timer >= current_spawn_rate:
                spawn_timer = 0
                new_obstacle = Obstacle(current_speed_min, current_speed_max)
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle) # Add to all_sprites for drawing

                # Increase difficulty slightly over time
                current_spawn_rate = max(15, current_spawn_rate - SPAWN_RATE_DECREASE) # Spawn faster, minimum rate 15
                current_speed_min = min(10, current_speed_min + SPEED_INCREASE_RATE) # Increase min speed, max 10
                current_speed_max = min(15, current_speed_max + SPEED_INCREASE_RATE) # Increase max speed, max 15

            # --- Collision Detection ---
            # pygame.sprite.spritecollide(sprite, group, dokill)
            # Checks if 'player' collides with any sprite in 'obstacles' group
            # True means the collided obstacle(s) will be removed from the 'obstacles' group
            collided_obstacles = pygame.sprite.spritecollide(player, obstacles, True)
            if collided_obstacles:
                if collision_sound:
                    collision_sound.play()
                game_state = "GAME_OVER" # Change state on collision

            # --- Score ---
            # Simple scoring based on time/dodged obstacles could be added here
            # For now, score increases implicitly via difficulty ramping, shown at game over.
            # Or, increment score when obstacle.kill() is called due to going off screen?
            # Let's modify the Obstacle update slightly:
            for obstacle in list(obstacles): # Iterate over a copy if modifying group
                if obstacle.rect.top > HEIGHT:
                    obstacle.kill()
                    score += 1 # Score for dodging

            # --- Background Scrolling ---
            bg_y1 += bg_speed
            bg_y2 += bg_speed
            if bg_y1 >= background_rect.height:
                bg_y1 = bg_y2 - background_rect.height
            if bg_y2 >= background_rect.height:
                bg_y2 = bg_y1 - background_rect.height

            # --- Drawing ---
            # Draw scrolling background
            screen.blit(background_image, (0, bg_y1))
            screen.blit(background_image, (0, bg_y2))

            # Draw all sprites
            all_sprites.draw(screen) # Efficiently draws all sprites in the group

            # Draw score during gameplay
            draw_text(screen, f"Score: {score}", font_small, WHITE, (WIDTH / 2, 30))


        elif game_state == "GAME_OVER":
            show_game_over_screen(score)
            # Event handling inside show_game_over_screen will wait for R or Q
            # If R is pressed, the loop continues, hits pygame.QUIT or returns from run_game()
            # If Q is pressed, pygame quits.
            pass # Logic is handled within the function and event loop check


        # --- Update Display ---
        pygame.display.flip()


    # --- Cleanup ---
    pygame.mixer.music.stop() # Stop music on exit
    pygame.quit()
    sys.exit()

# --- Start Game ---
if __name__ == "__main__":
    while True: # Keep restarting the game until Q is pressed
        run_game()
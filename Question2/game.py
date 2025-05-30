import pygame
import random
import sys

# Importing sound effects and background music functions from a separate module
from sounds import (
    FIRE_SOUND,
    EXPLOSION_SOUND,
    COLLISION_SOUND,
    GAME_OVER_SOUND,
    VICTORY_SOUND,
    play_background_music,
)

# Initialize all imported pygame modules
pygame.init()
play_background_music()  # Play background music on game start

# Constants 
# Window dimensions
WIDTH, HEIGHT = 600, 800

# Speeds
PLAYER_VEL = 5
BULLET_VEL = 7
BOSS_BULLET_VEL = 5

# Timings
FPS = 60
BOSS_FIRE_INTERVAL = 60  # Frames between boss firing
PLAYER_FIRE_INTERVAL = 10  # Frames between player shots

# Game conditions
MAX_HEALTH = 3
BOSS_HEALTH = 50
LEVEL_ONE_SCORE = 200 # Score upto which Level 1 exists
LEVEL_TWO_SCORE = 500 # Score upto which Level 2 exists

# Game Setup
# Create game window
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

# function to load and scale images
def load_img(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

# Load all assets
PLAYER_IMG = load_img("assets/images/hero.png", (50, 30))
ENEMY_IMG = load_img("assets/images/enemy.png", (40, 30))
BOSS_IMG = load_img("assets/images/boss.png", (100, 60))
HEART_IMG = load_img("assets/images/health.png", (30, 30))
PICKUP_IMG = load_img("assets/images/health.png", (25, 25))  
BG_IMG = load_img("assets/images/background.png", (WIDTH, HEIGHT))

# font
FONT = pygame.font.SysFont("comicsans", 40)

# Function to draw the window, player, enemy and all assets
def draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health):
    WIN.blit(BG_IMG, (0, 0))  # Draw background
    WIN.blit(PLAYER_IMG, player.topleft)  # Draw player ship

    # Draw all player bullets
    for bullet in bullets:
        pygame.draw.rect(WIN, (0, 255, 0), bullet)

    # Draw all enemies
    for enemy in enemies:
        WIN.blit(ENEMY_IMG, enemy.topleft)

    # Draw boss and its health bar
    if boss:
        WIN.blit(BOSS_IMG, boss["rect"].topleft)
        bar_width = int(boss["rect"].width * (boss["health"] / BOSS_HEALTH))
        pygame.draw.rect(WIN, (255, 0, 0), (boss["rect"].x, boss["rect"].y - 10, bar_width, 5))

    # Draw boss bullets
    for b_bullet in boss_bullets:
        pygame.draw.rect(WIN, (255, 0, 0), b_bullet)

    # Draw health pickups
    for pickup in pickups:
        WIN.blit(PICKUP_IMG, pickup.topleft)

    # Draw player's health
    for i in range(health):
        WIN.blit(HEART_IMG, (WIDTH - 40 * (i + 1), 10))

    # Draw score and level
    WIN.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    WIN.blit(FONT.render(f"Level: {level}", True, (255, 255, 255)), (10, 50))

    pygame.display.update()  # Refresh display

#Function for bullet logic
def handle_bullets(bullets, enemies, boss):
    score_increase = 0
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL  # Move bullet upwards

        # Remove bullet if off-screen
        if bullet.y < 0:
            bullets.remove(bullet)
            continue

        # Check for collision with enemies
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                EXPLOSION_SOUND.play()
                score_increase += 10
                break

        # Check for collision with boss
        if boss and bullet.colliderect(boss["rect"]):
            boss["health"] -= 1
            bullets.remove(bullet)
            EXPLOSION_SOUND.play()
            if boss["health"] <= 0:
                return "boss_defeated", score_increase + 100

    return "continue", score_increase

# Game Over / Victory Screen
def display_game_over(message):
    # WIN.fill((0, 0, 0))  # Black background
    game_over_text = FONT.render(message, True, (255, 0, 0))
    instruction_text = FONT.render("Press R to Restart or Q to Quit", True, (255, 255, 255))

    # Center the text
    WIN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    WIN.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    # Wait for user input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit(); sys.exit()

# Main Game Function
def main():
    clock = pygame.time.Clock()

    # Player setup
    player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 30)
    bullets, enemies, pickups, boss_bullets = [], [], [], []
    boss, boss_active = None, False

    # Initial game state
    level, score, health = 1, 0, MAX_HEALTH
    spawn_timer = pickup_timer = boss_fire_timer = player_fire_timer = 0
    enemy_spawn_time = 30  # Frames between enemy spawns
    ENEMY_VEL = 3

    # Functions to spawn enemies and pickups
    def spawn_enemy():
        return pygame.Rect(random.randint(0, WIDTH - 40), random.randint(-100, -40), 40, 30)

    def spawn_pickup():
        return pygame.Rect(random.randint(0, WIDTH - 25), -30, 25, 25)

    # Main game loop
    while True:
        clock.tick(FPS)
        spawn_timer += 1
        pickup_timer += 1
        player_fire_timer += 1

        # Handle quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += PLAYER_VEL

        # Player shooting
        if keys[pygame.K_SPACE] and player_fire_timer >= PLAYER_FIRE_INTERVAL:
            player_fire_timer = 0
            center_x = player.centerx - 2
            offsets = [-10, 0, 10]
            bullets.extend([pygame.Rect(center_x + o, player.y, 4, 10) for o in offsets])
            FIRE_SOUND.play()

        # Enemy spawning
        if level < 3 and spawn_timer > enemy_spawn_time:
            spawn_timer = 0
            enemies.append(spawn_enemy())

        # Pickup spawning
        if pickup_timer > 300:
            pickup_timer = 0
            pickups.append(spawn_pickup())

        # Move enemies and handle collision with player
        for enemy in enemies[:]:
            enemy.y += ENEMY_VEL
            if enemy.y > HEIGHT or enemy.colliderect(player):
                enemies.remove(enemy)
                if enemy.colliderect(player):
                    COLLISION_SOUND.play()
                    health -= 1
                    if health <= 0:
                        pygame.mixer.music.stop()
                        GAME_OVER_SOUND.play()
                        return "lose"

        # Activate boss at level 3
        if level == 3 and not boss_active:
            boss = {"rect": pygame.Rect(WIDTH // 2 - 50, 50, 100, 60), "health": BOSS_HEALTH, "direction": 1}
            boss_active = True

        # Boss movement and shooting
        if boss:
            boss["rect"].x += boss["direction"] * 4
            if boss["rect"].right >= WIDTH or boss["rect"].left <= 0:
                boss["direction"] *= -1

            boss_fire_timer += 1
            if boss_fire_timer >= BOSS_FIRE_INTERVAL:
                boss_fire_timer = 0
                bx = boss["rect"].centerx - 2
                by = boss["rect"].bottom
                boss_bullets.extend([
                    pygame.Rect(bx, by, 4, 10),
                    pygame.Rect(bx - 20, by, 4, 10),
                    pygame.Rect(bx + 20, by, 4, 10)
                ])

        # Move and check boss bullets
        for b_bullet in boss_bullets[:]:
            b_bullet.y += BOSS_BULLET_VEL
            if b_bullet.colliderect(player):
                boss_bullets.remove(b_bullet)
                health -= 1
                if health <= 0:
                    pygame.mixer.music.stop()
                    GAME_OVER_SOUND.play()
                    return "lose"
            elif b_bullet.y > HEIGHT:
                boss_bullets.remove(b_bullet)

        # Move pickups
        for pickup in pickups[:]:
            pickup.y += 2
            if pickup.colliderect(player):
                pickups.remove(pickup)
                health = min(MAX_HEALTH, health + 1)
            elif pickup.y > HEIGHT:
                pickups.remove(pickup)

        # Handle bullet-enemy/boss collisions
        status, gained = handle_bullets(bullets, enemies, boss)
        score += gained

        # Victory condition
        if status == "boss_defeated":
            draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health)
            pygame.mixer.music.stop()
            VICTORY_SOUND.play()
            pygame.time.delay(1000)
            return "win"

        # Level progression
        if score >= LEVEL_ONE_SCORE and level == 1:
            level = 2
            ENEMY_VEL += 1
            enemy_spawn_time = max(10, enemy_spawn_time - 5)
        elif score >= LEVEL_TWO_SCORE and level == 2:
            level = 3

        # Draw everything for the current frame
        draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health)

# Game Entry Point
def run_game():
    while True:
        result = main()
        if result == "win":
            restart = display_game_over("You Win!")
        elif result == "lose":
            restart = display_game_over("Game Over")
        else:
            break

        if not restart:
            break

    pygame.quit()
    sys.exit()

# Launch the game
if __name__ == "__main__":
    run_game()

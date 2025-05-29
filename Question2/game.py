import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 800
PLAYER_VEL = 5
BULLET_VEL = 7
FPS = 60
BOSS_BULLET_VEL = 5
BOSS_HEALTH=50
BOSS_FIRE_INTERVAL = 60
PLAYER_FIRE_INTERVAL = 10
MAX_HEALTH = 3

# Window setup
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Space Shooter")

# Load and scale assets
def load_img(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

PLAYER_IMG = load_img("assets/hero.png", (50, 30))
ENEMY_IMG = load_img("assets/enemy.png", (40, 30))
BOSS_IMG = load_img("assets/boss.png", (100, 60))
HEART_IMG = load_img("assets/health.png", (30, 30))
PICKUP_IMG = load_img("assets/health.png", (25, 25))
BG_IMG = load_img("assets/bg1.png", (WIDTH, HEIGHT))

# Font
FONT = pygame.font.SysFont("comicsans", 40)

# Draw all game elements each frame
def draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health):
    WIN.blit(BG_IMG, (0, 0))
    WIN.blit(PLAYER_IMG, player.topleft)

    for bullet in bullets:
        pygame.draw.rect(WIN, (0, 255, 0), bullet)

    for enemy in enemies:
        WIN.blit(ENEMY_IMG, enemy.topleft)

    if boss:
        WIN.blit(BOSS_IMG, boss["rect"].topleft)
        # Boss health bar
        bar_width = int(boss["rect"].width * (boss["health"] / BOSS_HEALTH))
        pygame.draw.rect(WIN, (255, 0, 0), (boss["rect"].x, boss["rect"].y - 10, bar_width, 5))

    for b_bullet in boss_bullets:
        pygame.draw.rect(WIN, (255, 0, 0), b_bullet)

    for pickup in pickups:
        WIN.blit(PICKUP_IMG, pickup.topleft)

    # Draw health
    for i in range(health):
        WIN.blit(HEART_IMG, (WIDTH - 40 * (i + 1), 10))

    # Score and level
    WIN.blit(FONT.render(f"Score: {score}", True, (255, 255, 255)), (10, 10))
    WIN.blit(FONT.render(f"Level: {level}", True, (255, 255, 255)), (10, 50))
    pygame.display.update()

# Handle player bullets and their collisions
def handle_bullets(bullets, enemies, boss):
    score_increase = 0
    for bullet in bullets[:]:
        bullet.y -= BULLET_VEL
        if bullet.y < 0:
            bullets.remove(bullet)
            continue

        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score_increase += 10
                break

        if boss and bullet.colliderect(boss["rect"]):
            boss["health"] -= 1
            bullets.remove(bullet)
            if boss["health"] <= 0:
                return "boss_defeated", score_increase + 100

    return "continue", score_increase

# Display win/lose screen
def display_game_over(message):
    WIN.fill((0, 0, 0))
    game_over_text = FONT.render(message, True, (255, 0, 0))
    instruction_text = FONT.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    WIN.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 60))
    WIN.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Main game logic
def main():
    clock = pygame.time.Clock()
    player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 30)
    bullets, enemies, pickups, boss_bullets = [], [], [], []
    boss, boss_active = None, False

    level, score, health = 1, 0, MAX_HEALTH
    spawn_timer, pickup_timer, boss_fire_timer, player_fire_timer = 0, 0, 0, 0
    enemy_spawn_time = 30
    ENEMY_VEL = 3

    def spawn_enemy():
        return pygame.Rect(random.randint(0, WIDTH - 40), random.randint(-100, -40), 40, 30)

    def spawn_pickup():
        return pygame.Rect(random.randint(0, WIDTH - 25), -30, 25, 25)

    while True:
        clock.tick(FPS)
        spawn_timer += 1
        pickup_timer += 1
        player_fire_timer += 1

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += PLAYER_VEL
        if keys[pygame.K_SPACE] and player_fire_timer >= PLAYER_FIRE_INTERVAL:
            player_fire_timer = 0
            center_x = player.centerx - 2
            # Fire three bullets
            offsets = [-10, 0, 10]
            bullets.extend([pygame.Rect(center_x + o, player.y, 4, 10) for o in offsets])

        # Spawn enemies
        if level < 3 and spawn_timer > enemy_spawn_time:
            spawn_timer = 0
            enemies.append(spawn_enemy())

        # Spawn pickups
        if pickup_timer > 300:
            pickup_timer = 0
            pickups.append(spawn_pickup())

        # Enemy movement & collision
        for enemy in enemies[:]:
            enemy.y += ENEMY_VEL
            if enemy.y > HEIGHT or enemy.colliderect(player):
                enemies.remove(enemy)
                if enemy.colliderect(player):
                    health -= 1
                    if health <= 0:
                        return "lose"

        # Boss logic
        if level == 3 and not boss_active:
            boss = {"rect": pygame.Rect(WIDTH // 2 - 50, 50, 100, 60), "health": BOSS_HEALTH, "direction": 1}
            boss_active = True

        if boss:
            # Move boss
            boss["rect"].x += boss["direction"] * 4
            if boss["rect"].right >= WIDTH or boss["rect"].left <= 0:
                boss["direction"] *= -1

            # Boss fires bullets
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

        # Move boss bullets
        for b_bullet in boss_bullets[:]:
            b_bullet.y += BOSS_BULLET_VEL
            if b_bullet.colliderect(player):
                boss_bullets.remove(b_bullet)
                health -= 1
                if health <= 0:
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

        # Handle bullets
        status, gained = handle_bullets(bullets, enemies, boss)
        score += gained

        if status == "boss_defeated":
            draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health)
            pygame.time.delay(1000)
            return "win"

        # Level progression
        if score >= 50 and level == 1:
            level = 2
            ENEMY_VEL += 1
            enemy_spawn_time = max(10, enemy_spawn_time - 5)
        elif score >= 150 and level == 2:
            level = 3

        draw_window(player, bullets, enemies, boss, boss_bullets, pickups, score, level, health)

# Game loop with restart support
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

# Entry point
if __name__ == "__main__":
    run_game()

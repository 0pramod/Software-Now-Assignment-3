import pygame

# Initialize the mixer
pygame.mixer.init()

# Sound Effects
FIRE_SOUND = pygame.mixer.Sound("assets/sounds/laser.wav")
EXPLOSION_SOUND = pygame.mixer.Sound("assets/sounds/explosion.flac")
COLLISION_SOUND = pygame.mixer.Sound("assets/sounds/collision.wav")
GAME_OVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")
VICTORY_SOUND = pygame.mixer.Sound("assets/sounds/victory.ogg")

# Background music
def play_background_music():
    pygame.mixer.music.load("assets/sounds/background.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)  # Loop indefinitely

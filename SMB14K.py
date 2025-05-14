import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mario Clone - Vibe Mode ON")

# Clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)

# Player properties
player_width, player_height = 32, 32
player_x = 50
player_y = HEIGHT - player_height - 50
player_vel_x = 0
player_vel_y = 0
player_speed = 5
jump_force = 10
gravity = 0.5
on_ground = False

# Platforms
platforms = [
    pygame.Rect(0, HEIGHT - 20, WIDTH, 20),  # Ground
    pygame.Rect(100, HEIGHT - 100, 100, 10),
    pygame.Rect(250, HEIGHT - 150, 100, 10),
    pygame.Rect(400, HEIGHT - 200, 100, 10)
]

# Main game loop
running = True
while running:
    clock.tick(FPS)
    screen.fill(WHITE)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Key handling
    keys = pygame.key.get_pressed()
    player_vel_x = 0
    if keys[pygame.K_LEFT]:
        player_vel_x = -player_speed
    if keys[pygame.K_RIGHT]:
        player_vel_x = player_speed
    if keys[pygame.K_SPACE] and on_ground:
        player_vel_y = -jump_force
        on_ground = False

    # Apply gravity
    player_vel_y += gravity

    # Update player position
    player_x += player_vel_x
    player_y += player_vel_y

    # Create player rect
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

    # Collision detection
    on_ground = False
    for platform in platforms:
        if player_rect.colliderect(platform):
            if player_vel_y > 0:
                player_y = platform.top - player_height
                player_vel_y = 0
                on_ground = True

    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, BROWN, platform)

    # Draw player
    pygame.draw.rect(screen, RED, (player_x, player_y, player_width, player_height))

    # Update display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

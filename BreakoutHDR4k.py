import pygame
import sys
import random
import numpy as np

# Hide pygame welcome prompt
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

# Initialize mixer for stereo sound
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2)
pygame.init()

# Screen setup
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout - Raw Vibe Mode")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BRICK_COLOR = (200, 50, 50)
PADDLE_COLOR = (50, 200, 50)
BALL_COLOR = (50, 50, 200)

# Paddle setup
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 15
paddle_x = (WIDTH - PADDLE_WIDTH) // 2
paddle_y = HEIGHT - 40
paddle_speed = 7

# Ball setup
BALL_RADIUS = 10
ball_x = WIDTH // 2
ball_y = HEIGHT // 2
ball_speed_x = random.choice([-4, 4])
ball_speed_y = -4

# Brick setup
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_WIDTH = WIDTH // BRICK_COLS
BRICK_HEIGHT = 20
bricks = [pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 40, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
          for row in range(BRICK_ROWS) for col in range(BRICK_COLS)]

# Font
font = pygame.font.SysFont("Arial", 24)

# Score
score = 0

# Generate sine wave sound function (stereo)
def generate_tone(frequency, duration, amplitude=0.5):
    sample_rate = 44100
    samples_count = int(sample_rate * duration)
    t = np.arange(samples_count)
    waveform = amplitude * np.sin(2 * np.pi * frequency * t / sample_rate)
    stereo_waveform = np.column_stack((waveform, waveform))  # stereo
    stereo_waveform = np.int16(stereo_waveform * 32767)
    return pygame.sndarray.make_sound(stereo_waveform)

# Generate sounds on the fly
bounce_sound = generate_tone(880, 0.1)       # A5, quick bounce
brick_hit_sound = generate_tone(523, 0.1)    # C5, brick smash
game_over_sound = generate_tone(261, 0.5)    # C4, game over wail

clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < WIDTH - PADDLE_WIDTH:
        paddle_x += paddle_speed

    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Ball collision with walls
    if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WIDTH:
        ball_speed_x *= -1
        bounce_sound.play()
    if ball_y - BALL_RADIUS <= 0:
        ball_speed_y *= -1
        bounce_sound.play()

    # Ball collision with paddle
    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS*2, BALL_RADIUS*2)
    if ball_rect.colliderect(paddle_rect) and ball_speed_y > 0:
        ball_speed_y *= -1
        hit_pos = (ball_x - paddle_x) / PADDLE_WIDTH
        ball_speed_x = (hit_pos - 0.5) * 8
        bounce_sound.play()

    # Ball collision with bricks
    hit_index = ball_rect.collidelist(bricks)
    if hit_index != -1:
        bricks.pop(hit_index)
        ball_speed_y *= -1
        brick_hit_sound.play()
        score += 10

    # Ball falls below paddle — game over, reset
    if ball_y > HEIGHT:
        game_over_sound.play()
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 2
        ball_speed_x = random.choice([-4, 4])
        ball_speed_y = -4
        paddle_x = (WIDTH - PADDLE_WIDTH) // 2
        score = 0
        bricks = [pygame.Rect(col * BRICK_WIDTH, row * BRICK_HEIGHT + 40, BRICK_WIDTH - 2, BRICK_HEIGHT - 2)
                  for row in range(BRICK_ROWS) for col in range(BRICK_COLS)]

    # Draw bricks
    for brick in bricks:
        pygame.draw.rect(screen, BRICK_COLOR, brick)

    # Draw paddle
    pygame.draw.rect(screen, PADDLE_COLOR, paddle_rect)

    # Draw ball
    pygame.draw.circle(screen, BALL_COLOR, (int(ball_x), int(ball_y)), BALL_RADIUS)

    # Draw score
    score_surface = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surface, (10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()

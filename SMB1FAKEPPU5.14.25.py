import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 600, 400
TILE = 16
TILES_X = WIDTH // TILE
TILES_Y = HEIGHT // TILE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NES Mario - Python PPU 90s Vibes")
clock = pygame.time.Clock()
FPS = 60

# NES palette
SKY = (92, 148, 252)
GROUND = (228, 92, 16)
BRICK = (188, 60, 44)
BLOCK = (255, 216, 52)
PIPE = (16, 192, 64)
MARIO = (236, 0, 0)
SKIN = (255, 220, 170)
COIN = (255, 236, 32)
FLAG = (0, 200, 32)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

font = pygame.font.SysFont("Courier New", 16, bold=True)
bigfont = pygame.font.SysFont("Courier New", 32, bold=True)

LEVEL_COUNT = 32

def scanlines():
    # Draw CRT scanlines for extra nostalgia
    for y in range(0, HEIGHT, 2):
        pygame.draw.line(screen, (0,0,0,40), (0, y), (WIDTH, y), 1)

def nes_hud(lives, coins, levelnum, time):
    hud = font.render(f"MARIO   x{lives}   COIN:{coins:02}   WORLD:{levelnum+1:02}   TIME:{time:03}", True, WHITE)
    screen.blit(hud, (16, 4))

def make_level(level_idx):
    random.seed(level_idx)
    level = [[0 for _ in range(TILES_X * 3)] for _ in range(TILES_Y)]  # 3 screens wide
    # Ground
    for x in range(TILES_X * 3):
        for y in range(TILES_Y - 2, TILES_Y):
            level[y][x] = 1
    # Pipes
    for _ in range(random.randint(1, 4)):
        px = random.randint(6, TILES_X * 3 - 7)
        for py in range(TILES_Y - 5, TILES_Y - 2):
            level[py][px] = 4
            level[py - 1][px] = 4
    # Bricks and blocks
    for _ in range(18):
        bx = random.randint(4, TILES_X * 3 - 6)
        by = random.randint(4, TILES_Y - 7)
        level[by][bx] = random.choice([2, 3])
    # Coins
    for _ in range(18):
        cx = random.randint(4, TILES_X * 3 - 6)
        cy = random.randint(2, TILES_Y - 10)
        level[cy][cx] = 5
    # Flag at far right
    level[3][TILES_X * 3 - 3] = 6
    return level

def draw_level(level, camera_x):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            sx = x * TILE - camera_x
            sy = y * TILE
            if sx < -TILE or sx > WIDTH: continue
            if tile == 1:  # Ground
                pygame.draw.rect(screen, GROUND, (sx, sy, TILE, TILE))
            elif tile == 2:  # Brick
                pygame.draw.rect(screen, BRICK, (sx, sy, TILE, TILE))
                pygame.draw.rect(screen, BLACK, (sx+2, sy+2, TILE-4, TILE-4), 1)
            elif tile == 3:  # Block
                pygame.draw.rect(screen, BLOCK, (sx, sy, TILE, TILE))
                pygame.draw.rect(screen, WHITE, (sx+5, sy+5, 6, 6))
            elif tile == 4:  # Pipe
                pygame.draw.rect(screen, PIPE, (sx, sy, TILE, TILE*2))
                pygame.draw.rect(screen, WHITE, (sx, sy, TILE, 3))
            elif tile == 5:  # Coin
                pygame.draw.circle(screen, COIN, (sx+TILE//2, sy+TILE//2), TILE//4)
            elif tile == 6:  # Flag
                pygame.draw.rect(screen, FLAG, (sx+TILE//2-1, sy, 3, TILE*7))
                pygame.draw.rect(screen, WHITE, (sx+TILE//2+3, sy, 10, 10))

def draw_mario(mx, my, flicker=0):
    # Blocky Mario: body/head/hat/eye
    color = MARIO if flicker % 8 < 5 else (180,30,30)  # Simple flicker every ~.13s
    pygame.draw.rect(screen, color, (mx, my, TILE, TILE))  # Body
    pygame.draw.rect(screen, SKIN, (mx+3, my-7, 10, 7))  # Head
    pygame.draw.rect(screen, BLACK, (mx+9, my-4, 2, 2))  # Eye
    pygame.draw.rect(screen, color, (mx+3, my-7, 10, 3))  # Hat

def menu_screen(selected_level):
    screen.fill(SKY)
    title = bigfont.render("NES MARIO CLONE", True, MARIO)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))
    info = font.render("ARROWS = Level  ENTER = Play  ESC = Quit", True, WHITE)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, 120))
    levtxt = font.render(f"WORLD {selected_level+1:02}", True, COIN)
    screen.blit(levtxt, (WIDTH//2 - levtxt.get_width()//2, 180))
    scanlines()
    pygame.display.flip()

def level_start_screen(levelnum):
    screen.fill(BLACK)
    msg = bigfont.render(f"WORLD {levelnum+1:02}", True, WHITE)
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2-40))
    msg2 = font.render("GET READY!", True, GRAY)
    screen.blit(msg2, (WIDTH//2 - msg2.get_width()//2, HEIGHT//2))
    pygame.display.flip()
    pygame.time.wait(1000)

def game_over_screen():
    screen.fill(BLACK)
    msg = bigfont.render("GAME OVER", True, (255,64,64))
    screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2-20))
    pygame.display.flip()
    pygame.time.wait(1500)

def main():
    selected_level = 0
    lives = 3
    while True:
        # --- Main Menu ---
        menu = True
        while menu:
            menu_screen(selected_level)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    elif event.key == pygame.K_LEFT:
                        selected_level = (selected_level - 1) % LEVEL_COUNT
                    elif event.key == pygame.K_RIGHT:
                        selected_level = (selected_level + 1) % LEVEL_COUNT
                    elif event.key == pygame.K_RETURN:
                        menu = False

        # --- Start Level ---
        level_start_screen(selected_level)
        level = make_level(selected_level)
        mx, my = 40, HEIGHT - 3 * TILE
        vx, vy = 0, 0
        speed = 3
        jump = 8.5
        gravity = 0.5
        on_ground = False
        coins = 0
        camera_x = 0
        level_w_px = len(level[0]) * TILE
        win = False
        timer = 999
        timer_counter = 0
        flicker = 0
        while True:
            clock.tick(FPS)
            flicker += 1
            screen.fill(SKY)
            # Input
            keys = pygame.key.get_pressed()
            vx = 0
            if keys[pygame.K_LEFT]: vx = -speed
            if keys[pygame.K_RIGHT]: vx = speed
            if keys[pygame.K_SPACE] and on_ground:
                vy = -jump
                on_ground = False
            vy += gravity
            mx += vx
            my += vy
            # Camera
            camera_x = max(0, min(mx - WIDTH // 3, level_w_px - WIDTH))
            # Bounds
            if mx < 0: mx = 0
            if mx > level_w_px - TILE: mx = level_w_px - TILE
            if my > HEIGHT:
                lives -= 1
                if lives == 0:
                    game_over_screen()
                    lives = 3
                    break
                else:
                    level_start_screen(selected_level)
                    mx, my, vx, vy = 40, HEIGHT - 3 * TILE, 0, 0
                    continue
            # Collisions
            on_ground = False
            mario_rect = pygame.Rect(mx, my, TILE, TILE)
            for y, row in enumerate(level):
                for x, t in enumerate(row):
                    if t in [1, 2, 3, 4]:
                        block = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                        if mario_rect.colliderect(block):
                            if vy > 0:
                                my = block.top - TILE
                                vy = 0
                                on_ground = True
                            elif vy < 0:
                                my = block.bottom
                                vy = 1
            # Coin
            for y, row in enumerate(level):
                for x, t in enumerate(row):
                    if t == 5:
                        coin_rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                        if mario_rect.colliderect(coin_rect):
                            level[y][x] = 0
                            coins += 1
            # Flag
            for y, row in enumerate(level):
                for x, t in enumerate(row):
                    if t == 6:
                        flag_rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE * 7)
                        if mario_rect.colliderect(flag_rect):
                            win = True
            # Timer
            timer_counter += 1
            if timer_counter >= FPS:
                timer -= 1
                timer_counter = 0
                if timer == 0:
                    lives -= 1
                    if lives == 0:
                        game_over_screen()
                        lives = 3
                        break
                    else:
                        level_start_screen(selected_level)
                        mx, my, vx, vy, timer = 40, HEIGHT - 3 * TILE, 0, 0, 999
                        continue

            # Draw
            draw_level(level, camera_x)
            draw_mario(mx - camera_x, my, flicker)
            nes_hud(lives, coins, selected_level, timer)
            scanlines()
            if win:
                msg = bigfont.render("LEVEL CLEAR!", True, COIN)
                screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 140))
                pygame.display.flip()
                pygame.time.wait(1200)
                break
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        break
            else:
                continue
            break

if __name__ == "__main__":
    main()

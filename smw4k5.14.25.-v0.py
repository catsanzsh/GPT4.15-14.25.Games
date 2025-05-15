import pygame, random

# --- CORE CONSTANTS ---
WIDTH, HEIGHT = 600, 400
TILE = 32
FPS = 60

# --- COLORS ---
COL = dict(
    white=(255,255,255), black=(0,0,0), red=(220,50,50), green=(60,220,60), blue=(50,90,220), yellow=(240,220,70),
    brown=(170,100,40), sky=(110,180,240), gray=(120,120,120), gold=(240,220,70), orange=(220,120,30),
    darkgreen=(20,100,20), darkred=(150,20,30)
)

# --- CORE ENGINE CLASSES ---

class Entity:
    def __init__(self, x, y, w, h, color):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.vx, self.vy = 0, 0
        self.color = color
        self.on_ground = False
        self.active = True
    def rect(self): return pygame.Rect(self.x, self.y, self.w, self.h)
    def update(self, state): pass
    def draw(self, surf): pygame.draw.rect(surf, self.color, self.rect())

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 32, COL["red"])
        self.power = "small" # 'small', 'big', 'cape', 'fire'
        self.lives, self.score, self.coins = 5, 0, 0
        self.yoshi = None
        self.state = "idle" # walking, jumping, spin, swimming, riding
        self.invincible = 0
        self.carrying = None
        self.keys = []
        # SNES-like movement
        self.accel = 0.18   # acceleration
        self.max_speed = 2.4  # top speed
        self.friction = 0.12  # slide
        self.jump_power = -7
        self.gravity = 0.27
    def handle_input(self, keys):
        # SNES: acceleration and friction
        if keys[pygame.K_LEFT]:
            self.vx -= self.accel
        elif keys[pygame.K_RIGHT]:
            self.vx += self.accel
        else:
            if self.vx > 0:
                self.vx -= self.friction
                if self.vx < 0: self.vx = 0
            elif self.vx < 0:
                self.vx += self.friction
                if self.vx > 0: self.vx = 0
        # Clamp speed
        if self.vx > self.max_speed: self.vx = self.max_speed
        if self.vx < -self.max_speed: self.vx = -self.max_speed
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = self.jump_power
        if keys[pygame.K_LSHIFT]:
            self.state = "spin"
    def update(self, state):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        if self.x < 0: self.x = 0
        if self.x > WIDTH-self.w: self.x = WIDTH-self.w
        self.on_ground = False
        rect = self.rect()
        for plat in state.level.platforms:
            if rect.colliderect(plat.rect()):
                if self.vy > 0 and rect.bottom - plat.rect().top < 12:
                    self.y = plat.rect().top - self.h
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:
                    self.vy = 0
        if self.yoshi: self.yoshi.x, self.yoshi.y = self.x, self.y+24

class Yoshi(Entity):
    def __init__(self, x, y): super().__init__(x, y, 36, 28, COL["green"])
    def update(self, state): pass

class Enemy(Entity):
    def __init__(self, x, y, kind="goomba"):
        color = COL["brown"] if kind=="goomba" else COL["green"]
        super().__init__(x, y, 24, 24, color)
        self.kind = kind
    def update(self, state): self.x += (-1 if self.kind=="goomba" else 1)

class Platform(Entity):
    def __init__(self, x, y, w, h): super().__init__(x, y, w, h, COL["brown"])
    def update(self, state): pass

class Block(Entity):
    def __init__(self, x, y, block_type="coin"):
        color = COL["gold"] if block_type=="coin" else COL["gray"]
        super().__init__(x, y, TILE, TILE, color)
        self.block_type = block_type
    def update(self, state): pass

class Pipe(Entity):
    def __init__(self, x, y, vert=True): super().__init__(x, y, TILE, TILE*2 if vert else TILE, COL["green"])
    def update(self, state): pass

class Switch(Entity):
    def __init__(self, x, y, color): super().__init__(x, y, TILE, TILE/2, COL[color])
    def update(self, state): pass

class PowerUp(Entity):
    def __init__(self, x, y, ptype): super().__init__(x, y, 20, 20, COL["orange"])
    def update(self, state): pass

class Flag(Entity):
    def __init__(self, x, y): super().__init__(x, y, 16, 32, COL["yellow"])
    def update(self, state): pass

# --- OVERWORLD/MAP STUB ---
class Overworld:
    def __init__(self):
        self.map_nodes = [(i*60+30, HEIGHT//2+random.randint(-40,40)) for i in range(8)] # node x, y
        self.player_pos = 0
        self.move_delay = 0  # Cooldown for move
        self.move_cooldown = 0.15  # 150 ms between moves
    def draw(self, surf):
        for i, (x, y) in enumerate(self.map_nodes):
            pygame.draw.circle(surf, COL["green"], (x, y), 16)
            if i > 0:
                px, py = self.map_nodes[i-1]
                pygame.draw.line(surf, COL["gray"], (px, py), (x, y), 5)
        # Map Mario
        x, y = self.map_nodes[self.player_pos]
        pygame.draw.circle(surf, COL["red"], (x, y), 12)

    def move(self, d, dt):
        if self.move_delay <= 0:
            self.player_pos = max(0, min(len(self.map_nodes)-1, self.player_pos+d))
            self.move_delay = self.move_cooldown
        # dt will be decremented in game loop

# --- LEVEL GENERATOR STUB ---
class Level:
    def __init__(self, world=1, level=1):
        self.platforms = [Platform(x*TILE, HEIGHT-40, TILE, 12) for x in range(20)]
        self.platforms += [Platform(120, 220, 80, 12), Platform(320, 170, 80, 12)]
        self.enemies = [Enemy(260, HEIGHT-72)]
        self.items = [Block(160, 160), Block(190, 160, "powerup")]
        self.flag = Flag(540, HEIGHT-72)
        self.pipes = [Pipe(300, HEIGHT-72)]
        self.switches = [Switch(220, HEIGHT-52, "blue")]
        self.powerups = [PowerUp(192, 156, "mushroom")]
        self.yoshi = Yoshi(90, HEIGHT-72) if random.random() < 0.5 else None

    def draw(self, surf):
        for p in self.platforms: p.draw(surf)
        for e in self.enemies: e.draw(surf)
        for i in self.items: i.draw(surf)
        for pi in self.pipes: pi.draw(surf)
        for s in self.switches: s.draw(surf)
        for pu in self.powerups: pu.draw(surf)
        if self.yoshi: self.yoshi.draw(surf)
        self.flag.draw(surf)

# --- GAME STATE ---
class GameState:
    def __init__(self):
        self.scene = "overworld" # or "level"
        self.overworld = Overworld()
        self.level = Level()
        self.player = Player(60, HEIGHT-72)
    def switch_level(self):
        self.level = Level()
        self.player.x, self.player.y = 60, HEIGHT-72
        self.scene = "level"
    def back_to_overworld(self):
        self.scene = "overworld"

# --- GAME LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    state = GameState()
    running = True
    while running:
        dt = clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()
        # --- Update overworld move cooldown ---
        if state.scene == "overworld":
            if hasattr(state.overworld, "move_delay"):
                if state.overworld.move_delay > 0:
                    state.overworld.move_delay -= dt
                else:
                    state.overworld.move_delay = 0
        # --- SCENE SWITCH ---
        if state.scene == "overworld":
            if keys[pygame.K_RIGHT]: state.overworld.move(1, dt)
            if keys[pygame.K_LEFT]: state.overworld.move(-1, dt)
            if keys[pygame.K_RETURN]: state.switch_level()
        elif state.scene == "level":
            state.player.handle_input(keys)
            state.player.update(state)
            for e in state.level.enemies: e.update(state)
            if state.level.yoshi: state.level.yoshi.update(state)
            # Finish/Death
            if state.player.rect().colliderect(state.level.flag.rect()):
                state.back_to_overworld()
            if state.player.y > HEIGHT:
                state.player.lives -= 1
                if state.player.lives <= 0:
                    state.player.lives = 5
                state.player.x, state.player.y = 60, HEIGHT-72
        # --- DRAW ---
        screen.fill(COL["sky"])
        if state.scene == "overworld":
            state.overworld.draw(screen)
            txt = font.render("Map: ←/→ move, Enter=Play Level", True, COL["black"])
            screen.blit(txt, (10, 10))
        elif state.scene == "level":
            state.level.draw(screen)
            state.player.draw(screen)
            txt = font.render(f"Lives: {state.player.lives} Coins: {state.player.coins} Power: {state.player.power}", True, COL["black"])
            screen.blit(txt, (10, 10))
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()

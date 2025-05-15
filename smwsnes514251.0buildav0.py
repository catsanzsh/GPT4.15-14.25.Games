import pygame
import sys

WIDTH, HEIGHT, TILE, FPS = 640, 400, 32, 60
FIX = 256

COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (220, 50, 50),
    'GREEN': (60, 220, 60),
    'BLUE': (50, 90, 220),
    'YELLOW': (240, 220, 70),
    'BROWN': (170, 100, 40),
    'SKY': (110, 180, 240),
    'GRAY': (120, 120, 120),
    'ORANGE': (220, 120, 30),
    'PURPLE': (120, 60, 180)
}

SMW_MAP = [
    {
        'name': "Yoshi's Island",
        'nodes': [
            {'pos': (80, 220), 'level': (1, 1), 'label': "YI 1"},
            {'pos': (180, 200), 'level': (1, 2), 'label': "YI 2"},
            {'pos': (300, 220), 'level': (1, 3), 'label': "YI 3"},
            {'pos': (420, 200), 'level': (1, 4), 'label': "YI 4"},
            {'pos': (540, 220), 'level': (1, 5), 'label': "Castle"},
        ]
    },
    {
        'name': 'Donut Plains',
        'nodes': [
            {'pos': (80, 100), 'level': (2, 1), 'label': "DP 1"},
            {'pos': (180, 120), 'level': (2, 2), 'label': "DP 2"},
            {'pos': (300, 90),  'level': (2, 3), 'label': "DP 3"},
            {'pos': (420, 110), 'level': (2, 4), 'label': "DP 4"},
            {'pos': (540, 100), 'level': (2, 5), 'label': "Castle"},
        ]
    }
]

def simple_level():
    return {
        'platforms': [(0, HEIGHT-40, WIDTH, 12)],
        'enemies': [],
        'items': [],
        'flag': (580, HEIGHT-72),
        'pipes': [],
        'switches': [],
        'powerups': [],
        'yoshi': None
    }

SMW_LEVELS = {
    (1, 1): {
        'platforms': [(0, HEIGHT-40, WIDTH, 12), (120, 220, 80, 12)],
        'enemies': [(260, HEIGHT-72, 'goomba')],
        'items': [(160, 160, 'coin')],
        'flag': (580, HEIGHT-72),
        'pipes': [],
        'switches': [],
        'powerups': [],
        'yoshi': None
    },
    (1, 2): simple_level(),
    (1, 3): simple_level(),
    (1, 4): simple_level(),
    (1, 5): simple_level(),  # Castle
    (2, 1): simple_level(),
    (2, 2): simple_level(),
    (2, 3): simple_level(),
    (2, 4): simple_level(),
    (2, 5): simple_level(),  # Castle
}

class Entity:
    __slots__ = ('x', 'y', 'w', 'h', 'vx', 'vy', 'color', 'on_ground')
    def __init__(self, x, y, w, h, color):
        self.x = x * FIX
        self.y = y * FIX
        self.vx = 0
        self.vy = 0
        self.w = w
        self.h = h
        self.color = color
        self.on_ground = False
    def rect(self):
        return pygame.Rect(self.x // FIX, self.y // FIX, self.w, self.h)
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect())

class RectEntity(Entity):
    def __init__(self, x, y, w, h, color):
        super().__init__(x, y, w, h, color)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 24, 32, COLORS['RED'])
        self.lives = 5
        self.coins = 0
        self.accel = int(0.18 * FIX)
        self.fric = int(0.12 * FIX)
        self.max_vx = int(2.4 * FIX)
        self.jump_v = int(-7 * FIX)
        self.gravity = int(0.27 * FIX)
    def handle_input(self, keys):
        ax = 0
        if keys[pygame.K_LEFT]: ax = -self.accel
        if keys[pygame.K_RIGHT]: ax = self.accel
        self.vx += ax
        if ax == 0:
            if self.vx > 0: self.vx = max(0, self.vx - self.fric)
            else: self.vx = min(0, self.vx + self.fric)
        self.vx = max(-self.max_vx, min(self.max_vx, self.vx))
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vy = self.jump_v
    def update_physics(self, platforms):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy
        self.on_ground = False
        rect = self.rect()
        for p in platforms:
            pr = p.rect()
            if rect.colliderect(pr):
                if self.vy > 0 and rect.bottom - pr.top < FIX:
                    self.y = (pr.top - self.h) * FIX
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0 and pr.bottom - rect.top < FIX:
                    self.y = pr.bottom * FIX
                    self.vy = 0

class Overworld:
    def __init__(self, map_data):
        self.map_data = map_data
        self.world = 0
        self.node = 0
        self.delay = 0
        self.cooldown = 0.15
    def draw(self, surface, font):
        nodes = self.map_data[self.world]['nodes']
        for i, n in enumerate(nodes):
            color = COLORS['GREEN']
            radius = 16 if i != self.node else 12
            pygame.draw.circle(surface, color, n['pos'], radius)
            label = n.get('label', str(i+1))
            text = font.render(label, True, COLORS['BLACK'])
            t_rect = text.get_rect(center=(n['pos'][0], n['pos'][1] - 20))
            surface.blit(text, t_rect)
            if i > 0:
                pygame.draw.line(surface, COLORS['GRAY'], nodes[i-1]['pos'], n['pos'], 5)
        name = self.map_data[self.world]['name']
        surface.blit(font.render(name, True, COLORS['BLACK']), (WIDTH//2 - 80, 20))
    def move_node(self, d):
        if self.delay <= 0:
            max_node = len(self.map_data[self.world]['nodes']) - 1
            self.node = max(0, min(max_node, self.node + d))
            self.delay = self.cooldown
    def switch_world(self, d):
        new_world = self.world + d
        if 0 <= new_world < len(self.map_data):
            self.world = new_world
            self.node = 0

class Level:
    def __init__(self, level_data):
        self.platforms = [RectEntity(x, y, w, h, COLORS['BROWN'])
                          for x, y, w, h in level_data['platforms']]
        self.enemies = [RectEntity(x, y, 24, 24, COLORS['BROWN'])
                        for x, y, _ in level_data['enemies']]
        fx, fy = level_data['flag']
        self.flag = RectEntity(fx, fy, 16, 32, COLORS['YELLOW'])
    def draw(self, surface):
        for e in self.platforms + self.enemies:
            e.draw(surface)
        self.flag.draw(surface)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    overworld = Overworld(SMW_MAP)
    player = Player(60, HEIGHT - 72)
    current_level = None
    state = 'overworld'
    while True:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if state == 'overworld':
            overworld.delay = max(0, overworld.delay - dt)
            if keys[pygame.K_UP]: overworld.switch_world(-1)
            if keys[pygame.K_DOWN]: overworld.switch_world(1)
            if keys[pygame.K_LEFT]: overworld.move_node(-1)
            if keys[pygame.K_RIGHT]: overworld.move_node(1)
            if keys[pygame.K_RETURN]:
                w, n = overworld.map_data[overworld.world]['nodes'][overworld.node]['level']
                current_level = Level(SMW_LEVELS[(w, n)])
                player = Player(60, HEIGHT - 72)
                state = 'level'
        else:
            player.handle_input(keys)
            player.update_physics(current_level.platforms)
            if player.rect().top > HEIGHT:
                player.lives = max(0, player.lives - 1)
                player = Player(60, HEIGHT - 72)
            if player.rect().colliderect(current_level.flag.rect()):
                state = 'overworld'
        screen.fill(COLORS['SKY'])
        if state == 'overworld':
            overworld.draw(screen, font)
        else:
            current_level.draw(screen)
            player.draw(screen)
            screen.blit(font.render(f"Lives: {player.lives}", True, COLORS['BLACK']), (10, 10))
        pygame.display.flip()

if __name__ == '__main__':
    main()

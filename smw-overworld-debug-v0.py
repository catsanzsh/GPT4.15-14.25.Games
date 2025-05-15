import pygame, sys, random

# -------------------------------------------------------------
#  CONSTANTS & GLOBALS (SNES‑style fixed‑point, no PNG assets)
# -------------------------------------------------------------
WIDTH, HEIGHT, TILE, FPS = 640, 400, 32, 60
FIX = 256                              # 8‑bit fractional fixed‑point (1px = 256)

COL = dict(
    white=(255,255,255), black=(0,0,0), red=(220,50,50), green=(60,220,60), blue=(50,90,220), yellow=(240,220,70),
    brown=(170,100,40), sky=(110,180,240), gray=(120,120,120), gold=(240,220,70), orange=(220,120,30),
    darkgreen=(20,100,20), darkred=(150,20,30), purple=(120,60,180)
)

# -------------------------------------------------------------
#  MAP & LEVEL DATA  (unchanged from user source, rectangles only)
# -------------------------------------------------------------
SMW_MAP = [
    {"name": "Yoshi's Island", "nodes": [
        {"pos": (80, 220), "level": (1,1)},
        {"pos": (180, 200), "level": (1,2)},
        {"pos": (300, 220), "level": (1,3)},
        {"pos": (420, 200), "level": (1,4)},
        {"pos": (540, 220), "level": (1,5)},
    ]},
    {"name": "Donut Plains", "nodes": [
        {"pos": (80, 100), "level": (2,1)},
        {"pos": (180, 120), "level": (2,2)},
        {"pos": (300, 90),  "level": (2,3)},
        {"pos": (420, 110), "level": (2,4)},
        {"pos": (540, 100), "level": (2,5)},
    ]},
]

SMW_LEVELS = {
    (1,1): {
        "platforms": [(0, HEIGHT-40, WIDTH, 12), (120, 220, 80, 12), (320, 170, 80, 12)],
        "enemies": [(260, HEIGHT-72, "goomba")],
        "items": [(160, 160, "coin"), (190, 160, "powerup")],
        "flag": (580, HEIGHT-72),
        "pipes": [(300, HEIGHT-72, True)],
        "switches": [(220, HEIGHT-52, "blue")],
        "powerups": [(192, 156, "mushroom")],
        "yoshi": (90, HEIGHT-72)
    },
    (1,2): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (200, 160, 100, 12)],
             "enemies": [(350, HEIGHT-72, "goomba"), (400, 140, "koopa")],
             "items": [(240, 120, "coin")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": None
    },
    (1,3): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (300, 120, 120, 12), (500, 70, 80, 12)],
             "enemies": [(400, HEIGHT-72, "koopa")],
             "items": [(320, 100, "powerup")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [(325, 90, "mushroom")], "yoshi": None
    },
    (1,4): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (220, 190, 80, 12), (400, 110, 70, 12)],
             "enemies": [(420, HEIGHT-72, "goomba")],
             "items": [(270, 170, "coin")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": (100, HEIGHT-72)
    },
    (1,5): {"platforms": [(0, HEIGHT-40, WIDTH, 12)],
             "enemies": [(450, HEIGHT-72, "koopa")],
             "items": [], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": None
    },
    (2,1): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (200, 130, 100, 12), (400, 80, 80, 12)],
             "enemies": [(280, HEIGHT-72, "goomba")],
             "items": [(210, 110, "coin")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": None
    },
    (2,2): {"platforms": [(0, HEIGHT-40, WIDTH, 12)],
             "enemies": [(360, HEIGHT-72, "koopa")],
             "items": [(230, 130, "coin")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": (100, HEIGHT-72)
    },
    (2,3): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (400, 60, 100, 12)],
             "enemies": [(420, 38, "goomba")], "items": [], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": None
    },
    (2,4): {"platforms": [(0, HEIGHT-40, WIDTH, 12), (150, 110, 200, 12)],
             "enemies": [], "items": [(180, 90, "powerup")], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [(200, HEIGHT-52, "purple")], "powerups": [], "yoshi": None
    },
    (2,5): {"platforms": [(0, HEIGHT-40, WIDTH, 12)],
             "enemies": [(560, HEIGHT-72, "koopa")], "items": [], "flag": (580, HEIGHT-72),
             "pipes": [], "switches": [], "powerups": [], "yoshi": (90, HEIGHT-72)
    }
}

# -------------------------------------------------------------
#  CORE FIXED-POINT ENTITY & HELPERS
# -------------------------------------------------------------
class Ent:
    __slots__ = ("x","y","w","h","vx","vy","col","on_ground")
    def __init__(s, x, y, w, h, col):
        s.x, s.y = x * FIX, y * FIX
        s.vx = s.vy = 0
        s.w, s.h = w, h
        s.col = col
        s.on_ground = False
    def R(s): return pygame.Rect(s.x // FIX, s.y // FIX, s.w, s.h)
    def draw(s, surf): surf.fill(s.col, s.R())

class RectEnt:
    __slots__ = ("_rect","col")
    def __init__(s, x, y, w, h, col):
        s._rect = pygame.Rect(x, y, w, h)
        s.col = col
    def R(s): return s._rect
    def draw(s, surf): surf.fill(s.col, s._rect)

# -------------------------------------------------------------
#  ACTORS: Player, Enemy, etc.
# -------------------------------------------------------------
class Player(Ent):
    __slots__ = Ent.__slots__ + ("lives","coins","accel","fric","max_vx","jump_v","grav")
    def __init__(s, x, y):
        super().__init__(x, y, 24, 32, COL['red'])
        s.lives, s.coins = 5, 0
        s.accel = int(0.18 * FIX)
        s.fric  = int(0.12 * FIX)
        s.max_vx = int(2.4 * FIX)
        s.jump_v = int(-7 * FIX)
        s.grav   = int(0.27 * FIX)
    def handle_input(s, k):
        ax = 0
        if k[pygame.K_LEFT]:  ax = -s.accel
        if k[pygame.K_RIGHT]: ax = s.accel
        s.vx += ax
        if ax == 0:
            if s.vx > 0: s.vx = max(0, s.vx - s.fric)
            elif s.vx < 0: s.vx = min(0, s.vx + s.fric)
        s.vx = max(-s.max_vx, min(s.max_vx, s.vx))
        if k[pygame.K_SPACE] and s.on_ground: s.vy = s.jump_v
    def physics(s, plats):
        s.vy += s.grav
        s.x += s.vx; s.y += s.vy
        if s.x < 0: s.x = 0
        if s.x > (WIDTH - s.w) * FIX: s.x = (WIDTH - s.w) * FIX
        s.on_ground = False
        Rct = s.R()
        for p in plats:
            pr = p.R()
            if Rct.colliderect(pr):
                if s.vy > 0 and Rct.bottom - pr.top < 16:
                    s.y = (pr.top - s.h) * FIX
                    s.vy = 0; s.on_ground = True
                elif s.vy < 0 and pr.bottom - Rct.top < 16:
                    s.y = pr.bottom * FIX; s.vy = 0

class Enemy(RectEnt): pass

# -------------------------------------------------------------
#  OVERWORLD & LEVEL LOADER
# -------------------------------------------------------------
class Overworld:
    __slots__ = ("smw_map","world","node","move_delay","move_cooldown")
    def __init__(s, smw_map):
        s.smw_map = smw_map; s.world = 0; s.node = 0
        s.move_delay = 0; s.move_cooldown = 0.15
    def draw(s, surf, font):
        nodes = s.smw_map[s.world]['nodes']
        for i, n in enumerate(nodes):
            pygame.draw.circle(surf, COL['green'], n['pos'], 16)
            if i>0: pygame.draw.line(surf, COL['gray'], nodes[i-1]['pos'], n['pos'], 5)
        pygame.draw.circle(surf, COL['red'], nodes[s.node]['pos'], 12)
        surf.blit(font.render(s.smw_map[s.world]['name'], True, COL['black']), (WIDTH//2-80, 20))
    def move(s, d):
        if s.move_delay <=0:
            s.node = max(0, min(len(s.smw_map[s.world]['nodes'])-1, s.node + d))
            s.move_delay = s.move_cooldown
    def switch_world(s, d):
        w = s.world + d
        if 0<=w<len(s.smw_map): s.world, s.node = w,0

class Level:
    __slots__ = ("plats","enemies","flag")
    def __init__(s, data):
        s.plats   = [RectEnt(*p, COL['brown']) for p in data['platforms']]
        s.enemies = [RectEnt(x,y,24,24,COL['brown']) for x,y,_ in data['enemies']]
        fx, fy = data['flag']; s.flag = RectEnt(fx, fy, 16, 32, COL['yellow'])
    def draw(s, surf):
        surf.blits([(e.col, e.R()) for e in s.plats+s.enemies])
        s.flag.draw(surf)

# -------------------------------------------------------------
#  GAME STATE & LOOP
# -------------------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    state = 'overworld'
    ow = Overworld(SMW_MAP)
    player = Player(60, HEIGHT-72)
    level = None

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        keys = pygame.key.get_pressed()

        if state == 'overworld':
            if ow.move_delay>0: ow.move_delay -= clock.get_time()/1000.0
            if keys[pygame.K_UP]: ow.switch_world(-1)
            if keys[pygame.K_DOWN]: ow.switch_world(1)
            if keys[pygame.K_RIGHT]: ow.move(1)
            if keys[pygame.K_LEFT]: ow.move(-1)
            if keys[pygame.K_RETURN]:
                w,n = ow.smw_map[ow.world]['nodes'][ow.node]['level']
                level = Level(SMW_LEVELS[(w,n)])
                player.x, player.y = 60*FIX, (HEIGHT-72)*FIX
                state = 'level'

        elif state == 'level':
            player.handle_input(keys)
            player.physics(level.plats)
            if player.y//FIX > HEIGHT:
                player.x, player.y = 60*FIX, (HEIGHT-72)*FIX; player.lives -= 1
                if player.lives<0: player.lives = 5
            if player.R().colliderect(level.flag.R()): state = 'overworld'

        screen.fill(COL['sky'])
        if state == 'overworld':
            ow.draw(screen, font)
            screen.blit(font.render("World: ↑/↓ Node: ←/→ Enter=Play", True, COL['black']), (10,10))
        else:
            level.draw(screen); player.draw(screen)
            screen.blit(font.render(f"Lives:{player.lives}", True, COL['black']), (10,10))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__": main()

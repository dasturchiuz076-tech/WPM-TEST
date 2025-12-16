import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Tuple
import os
pygame.init()
pygame.mixer.init()

# ----- SCREEN & FULLSCREEN -----
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Arkanoid | Ultimate Edition - Dasturchi Uz")

FPS = 60

# ----- COLORS -----
BG = (30, 30, 30)
BG2 = (40, 40, 60)
PADDLE_COLOR = (200, 200, 255)
BALL_COLOR = (255, 165, 0)
BRICK_COLOR = (230, 200, 80)
BRICK_HIT_COLOR = (200, 120, 40)
POWERUP_COLOR = (100, 255, 100)
OBSTACLE_COLOR = (120, 120, 120)
TEXT_COLOR = (240, 240, 240)
MENU_BG = (20, 20, 60)
POWERUP_TEXT_COLOR = (255, 255, 50)
LASER_COLOR = (255, 50, 50)
SHIELD_COLOR = (100, 200, 255)
MAGNET_COLOR = (255, 100, 255)
COMBO_COLOR = (255, 215, 0)
BOSS_COLOR = (200, 50, 50)

# Yangi ranglar
RAINBOW_BRICK = [(255,0,0), (255,127,0), (255,255,0), (0,255,0), (0,0,255), (75,0,130), (148,0,211)]
MOVING_BRICK_COLOR = (150, 100, 200)
EXPLOSIVE_BRICK_COLOR = (255, 100, 0)

FONT = pygame.font.SysFont("Arial", 20)
BIG = pygame.font.SysFont("Arial", 48)
HUGE = pygame.font.SysFont("Arial", 96)
SMALL = pygame.font.SysFont("Arial", 16)

# ----- SOUNDS -----
try:
    start_sound = pygame.mixer.Sound("start.ogg")
    ball_sound = pygame.mixer.Sound("ball_loop.ogg")
    game_over_sound = pygame.mixer.Sound("gameover.ogg")
except:
    start_sound = ball_sound = game_over_sound = None

# ----- PARTICLE SYSTEM -----
@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    color: Tuple[int, int, int]
    size: int = 3
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.life -= 1
        
    def draw(self, surf):
        if self.life > 0:
            alpha = min(255, int(255 * (self.life / 30)))
            # RGBA rangini yaratish
            rgba = (self.color[0], self.color[1], self.color[2], alpha)
            # Alohida surface yaratish
            s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, rgba, (self.size, self.size), self.size)
            surf.blit(s, (int(self.x - self.size), int(self.y - self.size)))

def create_explosion(x, y, color, count=20):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        particles.append(Particle(x, y, math.cos(angle) * speed, math.sin(angle) * speed,
                                random.randint(20, 40), color, random.randint(2, 5)))
    return particles

# ----- BACKGROUND STARS -----
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(150, 255)
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self, surf):
        pygame.draw.circle(surf, (self.brightness, self.brightness, self.brightness), 
                         (int(self.x), int(self.y)), self.size)

# ----- GAME OBJECTS -----
class Paddle:
    def __init__(self, x, y, w=120, h=12, speed=7):
        self.rect = pygame.Rect(x, y, w, h)
        self.speed = speed
        self.color = PADDLE_COLOR
        self.has_laser = False
        self.has_shield = False
        self.has_magnet = False
        self.laser_timer = 0
        self.shield_timer = 0
        self.magnet_timer = 0
        self.laser_cooldown = 0
        
    def move(self, dir, dt=1):
        self.rect.x += dir * self.speed * dt
        self.rect.x = max(0, min(WIDTH - self.rect.w, self.rect.x))
        
    def update(self):
        if self.laser_timer > 0:
            self.laser_timer -= 1
            if self.laser_timer == 0: self.has_laser = False
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0: self.has_shield = False
        if self.magnet_timer > 0:
            self.magnet_timer -= 1
            if self.magnet_timer == 0: self.has_magnet = False
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1

    def draw(self, surf):
        if self.has_shield:
            pygame.draw.ellipse(surf, SHIELD_COLOR, 
                              (self.rect.x - 10, self.rect.y - 20, self.rect.w + 20, 50), 3)
        color = self.color
        if self.has_laser: color = LASER_COLOR
        elif self.has_magnet: color = MAGNET_COLOR
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        if self.has_laser:
            pygame.draw.rect(surf, (255, 0, 0), (self.rect.left + 5, self.rect.top - 5, 4, 8))
            pygame.draw.rect(surf, (255, 0, 0), (self.rect.right - 9, self.rect.top - 5, 4, 8))
    
    def shoot_laser(self):
        if self.has_laser and self.laser_cooldown == 0:
            self.laser_cooldown = 15
            return [Laser(self.rect.left + 7, self.rect.top), Laser(self.rect.right - 7, self.rect.top)]
        return []

class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.alive = True
        self.w = 3
        self.h = 15
        
    @property
    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y, self.w, self.h)
        
    def update(self):
        self.y -= self.speed
        if self.y < -20: self.alive = False
            
    def draw(self, surf):
        pygame.draw.rect(surf, LASER_COLOR, self.rect)
        pygame.draw.rect(surf, (255, 255, 0), self.rect, 1)

class Ball:
    def __init__(self, x, y, vx=4, vy=-4, r=7):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.alive = True
        self.color = BALL_COLOR
        self.trail = []

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r*2, self.r*2)

    def update(self, dt=1):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5: self.trail.pop(0)
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.x - self.r <= 0:
            self.x = self.r
            self.vx *= -1
        if self.x + self.r >= WIDTH:
            self.x = WIDTH - self.r
            self.vx *= -1
        if self.y - self.r <= 0:
            self.y = self.r
            self.vy *= -1

    def draw(self, surf):
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(100 * (i / len(self.trail)))
            size = int(self.r * (0.3 + 0.7 * (i / len(self.trail))))
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (size, size), size)
            surf.blit(s, (int(tx - size), int(ty - size)))
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surf, (255,255,255), (int(self.x), int(self.y)), self.r, 1)
        glow = pygame.Surface((self.r*4, self.r*4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 50), (self.r*2, self.r*2), self.r*2)
        surf.blit(glow, (int(self.x - self.r*2), int(self.y - self.r*2)))

class Brick:
    def __init__(self, x, y, w, h, hits=1, obstacle=False, brick_type="normal"):
        self.rect = pygame.Rect(x, y, w, h)
        self.hits = hits
        self.max_hits = hits
        self.obstacle = obstacle
        self.base_color = BRICK_COLOR
        self.brick_type = brick_type
        self.move_dir = random.choice([-1, 1]) if brick_type == "moving" else 0
        self.move_speed = 1
        self.original_x = x
        self.move_range = 50
        self.color_index = 0
        self.animation_timer = 0
        
    def update(self):
        if self.brick_type == "moving":
            self.rect.x += self.move_dir * self.move_speed
            if abs(self.rect.x - self.original_x) > self.move_range:
                self.move_dir *= -1
        elif self.brick_type == "rainbow":
            self.animation_timer += 1
            if self.animation_timer >= 5:
                self.animation_timer = 0
                self.color_index = (self.color_index + 1) % len(RAINBOW_BRICK)

    def hit(self):
        if self.obstacle: return False
        self.hits -= 1
        return self.hits <= 0

    def draw(self, surf):
        if self.obstacle: color = OBSTACLE_COLOR
        elif self.brick_type == "moving": color = MOVING_BRICK_COLOR
        elif self.brick_type == "explosive": color = EXPLOSIVE_BRICK_COLOR
        elif self.brick_type == "rainbow": color = RAINBOW_BRICK[self.color_index]
        elif self.brick_type == "boss": color = BOSS_COLOR
        else:
            hit_ratio = self.hits / self.max_hits
            color = tuple(int(c * hit_ratio) for c in self.base_color)
        pygame.draw.rect(surf, color, self.rect)
        pygame.draw.rect(surf, (20,20,20), self.rect, 2)
        if self.hits > 1 and not self.obstacle:
            hit_text = SMALL.render(str(self.hits), True, (255, 255, 255))
            surf.blit(hit_text, (self.rect.centerx - hit_text.get_width()//2, 
                                self.rect.centery - hit_text.get_height()//2))

@dataclass
class PowerUp:
    x: float
    y: float
    kind: str
    vy: float = 2.5
    r: int = 10
    alive: bool = True
    color: tuple = POWERUP_COLOR
    rotation: float = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.r), int(self.y - self.r), self.r*2, self.r*2)

    def update(self):
        self.y += self.vy
        self.rotation += 5
        if self.y > HEIGHT + 50: self.alive = False

    def draw(self, surf):
        s = pygame.Surface((self.r*4, self.r*4), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, 100), (self.r*2, self.r*2), self.r*2)
        surf.blit(s, (int(self.x - self.r*2), int(self.y - self.r*2)))
        points = []
        for i in range(6):
            angle = math.radians(self.rotation + i * 60)
            px = self.x + math.cos(angle) * self.r
            py = self.y + math.sin(angle) * self.r
            points.append((px, py))
        pygame.draw.polygon(surf, self.color, points)
        lbl = SMALL.render(self.kind[:3], True, (10,10,10))
        surf.blit(lbl, (self.x - lbl.get_width()//2, self.y - lbl.get_height()//2))

# ----- COMBO SYSTEM -----
class ComboTracker:
    def __init__(self):
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.combo_multiplier = 1.0
        
    def hit(self):
        self.combo += 1
        self.combo_timer = 120
        if self.combo > self.max_combo: self.max_combo = self.combo
        self.combo_multiplier = 1.0 + (self.combo * 0.1)
        
    def update(self):
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo = 0
                self.combo_multiplier = 1.0
                
    def get_bonus(self):
        return int(100 * self.combo_multiplier)
    
    def draw(self, surf, x, y):
        if self.combo > 2:
            combo_text = FONT.render(f"COMBO x{self.combo}!", True, COMBO_COLOR)
            surf.blit(combo_text, (x, y))
            bar_w = 100
            bar_h = 5
            progress = self.combo_timer / 120
            pygame.draw.rect(surf, (50, 50, 50), (x, y + 25, bar_w, bar_h))
            pygame.draw.rect(surf, COMBO_COLOR, (x, y + 25, int(bar_w * progress), bar_h))

# ----- LEVEL GENERATOR -----
def generate_level(n):
    rows = 5 + n//10
    cols = 8 + n//5
    bricks = []
    margin_x = 60
    margin_y = 60
    total_w = WIDTH - 2*margin_x
    brick_w = total_w // cols - 4
    brick_h = 22
    gap = 4
    is_boss_level = (n % 10 == 0)
    
    for i in range(rows):
        for j in range(cols):
            x = margin_x + j*(brick_w + gap)
            y = margin_y + i*(brick_h + gap)
            if is_boss_level:
                hits = random.randint(3, 5)
                bricks.append(Brick(x, y, brick_w, brick_h, hits=hits, brick_type="boss"))
            else:
                choice = random.random()
                if choice < 0.03:
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=999, obstacle=True))
                elif choice < 0.1 and n > 3:
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=2, brick_type="moving"))
                elif choice < 0.15 and n > 5:
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=1, brick_type="explosive"))
                elif choice < 0.2 and n > 2:
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=1, brick_type="rainbow"))
                elif choice < 0.5:
                    hits = random.choice([1,2,3])
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=hits))
                else:
                    bricks.append(Brick(x, y, brick_w, brick_h, hits=1))
    return bricks

# ----- HELPERS -----
def reflect_ball_from_rect(ball, rect):
    dx = ball.x - rect.centerx
    dy = ball.y - rect.centery
    if abs(dx) > abs(dy): ball.vx *= -1
    else: ball.vy *= -1

def ball_paddle_collision(ball, paddle):
    if ball.rect.colliderect(paddle.rect):
        ball.y = paddle.rect.top - ball.r - 0.1
        ball.vy *= -1
        hit_pos = (ball.x - paddle.rect.left) / paddle.rect.w
        angle = (hit_pos - 0.5) * math.radians(120)
        speed = math.hypot(ball.vx, ball.vy)
        ball.vx = speed * math.sin(angle)
        ball.vy = -abs(speed * math.cos(angle))

def spawn_powerup(brick):
    if random.random() > 0.35 or brick.obstacle: return None
    kinds = ["x2","x3","slow","fast","bigpaddle","tinyball","laser","shield","magnet"]
    weights = [0.20, 0.15, 0.12, 0.12, 0.08, 0.05, 0.10, 0.10, 0.08]
    kind = random.choices(kinds, weights)[0]
    return PowerUp(brick.rect.centerx, brick.rect.centery, kind)

def multiply_balls(balls, factor):
    new_balls = []
    if factor <= 1: return
    current = list(balls)
    for _ in range(factor-1):
        duplicates = []
        for b in current:
            angle = math.atan2(b.vy,b.vx) + random.uniform(-0.4,0.4)
            speed = math.hypot(b.vx,b.vy)
            nb = Ball(b.x+random.uniform(-6,6), b.y+random.uniform(-6,6), 
                     speed*math.cos(angle), speed*math.sin(angle), r=b.r)
            duplicates.append(nb)
        new_balls.extend(duplicates)
        current = duplicates
    balls.extend(new_balls)

def load_record():
    try:
        with open("record.txt","r") as f: return int(f.read())
    except: return 0

def save_record(score):
    if score>load_record():
        with open("record.txt","w") as f: f.write(str(score))

def draw_center_text(surf,text,font,color=TEXT_COLOR):
    lbl = font.render(text,True,color)
    surf.blit(lbl,(WIDTH//2 - lbl.get_width()//2, HEIGHT//2 - lbl.get_height()//2))

# ----- BOSS ATTACK CLASSES -----
class BossBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8
        self.speed = 3
        self.color = (255, 50, 50)
        self.alive = True
        self.target_y = HEIGHT - 50
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT * 0.7:
            self.speed = 5
        if self.y > HEIGHT + 20:
            self.alive = False
            
    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (255, 200, 200), (int(self.x), int(self.y)), self.radius - 3)
        pygame.draw.line(surf, (255, 255, 255), 
                        (int(self.x - self.radius), int(self.y)),
                        (int(self.x + self.radius), int(self.y)), 2)
                        
    @property
    def rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)


class BossLaser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 15
        self.height = 0
        self.max_height = HEIGHT - 100
        self.growing = True
        self.alive = True
        self.timer = 180
        self.color1 = (255, 50, 50)
        self.color2 = (255, 200, 50)
        self.warning_timer = 60
        
    def update(self):
        if self.warning_timer > 0:
            self.warning_timer -= 1
            if self.warning_timer == 0:
                self.growing = True
        else:
            if self.growing:
                self.height += 10
                if self.height >= self.max_height:
                    self.growing = False
            else:
                self.timer -= 1
                if self.timer <= 0:
                    self.height -= 15
                    if self.height <= 0:
                        self.alive = False
                        
    def draw(self, surf):
        if self.warning_timer > 0:
            warning_alpha = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 150 + 50
            warning_surf = pygame.Surface((self.width, HEIGHT), pygame.SRCALPHA)
            for i in range(HEIGHT):
                alpha = int(warning_alpha * (1 - i/HEIGHT))
                color = (*self.color1[:3], alpha)
                pygame.draw.line(warning_surf, color, (0, i), (self.width, i))
            surf.blit(warning_surf, (self.x - self.width//2, 0))
            if self.warning_timer % 30 < 20:
                warn_text = FONT.render("LASER WARNING!", True, (255, 50, 50))
                surf.blit(warn_text, (self.x - warn_text.get_width()//2, 50))
        else:
            laser_rect = pygame.Rect(self.x - self.width//2, 0, self.width, self.height)
            pygame.draw.rect(surf, self.color1, laser_rect)
            for i in range(3):
                edge_rect = pygame.Rect(
                    laser_rect.x + i, 
                    laser_rect.y, 
                    laser_rect.width - i*2, 
                    laser_rect.height
                )
                color = (min(255, self.color2[0] + i*20), 
                        min(255, self.color2[1] + i*20), 
                        self.color2[2])
                pygame.draw.rect(surf, color, edge_rect, 1)
                
    @property
    def rect(self):
        if self.warning_timer > 0:
            return pygame.Rect(self.x - self.width//2, 0, self.width, HEIGHT)
        return pygame.Rect(self.x - self.width//2, 0, self.width, self.height)

# ----- BOSS CLASS -----
class Boss:
    def __init__(self, level):
        self.level = level
        self.width = min(400, 200 + level * 20)
        self.height = 40
        self.x = WIDTH//2 - self.width//2
        self.y = 100
        self.hp = 100 + level * 50
        self.max_hp = self.hp
        self.speed = 2 + level * 0.5
        self.direction = 1
        self.attack_timer = 0
        self.attacks = []
        self.invulnerable = False
        self.invuln_timer = 0
        
    def update(self):
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x + self.width >= WIDTH:
            self.direction *= -1
            
        self.attack_timer -= 1
        if self.attack_timer <= 0:
            self.launch_attack()
            self.attack_timer = random.randint(90, 180)
            
        if self.invulnerable:
            self.invuln_timer -= 1
            if self.invuln_timer <= 0:
                self.invulnerable = False
                
        for attack in self.attacks[:]:
            attack.update()
            if not attack.alive:
                self.attacks.remove(attack)
                
    def launch_attack(self):
        attack_type = random.choice(["bullet", "laser", "bullet", "bullet"])
        if attack_type == "bullet":
            self.attacks.append(BossBullet(self.x + self.width//2, self.y + self.height))
        elif attack_type == "laser":
            self.attacks.append(BossLaser(self.x + self.width//2, self.y + self.height))
            
    def draw(self, surf):
        pygame.draw.rect(surf, BOSS_COLOR, (self.x, self.y, self.width, self.height), border_radius=10)
        
        # Health bar
        bar_width = self.width - 20
        bar_height = 8
        bar_x = self.x + 10
        bar_y = self.y - 15
        
        pygame.draw.rect(surf, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, (255 * (1 - health_ratio), 255 * health_ratio, 0), 
                        (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
        
        boss_text = FONT.render(f"BOSS LEVEL {self.level}", True, (255, 255, 255))
        surf.blit(boss_text, (self.x + self.width//2 - boss_text.get_width()//2, self.y - 30))
        
        for attack in self.attacks:
            attack.draw(surf)

# ----- START MENU -----
def start_menu():
    stars = [Star() for _ in range(100)]
    menu_running = True
    selected = 0
    options = ["START GAME", "QUIT"]
    
    while menu_running:
        WIN.fill(MENU_BG)
        for star in stars:
            star.update()
            star.draw(WIN)
        title = HUGE.render("ARKANOID", True, (255,255,100))
        subtitle = FONT.render("Ultimate Edition", True, (200,200,255))
        record_text = FONT.render(f"BEST SCORE: {load_record()}", True, (180,255,180))
        WIN.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
        WIN.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 100))
        WIN.blit(record_text, (WIDTH//2 - record_text.get_width()//2, HEIGHT//4 + 150))
        for i, opt in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            opt_text = BIG.render(opt, True, color)
            y = HEIGHT//2 + i * 70
            WIN.blit(opt_text, (WIDTH//2 - opt_text.get_width()//2, y))
        controls = SMALL.render("↑/↓: Select | ENTER: Confirm | A/D or ←/→: Move | SPACE: Laser", 
                               True, (150, 150, 150))
        WIN.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 50))
        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_UP, pygame.K_w): selected = (selected - 1) % len(options)
                elif ev.key in (pygame.K_DOWN, pygame.K_s): selected = (selected + 1) % len(options)
                elif ev.key == pygame.K_RETURN:
                    if selected == 0:
                        if start_sound: start_sound.play()
                        menu_running = False
                    else: pygame.quit(); exit()
        pygame.time.Clock().tick(30)

# ----- MAIN GAME -----
def main():
    start_menu()
    if start_sound: start_sound.stop()
    if ball_sound: ball_sound.play(-1)
    clock = pygame.time.Clock()
    running = True
    level_index = 1
    paddle = Paddle(WIDTH//2 - 60, HEIGHT - 40)
    balls = [Ball(WIDTH//2, paddle.rect.top - 10)]
    powerups = []
    lasers = []
    particles = []
    stars = [Star() for _ in range(50)]
    score = 0
    lives = 3
    message_timer = 0
    show_message = ""
    bricks = generate_level(level_index)
    max_levels = 50
    combo = ComboTracker()

    while running:
        dt = clock.tick(FPS)/(1000/60)
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_r: main(); return
                if event.key==pygame.K_SPACE:
                    new_lasers = paddle.shoot_laser()
                    lasers.extend(new_lasers)

        keys = pygame.key.get_pressed()
        move_dir = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        paddle.move(move_dir, dt)
        paddle.update()
        combo.update()

        for star in stars: star.update()
        for br in bricks: br.update()
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

        for b in balls: 
            b.update(dt)
            if paddle.has_magnet:
                dx = paddle.rect.centerx - b.x
                dy = paddle.rect.centery - b.y
                dist = math.hypot(dx, dy)
                if dist < 200 and b.y < paddle.rect.top:
                    force = 0.3
                    b.vx += (dx / dist) * force
                    b.vy += (dy / dist) * force
        
        for b in balls:
            if b.alive and b.rect.colliderect(paddle.rect): 
                ball_paddle_collision(b, paddle)
        
        for b in balls:
            if not b.alive: continue
            for br in bricks[:]:
                if b.rect.colliderect(br.rect):
                    reflect_ball_from_rect(b, br.rect)
                    destroyed = br.hit()
                    if destroyed:
                        bricks.remove(br)
                        combo.hit()
                        bonus = combo.get_bonus()
                        score += bonus
                        particles.extend(create_explosion(br.rect.centerx, br.rect.centery, 
                                                         br.base_color, 15))
                        if br.brick_type == "explosive":
                            explosion_rect = pygame.Rect(br.rect.x - 50, br.rect.y - 50, 
                                                        br.rect.w + 100, br.rect.h + 100)
                            for other_br in bricks[:]:
                                if explosion_rect.colliderect(other_br.rect) and not other_br.obstacle:
                                    if other_br.hit():
                                        bricks.remove(other_br)
                                        score += 50
                                        particles.extend(create_explosion(
                                            other_br.rect.centerx, other_br.rect.centery, 
                                            other_br.base_color, 10))
                        pu = spawn_powerup(br)
                        if pu: powerups.append(pu)
                    else: score += 25
                    break

        for laser in lasers[:]:
            laser.update()
            if not laser.alive:
                lasers.remove(laser)
                continue
            for br in bricks[:]:
                if laser.rect.colliderect(br.rect) and not br.obstacle:
                    laser.alive = False
                    destroyed = br.hit()
                    if destroyed:
                        bricks.remove(br)
                        score += 50
                        particles.extend(create_explosion(br.rect.centerx, br.rect.centery, 
                                                         br.base_color, 10))
                    break

        for pu in powerups:
            pu.update()
            if pu.alive and pu.rect.colliderect(paddle.rect):
                pu.alive=False
                if pu.kind=="x2": 
                    multiply_balls(balls,2)
                    show_message="Ball x2!"
                elif pu.kind=="x3": 
                    multiply_balls(balls,3)
                    show_message="Ball x3!"
                elif pu.kind=="slow":
                    for b in balls: b.vx*=0.7; b.vy*=0.7
                    show_message="Slow Motion!"
                elif pu.kind=="fast":
                    for b in balls: b.vx*=1.3; b.vy*=1.3
                    show_message="Speed Up!"
                elif pu.kind=="bigpaddle": 
                    paddle.rect.w = min(300, paddle.rect.w * 1.5)
                    show_message="Big Paddle!"
                elif pu.kind=="tinyball": 
                    for b in balls: b.r=max(3,b.r-3)
                    show_message="Tiny Ball!"
                elif pu.kind=="laser":
                    paddle.has_laser = True
                    paddle.laser_timer = 600
                    show_message="LASER ACTIVATED!"
                elif pu.kind=="shield":
                    paddle.has_shield = True
                    paddle.shield_timer = 600
                    show_message="SHIELD ON!"
                elif pu.kind=="magnet":
                    paddle.has_magnet = True
                    paddle.magnet_timer = 600
                    show_message="MAGNET POWER!"
                message_timer=120
        powerups=[p for p in powerups if p.alive]

        for b in balls:
            if b.y - b.r > HEIGHT:
                if not paddle.has_shield: b.alive=False
                else: b.y = paddle.rect.top - b.r; b.vy *= -1
                
        alive_balls=[b for b in balls if b.alive]
        if not alive_balls:
            lives-=1
            if lives<=0:
                if ball_sound: ball_sound.stop()
                if game_over_sound: game_over_sound.play()
                save_record(score)
                WIN.fill(BG)
                draw_center_text(WIN,"GAME OVER",BIG,(255,100,100))
                final_score = FONT.render(f"Final Score: {score}", True, TEXT_COLOR)
                max_combo_text = FONT.render(f"Max Combo: {combo.max_combo}", True, COMBO_COLOR)
                restart = FONT.render("Press R to restart", True, (150,150,150))
                WIN.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 60))
                WIN.blit(max_combo_text, (WIDTH//2 - max_combo_text.get_width()//2, HEIGHT//2 + 90))
                WIN.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 130))
                pygame.display.flip()
                pygame.time.wait(3000)
                main(); return
            else: balls=[Ball(paddle.rect.centerx,paddle.rect.top-10,vx=4*(1 if random.random()<0.5 else -1),vy=-4)]

        # Level completion check
        if len(bricks) == 0:
            level_index += 1
            if level_index > max_levels:
                WIN.fill(BG)
                draw_center_text(WIN, "VICTORY! YOU WIN!", BIG, (100, 255, 100))
                victory_msg = FONT.render(f"Final Score: {score}", True, TEXT_COLOR)
                WIN.blit(victory_msg, (WIDTH//2 - victory_msg.get_width()//2, HEIGHT//2 + 70))
                pygame.display.flip()
                pygame.time.wait(4000)
                save_record(score)
                main()
                return
            
            # Clear effects for new level
            paddle.has_laser = False
            paddle.has_shield = False
            paddle.has_magnet = False
            paddle.laser_timer = 0
            paddle.shield_timer = 0
            paddle.magnet_timer = 0
            paddle.rect.w = 120  # Reset paddle size
            
            # Reset balls
            balls = [Ball(paddle.rect.centerx, paddle.rect.top - 10)]
            
            # Generate new level
            bricks = generate_level(level_index)
            show_message = f"LEVEL {level_index}!"
            message_timer = 90
            lives += 1  # Bonus life every level
            
            # Clear powerups and lasers
            powerups = []
            lasers = []

        # DRAWING
        WIN.fill(BG)
        
        # Draw gradient background
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            r = int(BG[0] + (BG2[0] - BG[0]) * ratio)
            g = int(BG[1] + (BG2[1] - BG[1]) * ratio)
            b = int(BG[2] + (BG2[2] - BG[2]) * ratio)
            pygame.draw.line(WIN, (r, g, b), (0, i), (WIDTH, i))
        
        # Draw stars
        for star in stars:
            star.draw(WIN)
        
        # Draw bricks
        for br in bricks:
            br.draw(WIN)
        
        # Draw particles
        for p in particles:
            p.draw(WIN)
        
        # Draw powerups
        for pu in powerups:
            pu.draw(WIN)
        
        # Draw lasers
        for laser in lasers:
            laser.draw(WIN)
        
        # Draw balls
        for b in balls:
            b.draw(WIN)
        
        # Draw paddle
        paddle.draw(WIN)
        
        # Draw UI
        score_text = FONT.render(f"SCORE: {score}", True, TEXT_COLOR)
        level_text = FONT.render(f"LEVEL: {level_index}/{max_levels}", True, TEXT_COLOR)
        lives_text = FONT.render(f"LIVES: {'❤' * lives}", True, (255, 100, 100))
        record_text = FONT.render(f"BEST: {load_record()}", True, (180, 255, 180))
        
        WIN.blit(score_text, (10, 10))
        WIN.blit(level_text, (10, 40))
        WIN.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
        WIN.blit(record_text, (WIDTH - record_text.get_width() - 10, 40))
        
        # Draw combo
        combo.draw(WIN, WIDTH//2 - 50, 80)
        
        # Draw powerup indicators
        y_pos = 70
        if paddle.has_laser:
            laser_ind = FONT.render("LASER", True, LASER_COLOR)
            WIN.blit(laser_ind, (WIDTH//2 - laser_ind.get_width()//2, y_pos))
            y_pos += 25
        
        if paddle.has_shield:
            shield_ind = FONT.render("SHIELD", True, SHIELD_COLOR)
            WIN.blit(shield_ind, (WIDTH//2 - shield_ind.get_width()//2, y_pos))
            y_pos += 25
        
        if paddle.has_magnet:
            magnet_ind = FONT.render("MAGNET", True, MAGNET_COLOR)
            WIN.blit(magnet_ind, (WIDTH//2 - magnet_ind.get_width()//2, y_pos))
        
        # Draw message
        if message_timer > 0:
            message_timer -= 1
            alpha = min(255, message_timer * 3)
            msg_surf = FONT.render(show_message, True, POWERUP_TEXT_COLOR)
            msg_surf.set_alpha(alpha)
            WIN.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//3))
        
        # Draw instructions
        inst = SMALL.render("SPACE: Laser | R: Restart | ESC: Quit", True, (150, 150, 150))
        WIN.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()

    pygame.quit()

# Add pause functionality
def draw_pause_screen(surf):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surf.blit(overlay, (0, 0))
    
    pause_text = BIG.render("PAUSED", True, (255, 255, 0))
    surf.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - 50))
    
    continue_text = FONT.render("Press P to continue", True, TEXT_COLOR)
    quit_text = FONT.render("Press ESC to quit", True, TEXT_COLOR)
    
    surf.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
    surf.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 50))

# Main game loop with pause
def main_with_pause():
    start_menu()
    if start_sound: start_sound.stop()
    if ball_sound: ball_sound.play(-1)
    clock = pygame.time.Clock()
    running = True
    paused = False
    level_index = 1
    paddle = Paddle(WIDTH//2 - 60, HEIGHT - 40)
    balls = [Ball(WIDTH//2, paddle.rect.top - 10)]
    powerups = []
    lasers = []
    particles = []
    stars = [Star() for _ in range(50)]
    score = 0
    lives = 3
    message_timer = 0
    show_message = ""
    bricks = generate_level(level_index)
    max_levels = 50
    combo = ComboTracker()

    while running:
        dt = clock.tick(FPS)/(1000/60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    main_with_pause()
                    return
                if event.key == pygame.K_p: 
                    paused = not paused
                if event.key == pygame.K_SPACE and not paused:
                    new_lasers = paddle.shoot_laser()
                    lasers.extend(new_lasers)
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        if paused:
            WIN.fill(BG)
            draw_pause_screen(WIN)
            pygame.display.flip()
            continue
        
        keys = pygame.key.get_pressed()
        move_dir = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        paddle.move(move_dir, dt)
        paddle.update()
        combo.update()

        for star in stars: star.update()
        for br in bricks: br.update()
        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

        for b in balls: 
            b.update(dt)
            if paddle.has_magnet:
                dx = paddle.rect.centerx - b.x
                dy = paddle.rect.centery - b.y
                dist = math.hypot(dx, dy)
                if dist < 200 and b.y < paddle.rect.top:
                    force = 0.3
                    b.vx += (dx / dist) * force
                    b.vy += (dy / dist) * force
        
        for b in balls:
            if b.alive and b.rect.colliderect(paddle.rect): 
                ball_paddle_collision(b, paddle)
        
        for b in balls:
            if not b.alive: continue
            for br in bricks[:]:
                if b.rect.colliderect(br.rect):
                    reflect_ball_from_rect(b, br.rect)
                    destroyed = br.hit()
                    if destroyed:
                        bricks.remove(br)
                        combo.hit()
                        bonus = combo.get_bonus()
                        score += bonus
                        particles.extend(create_explosion(br.rect.centerx, br.rect.centery, 
                                                         br.base_color, 15))
                        if br.brick_type == "explosive":
                            explosion_rect = pygame.Rect(br.rect.x - 50, br.rect.y - 50, 
                                                        br.rect.w + 100, br.rect.h + 100)
                            for other_br in bricks[:]:
                                if explosion_rect.colliderect(other_br.rect) and not other_br.obstacle:
                                    if other_br.hit():
                                        bricks.remove(other_br)
                                        score += 50
                                        particles.extend(create_explosion(
                                            other_br.rect.centerx, other_br.rect.centery, 
                                            other_br.base_color, 10))
                        pu = spawn_powerup(br)
                        if pu: powerups.append(pu)
                    else: score += 25
                    break

        for laser in lasers[:]:
            laser.update()
            if not laser.alive:
                lasers.remove(laser)
                continue
            for br in bricks[:]:
                if laser.rect.colliderect(br.rect) and not br.obstacle:
                    laser.alive = False
                    destroyed = br.hit()
                    if destroyed:
                        bricks.remove(br)
                        score += 50
                        particles.extend(create_explosion(br.rect.centerx, br.rect.centery, 
                                                         br.base_color, 10))
                    break

        for pu in powerups[:]:
            pu.update()
            if pu.alive and pu.rect.colliderect(paddle.rect):
                powerups.remove(pu)
                if pu.kind=="x2": 
                    multiply_balls(balls,2)
                    show_message="Ball x2!"
                elif pu.kind=="x3": 
                    multiply_balls(balls,3)
                    show_message="Ball x3!"
                elif pu.kind=="slow":
                    for b in balls: b.vx*=0.7; b.vy*=0.7
                    show_message="Slow Motion!"
                elif pu.kind=="fast":
                    for b in balls: b.vx*=1.3; b.vy*=1.3
                    show_message="Speed Up!"
                elif pu.kind=="bigpaddle": 
                    paddle.rect.w = min(300, paddle.rect.w * 1.5)
                    show_message="Big Paddle!"
                elif pu.kind=="tinyball": 
                    for b in balls: b.r=max(3,b.r-3)
                    show_message="Tiny Ball!"
                elif pu.kind=="laser":
                    paddle.has_laser = True
                    paddle.laser_timer = 600
                    show_message="LASER ACTIVATED!"
                elif pu.kind=="shield":
                    paddle.has_shield = True
                    paddle.shield_timer = 600
                    show_message="SHIELD ON!"
                elif pu.kind=="magnet":
                    paddle.has_magnet = True
                    paddle.magnet_timer = 600
                    show_message="MAGNET POWER!"
                message_timer=120

        for b in balls[:]:
            if b.y - b.r > HEIGHT:
                if not paddle.has_shield: 
                    balls.remove(b)
                else: 
                    b.y = paddle.rect.top - b.r
                    b.vy *= -1
                
        if len(balls) == 0:
            lives-=1
            if lives<=0:
                if ball_sound: ball_sound.stop()
                if game_over_sound: game_over_sound.play()
                save_record(score)
                WIN.fill(BG)
                draw_center_text(WIN,"GAME OVER",BIG,(255,100,100))
                final_score = FONT.render(f"Final Score: {score}", True, TEXT_COLOR)
                max_combo_text = FONT.render(f"Max Combo: {combo.max_combo}", True, COMBO_COLOR)
                restart = FONT.render("Press R to restart", True, (150,150,150))
                WIN.blit(final_score, (WIDTH//2 - final_score.get_width()//2, HEIGHT//2 + 60))
                WIN.blit(max_combo_text, (WIDTH//2 - max_combo_text.get_width()//2, HEIGHT//2 + 90))
                WIN.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 130))
                pygame.display.flip()
                pygame.time.wait(3000)
                main_with_pause()
                return
            else: 
                balls=[Ball(paddle.rect.centerx,paddle.rect.top-10,
                          vx=4*(1 if random.random()<0.5 else -1),vy=-4)]

        # Level completion check - TO'G'RILANGAN
        if len(bricks) == 0:
            level_index += 1
            if level_index > max_levels:
                WIN.fill(BG)
                draw_center_text(WIN, "VICTORY! YOU WIN!", BIG, (100, 255, 100))
                victory_msg = FONT.render(f"Final Score: {score}", True, TEXT_COLOR)
                WIN.blit(victory_msg, (WIDTH//2 - victory_msg.get_width()//2, HEIGHT//2 + 70))
                pygame.display.flip()
                pygame.time.wait(4000)
                save_record(score)
                main_with_pause()
                return
            
            # Clear effects for new level
            paddle.has_laser = False
            paddle.has_shield = False
            paddle.has_magnet = False
            paddle.laser_timer = 0
            paddle.shield_timer = 0
            paddle.magnet_timer = 0
            paddle.rect.w = 120
            
            # Reset balls
            balls = [Ball(paddle.rect.centerx, paddle.rect.top - 10)]
            
            # Generate new level
            bricks = generate_level(level_index)
            show_message = f"LEVEL {level_index}!"
            message_timer = 90
            lives += 1
            
            # Clear powerups and lasers
            powerups.clear()
            lasers.clear()
            particles.clear()
            
            # Yangi level ko'rsatish
            WIN.fill(BG)
            level_msg = BIG.render(f"LEVEL {level_index}", True, (100, 255, 100))
            WIN.blit(level_msg, (WIDTH//2 - level_msg.get_width()//2, HEIGHT//2 - 50))
            continue_text = FONT.render("Get ready!", True, TEXT_COLOR)
            WIN.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT//2 + 20))
            pygame.display.flip()
            pygame.time.wait(1500)
            
            continue  # ◀◀◀ BU YANGI LEVELGA TO'G'RI O'TISH UCHUN

        # DRAWING
        WIN.fill(BG)
        
        # Gradient background
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            r = int(BG[0] + (BG2[0] - BG[0]) * ratio)
            g = int(BG[1] + (BG2[1] - BG[1]) * ratio)
            b = int(BG[2] + (BG2[2] - BG[2]) * ratio)
            pygame.draw.line(WIN, (r, g, b), (0, i), (WIDTH, i))
        
        for star in stars: star.draw(WIN)
        for br in bricks: br.draw(WIN)
        for p in particles: p.draw(WIN)
        for pu in powerups: pu.draw(WIN)
        for laser in lasers: laser.draw(WIN)
        for b in balls: b.draw(WIN)
        paddle.draw(WIN)
        
        # UI drawing
        score_text = FONT.render(f"SCORE: {score}", True, TEXT_COLOR)
        level_text = FONT.render(f"LEVEL: {level_index}/{max_levels}", True, TEXT_COLOR)
        lives_text = FONT.render(f"LIVES: {'❤' * lives}", True, (255, 100, 100))
        record_text = FONT.render(f"BEST: {load_record()}", True, (180, 255, 180))
        
        WIN.blit(score_text, (10, 10))
        WIN.blit(level_text, (10, 40))
        WIN.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
        WIN.blit(record_text, (WIDTH - record_text.get_width() - 10, 40))
        
        combo.draw(WIN, WIDTH//2 - 50, 80)
        
        if message_timer > 0:
            message_timer -= 1
            alpha = min(255, message_timer * 3)
            msg_surf = FONT.render(show_message, True, POWERUP_TEXT_COLOR)
            msg_surf.set_alpha(alpha)
            WIN.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//3))
        
        inst = SMALL.render("P: Pause | SPACE: Laser | R: Restart | ESC: Quit", True, (150, 150, 150))
        WIN.blit(inst, (WIDTH//2 - inst.get_width()//2, HEIGHT - 30))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main_with_pause()
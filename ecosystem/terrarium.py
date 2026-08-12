#!/usr/bin/env python3
"""
DIGITAL TERRARIUM
==================
یک اکوسیستم مصنوعی زنده. موجودات ساده با ژنوم خودشون (رنگ، سرعت،
اندازه، حس بویایی، متابولیسم) در یک دنیای بسته زندگی می‌کنن، دنبال
غذا می‌گردن، تولیدمثل می‌کنن (با جهش ژنتیکی تصادفی روی فرزندان)،
و می‌میرن. با گذر زمان، جمعیت به سمت استراتژی‌های بقای متفاوتی
تکامل پیدا می‌کنه — این یعنی هر بار که اجرا می‌کنی، یه تاریخ تکاملی
متفاوت و غیرقابل پیش‌بینی می‌بینی.

کنترل‌ها:
  SPACE       - Pause / Resume
  F           - افزودن دسته‌ای غذا در نقطه رندوم (تزریق فراوانی)
  C           - افزودن یک موجود جدید تصادفی (Catastrophe recovery)
  UP / DOWN   - افزایش / کاهش سرعت شبیه‌سازی
  1-4         - تغییر حالت رنگ‌آمیزی نمایش (Species / Speed / Energy / Age)
  R           - ریست کامل دنیا
  ESC / Q     - خروج

نویسنده: ساخته‌شده برای کاوش تکامل، رفتار نوظهور (emergent behavior)
و زیبایی‌شناسی سیستم‌های پیچیده.
"""

import pygame
import random
import math
import sys
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# پیکربندی جهانی
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 800
SIDEBAR_W = 300
WORLD_W = WIDTH - SIDEBAR_W
FPS = 60

BG_COLOR = (8, 10, 14)
PANEL_COLOR = (14, 17, 23)
GRID_COLOR = (18, 22, 28)
TEXT_COLOR = (150, 220, 200)
TEXT_DIM = (80, 100, 95)
ACCENT = (80, 220, 160)
FOOD_COLOR = (60, 160, 90)
WARN_COLOR = (220, 90, 90)

INITIAL_POP = 40
INITIAL_FOOD = 90
MAX_FOOD = 260
FOOD_SPAWN_RATE = 0.9          # آیتم غذا در هر فریم (احتمالاتی)
FOOD_ENERGY = 34
MUTATION_RATE = 0.14
MUTATION_STRENGTH = 0.22
MAX_POPULATION = 260

random.seed()

# ---------------------------------------------------------------------------
# ابزارهای کمکی
# ---------------------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, t):
    return a + (b - a) * t


def hsv_to_rgb(h, s, v):
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    i %= 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    else:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)


# ---------------------------------------------------------------------------
# ژنوم: DNA هر موجود. یک بردار کوچک از صفات که با جهش منتقل می‌شه.
# ---------------------------------------------------------------------------
@dataclass
class Genome:
    hue: float          # 0..1  -> رنگ گونه (نشانگر بصری "خط تکاملی")
    speed: float         # سرعت حرکت پایه
    size: float          # اندازه فیزیکی (تأثیر روی مصرف انرژی و دید)
    sense: float          # شعاع حس بویایی برای یافتن غذا
    metabolism: float    # نرخ مصرف انرژی در واحد زمان
    aggression: float    # تمایل به شکار موجودات کوچکتر (0..1)

    def mutated(self):
        def m(val, lo, hi, strength=MUTATION_STRENGTH):
            if random.random() < MUTATION_RATE:
                val += random.uniform(-strength, strength) * (hi - lo)
            return clamp(val, lo, hi)

        hue = self.hue
        if random.random() < MUTATION_RATE * 0.5:
            hue = (hue + random.uniform(-0.05, 0.05)) % 1.0

        return Genome(
            hue=hue,
            speed=m(self.speed, 0.5, 3.2),
            size=m(self.size, 3.0, 11.0),
            sense=m(self.sense, 25.0, 160.0),
            metabolism=m(self.metabolism, 0.02, 0.16),
            aggression=m(self.aggression, 0.0, 1.0),
        )

    @staticmethod
    def random():
        return Genome(
            hue=random.random(),
            speed=random.uniform(0.8, 2.4),
            size=random.uniform(4.0, 8.0),
            sense=random.uniform(40.0, 110.0),
            metabolism=random.uniform(0.05, 0.11),
            aggression=random.uniform(0.0, 0.35),
        )


# ---------------------------------------------------------------------------
# غذا
# ---------------------------------------------------------------------------
@dataclass
class Food:
    x: float
    y: float
    energy: float = FOOD_ENERGY
    pulse: float = field(default_factory=lambda: random.uniform(0, math.pi * 2))


# ---------------------------------------------------------------------------
# موجود زنده
# ---------------------------------------------------------------------------
class Creature:
    __slots__ = (
        "x", "y", "vx", "vy", "genome", "energy", "age", "max_age",
        "wander_angle", "generation", "id", "reproduce_cooldown", "trail"
    )
    _next_id = 0

    def __init__(self, x, y, genome, energy=70.0, generation=0):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.genome = genome
        self.energy = energy
        self.age = 0.0
        self.max_age = random.uniform(900, 1500)
        self.wander_angle = random.uniform(0, math.pi * 2)
        self.generation = generation
        self.reproduce_cooldown = 0.0
        Creature._next_id += 1
        self.id = Creature._next_id
        self.trail = []

    @property
    def alive(self):
        return self.energy > 0 and self.age < self.max_age

    def nearest_food(self, foods):
        best, best_d2 = None, self.genome.sense ** 2
        for f in foods:
            dx, dy = f.x - self.x, f.y - self.y
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best, best_d2 = f, d2
        return best

    def nearest_prey(self, creatures):
        if self.genome.aggression < 0.12:
            return None
        best, best_d2 = None, (self.genome.sense * 0.7) ** 2
        for c in creatures:
            if c is self or not c.alive:
                continue
            if c.genome.size >= self.genome.size * 0.85:
                continue
            dx, dy = c.x - self.x, c.y - self.y
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best, best_d2 = c, d2
        return best

    def update(self, dt, foods, creatures, world_w, world_h):
        self.age += dt

        target_dx, target_dy = 0.0, 0.0
        prey = self.nearest_prey(creatures)
        target = None
        hunting = False
        if prey is not None:
            target = prey
            hunting = True
        else:
            target = self.nearest_food(foods)

        if target is not None:
            dx, dy = target.x - self.x, target.y - self.y
            dist = math.hypot(dx, dy) + 1e-6
            target_dx, target_dy = dx / dist, dy / dist
        else:
            # پرسه‌زنی تصادفی نرم (Perlin-like wander)
            self.wander_angle += random.uniform(-0.4, 0.4)
            target_dx = math.cos(self.wander_angle)
            target_dy = math.sin(self.wander_angle)

        speed = self.genome.speed * (1.4 if hunting else 1.0)
        self.vx = lerp(self.vx, target_dx * speed, 0.12)
        self.vy = lerp(self.vy, target_dy * speed, 0.12)

        self.x += self.vx
        self.y += self.vy

        # برخورد با دیواره (بازتاب نرم)
        margin = self.genome.size
        if self.x < margin:
            self.x = margin
            self.vx *= -0.6
        elif self.x > world_w - margin:
            self.x = world_w - margin
            self.vx *= -0.6
        if self.y < margin:
            self.y = margin
            self.vy *= -0.6
        elif self.y > world_h - margin:
            self.y = world_h - margin
            self.vy *= -0.6

        # مصرف انرژی متناسب با اندازه، سرعت و متابولیسم
        cost = self.genome.metabolism * (0.5 + self.genome.size * 0.05)
        cost += (abs(self.vx) + abs(self.vy)) * 0.02
        self.energy -= cost

        self.reproduce_cooldown = max(0.0, self.reproduce_cooldown - dt)

        # ردیابی مسیر برای جلوه بصری (کوتاه)
        self.trail.append((self.x, self.y))
        if len(self.trail) > 6:
            self.trail.pop(0)

        # شکار
        if hunting and target is not None and target.alive:
            dx, dy = target.x - self.x, target.y - self.y
            if dx * dx + dy * dy < (self.genome.size + target.genome.size) ** 2:
                gained = target.energy * 0.6 + 20
                self.energy += gained
                target.energy = -1  # کشته شد

        # خوردن غذا
        eaten = None
        for f in foods:
            dx, dy = f.x - self.x, f.y - self.y
            if dx * dx + dy * dy < (self.genome.size + 4) ** 2:
                eaten = f
                break
        if eaten is not None:
            self.energy += eaten.energy
            foods.remove(eaten)

        self.energy = min(self.energy, 160.0)

    def can_reproduce(self):
        return (
            self.energy > 95.0
            and self.reproduce_cooldown <= 0.0
            and self.age > 60
        )

    def reproduce(self):
        self.energy *= 0.45
        self.reproduce_cooldown = 140.0
        child_genome = self.genome.mutated()
        angle = random.uniform(0, math.pi * 2)
        cx = self.x + math.cos(angle) * (self.genome.size + 6)
        cy = self.y + math.sin(angle) * (self.genome.size + 6)
        return Creature(cx, cy, child_genome, energy=45.0, generation=self.generation + 1)

    def color(self, mode, world):
        g = self.genome
        if mode == "species":
            return hsv_to_rgb(g.hue, 0.75, 0.95)
        elif mode == "speed":
            t = clamp((g.speed - 0.5) / (3.2 - 0.5), 0, 1)
            return hsv_to_rgb(0.55 - t * 0.55, 0.85, 0.95)
        elif mode == "energy":
            t = clamp(self.energy / 160.0, 0, 1)
            return hsv_to_rgb(0.0 + t * 0.33, 0.85, 0.95)
        elif mode == "age":
            t = clamp(self.age / self.max_age, 0, 1)
            return hsv_to_rgb(0.75 - t * 0.6, 0.8, 0.95)
        return (200, 200, 200)


# ---------------------------------------------------------------------------
# دنیای شبیه‌سازی
# ---------------------------------------------------------------------------
class World:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.creatures = []
        self.foods = []
        self.tick = 0
        self.total_births = 0
        self.total_deaths = 0
        self.speed_mult = 1
        self.color_mode = "species"
        self.paused = False
        self.reset()

    def reset(self):
        self.creatures = [
            Creature(
                random.uniform(20, self.w - 20),
                random.uniform(20, self.h - 20),
                Genome.random(),
            )
            for _ in range(INITIAL_POP)
        ]
        self.foods = [
            Food(random.uniform(10, self.w - 10), random.uniform(10, self.h - 10))
            for _ in range(INITIAL_FOOD)
        ]
        self.tick = 0
        self.total_births = 0
        self.total_deaths = 0

    def spawn_food_burst(self, n=25):
        cx = random.uniform(80, self.w - 80)
        cy = random.uniform(80, self.h - 80)
        for _ in range(n):
            fx = clamp(cx + random.gauss(0, 60), 5, self.w - 5)
            fy = clamp(cy + random.gauss(0, 60), 5, self.h - 5)
            self.foods.append(Food(fx, fy))

    def add_random_creature(self):
        self.creatures.append(
            Creature(
                random.uniform(20, self.w - 20),
                random.uniform(20, self.h - 20),
                Genome.random(),
            )
        )

    def step(self, dt):
        if self.paused:
            return
        for _ in range(self.speed_mult):
            self._simulate_one(dt)

    def _simulate_one(self, dt):
        self.tick += 1

        if len(self.foods) < MAX_FOOD and random.random() < FOOD_SPAWN_RATE:
            self.foods.append(
                Food(random.uniform(5, self.w - 5), random.uniform(5, self.h - 5))
            )

        newborns = []
        for c in self.creatures:
            c.update(dt, self.foods, self.creatures, self.w, self.h)
            if c.can_reproduce() and len(self.creatures) < MAX_POPULATION:
                newborns.append(c.reproduce())
                self.total_births += 1

        before = len(self.creatures)
        self.creatures = [c for c in self.creatures if c.alive]
        self.total_deaths += before - len(self.creatures)

        self.creatures.extend(newborns)

        # جلوگیری از انقراض کامل: اگر جمعیت خیلی کم شد، چند موجود تازه اضافه کن
        if len(self.creatures) < 4:
            for _ in range(6):
                self.add_random_creature()

    def stats(self):
        n = len(self.creatures)
        if n == 0:
            return dict(n=0, avg_speed=0, avg_size=0, avg_sense=0, avg_aggr=0, max_gen=0)
        avg_speed = sum(c.genome.speed for c in self.creatures) / n
        avg_size = sum(c.genome.size for c in self.creatures) / n
        avg_sense = sum(c.genome.sense for c in self.creatures) / n
        avg_aggr = sum(c.genome.aggression for c in self.creatures) / n
        max_gen = max(c.generation for c in self.creatures)
        return dict(
            n=n, avg_speed=avg_speed, avg_size=avg_size,
            avg_sense=avg_sense, avg_aggr=avg_aggr, max_gen=max_gen,
        )


# ---------------------------------------------------------------------------
# رابط گرافیکی
# ---------------------------------------------------------------------------
class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Digital Terrarium — یک اکوسیستم مصنوعی زنده")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = World(WORLD_W, HEIGHT)

        self.font_small = pygame.font.SysFont("consolas", 14)
        self.font_med = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_big = pygame.font.SysFont("consolas", 26, bold=True)

        self.pop_history = []
        self.max_history = 200
        self.frame = 0

        self.color_modes = ["species", "speed", "energy", "age"]

    # -- رویدادها -----------------------------------------------------
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    return False
                elif event.key == pygame.K_SPACE:
                    self.world.paused = not self.world.paused
                elif event.key == pygame.K_f:
                    self.world.spawn_food_burst()
                elif event.key == pygame.K_c:
                    self.world.add_random_creature()
                elif event.key == pygame.K_r:
                    self.world.reset()
                    self.pop_history.clear()
                elif event.key == pygame.K_UP:
                    self.world.speed_mult = min(6, self.world.speed_mult + 1)
                elif event.key == pygame.K_DOWN:
                    self.world.speed_mult = max(1, self.world.speed_mult - 1)
                elif event.key == pygame.K_1:
                    self.world.color_mode = "species"
                elif event.key == pygame.K_2:
                    self.world.color_mode = "speed"
                elif event.key == pygame.K_3:
                    self.world.color_mode = "energy"
                elif event.key == pygame.K_4:
                    self.world.color_mode = "age"
        return True

    # -- ترسیم ----------------------------------------------------------
    def draw_grid(self, surf):
        step = 40
        for x in range(0, WORLD_W, step):
            pygame.draw.line(surf, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, step):
            pygame.draw.line(surf, GRID_COLOR, (0, y), (WORLD_W, y), 1)

    def draw_world(self):
        world_surf = self.screen.subsurface((0, 0, WORLD_W, HEIGHT))
        world_surf.fill(BG_COLOR)
        self.draw_grid(world_surf)

        # غذا (پالس ملایم)
        for f in self.world.foods:
            f.pulse += 0.08
            r = 3 + math.sin(f.pulse) * 1.2
            pygame.draw.circle(world_surf, FOOD_COLOR, (int(f.x), int(f.y)), max(1, int(r)))

        # موجودات
        for c in self.world.creatures:
            col = c.color(self.world.color_mode, self.world)
            # دنباله محو
            for i, (tx, ty) in enumerate(c.trail):
                alpha_t = (i + 1) / max(1, len(c.trail))
                trail_col = tuple(int(ch * alpha_t * 0.4) for ch in col)
                pygame.draw.circle(world_surf, trail_col, (int(tx), int(ty)), max(1, int(c.genome.size * 0.4)))

            size = max(2, int(c.genome.size))
            pygame.draw.circle(world_surf, col, (int(c.x), int(c.y)), size)

            # حلقه دید برای موجودات شکارچی پرانرژی (جلوه بصری ظریف)
            if c.genome.aggression > 0.5:
                pygame.draw.circle(world_surf, WARN_COLOR, (int(c.x), int(c.y)), size + 2, 1)

            # نوار انرژی کوچک بالای موجودات درشت
            if size > 5:
                bar_w = size * 2
                e_ratio = clamp(c.energy / 160.0, 0, 1)
                bx = int(c.x - bar_w / 2)
                by = int(c.y - size - 6)
                pygame.draw.rect(world_surf, (40, 40, 40), (bx, by, bar_w, 3))
                pygame.draw.rect(world_surf, ACCENT, (bx, by, int(bar_w * e_ratio), 3))

    def draw_sidebar(self):
        x0 = WORLD_W
        panel = pygame.Rect(x0, 0, SIDEBAR_W, HEIGHT)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel)
        pygame.draw.line(self.screen, GRID_COLOR, (x0, 0), (x0, HEIGHT), 2)

        pad = 18
        y = 20

        title = self.font_big.render("TERRARIUM", True, ACCENT)
        self.screen.blit(title, (x0 + pad, y))
        y += 40

        stats = self.world.stats()

        def line(label, value, color=TEXT_COLOR):
            nonlocal y
            txt = self.font_small.render(f"{label:<16}{value}", True, color)
            self.screen.blit(txt, (x0 + pad, y))
            y += 20

        status = "PAUSED" if self.world.paused else "RUNNING"
        status_col = WARN_COLOR if self.world.paused else ACCENT
        line("STATUS", status, status_col)
        line("TICK", stats and self.world.tick)
        line("SPEED", f"x{self.world.speed_mult}")
        y += 8
        pygame.draw.line(self.screen, GRID_COLOR, (x0 + pad, y), (WIDTH - pad, y), 1)
        y += 14

        line("POPULATION", stats["n"])
        line("FOOD", len(self.world.foods))
        line("BIRTHS", self.world.total_births)
        line("DEATHS", self.world.total_deaths)
        line("MAX GEN", stats["max_gen"])
        y += 8
        pygame.draw.line(self.screen, GRID_COLOR, (x0 + pad, y), (WIDTH - pad, y), 1)
        y += 14

        line("AVG SPEED", f"{stats['avg_speed']:.2f}")
        line("AVG SIZE", f"{stats['avg_size']:.2f}")
        line("AVG SENSE", f"{stats['avg_sense']:.1f}")
        line("AVG AGGR.", f"{stats['avg_aggr']:.2f}")
        y += 14

        mode_txt = self.font_med.render(f"COLOR: {self.world.color_mode.upper()}", True, TEXT_COLOR)
        self.screen.blit(mode_txt, (x0 + pad, y))
        y += 32

        # نمودار جمعیت زنده
        self.pop_history.append(stats["n"])
        if len(self.pop_history) > self.max_history:
            self.pop_history.pop(0)

        chart_h = 90
        chart_rect = pygame.Rect(x0 + pad, y, SIDEBAR_W - pad * 2, chart_h)
        pygame.draw.rect(self.screen, (10, 12, 16), chart_rect)
        pygame.draw.rect(self.screen, GRID_COLOR, chart_rect, 1)
        if len(self.pop_history) > 1:
            max_pop = max(max(self.pop_history), 10)
            pts = []
            for i, v in enumerate(self.pop_history):
                px = chart_rect.x + i / (self.max_history - 1) * chart_rect.w
                py = chart_rect.y + chart_rect.h - (v / max_pop) * chart_rect.h
                pts.append((px, py))
            if len(pts) > 1:
                pygame.draw.lines(self.screen, ACCENT, False, pts, 2)
        chart_label = self.font_small.render("POPULATION HISTORY", True, TEXT_DIM)
        self.screen.blit(chart_label, (x0 + pad, y - 18))
        y += chart_h + 26

        # راهنمای کنترل
        pygame.draw.line(self.screen, GRID_COLOR, (x0 + pad, y), (WIDTH - pad, y), 1)
        y += 12
        help_title = self.font_med.render("CONTROLS", True, ACCENT)
        self.screen.blit(help_title, (x0 + pad, y))
        y += 26

        controls = [
            ("SPACE", "Pause / Resume"),
            ("F", "Food burst"),
            ("C", "Add creature"),
            ("UP/DOWN", "Sim speed"),
            ("1-4", "Color mode"),
            ("R", "Reset world"),
            ("ESC / Q", "Quit"),
        ]
        for key, desc in controls:
            key_txt = self.font_small.render(key, True, ACCENT)
            desc_txt = self.font_small.render(desc, True, TEXT_DIM)
            self.screen.blit(key_txt, (x0 + pad, y))
            self.screen.blit(desc_txt, (x0 + pad + 90, y))
            y += 20

    # -- حلقه اصلی --------------------------------------------------------
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.world.step(1.0)
            self.draw_world()
            self.draw_sidebar()
            pygame.display.flip()
            self.clock.tick(FPS)
            self.frame += 1
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    App().run()

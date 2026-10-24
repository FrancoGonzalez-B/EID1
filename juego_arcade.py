import math
import random

import pygame


WIDTH = 1000
HEIGHT = 700
FPS = 60
MAP_RECT = pygame.Rect(22, 76, WIDTH - 44, HEIGHT - 154)
BACKGROUND = (7, 13, 31)
WHITE = (235, 244, 255)
CYAN = (73, 225, 255)
PLAYER_COLOR = (93, 234, 255)

AMMO_NAMES = {"basic": "BÁSICA", "parabolic": "PARABÓLICA", "conic": "CÓNICA"}
AMMO_DAMAGE = {"basic": 1, "parabolic": 2, "conic": 3}
AMMO_COOLDOWN = {"parabolic": 760, "conic": 1180}
PLAYER_DAMAGE = {1: 1, 2: 2, 3: 3, "boss": 12}

ENEMY_SETTINGS = {
    1: {"amplitude": 30, "frequency": 1.08, "phase": 0.15, "speed": 122, "hp": 3, "stop_x": MAP_RECT.left + 268},
    2: {"amplitude": 41, "frequency": 1.39, "phase": 0.83, "speed": 100, "hp": 6, "stop_x": MAP_RECT.left + 340},
    3: {"amplitude": 53, "frequency": 1.72, "phase": 1.57, "speed": 86, "hp": 9, "stop_x": MAP_RECT.left + 405},
    "boss": {"amplitude": 68, "frequency": 0.77, "phase": 2.21, "speed": 54, "hp": 18, "stop_x": MAP_RECT.left + 692},
}

WAVES = [
    [1, 1, 1, 1],
    [1, 2, 1, 2],
    [1, 2, 3, 1, 2, 3],
    ["boss", 1, 2],
]


class Player:
    def __init__(self):
        self.x = MAP_RECT.left + 56
        self.y = MAP_RECT.centery
        self.speed = 310
        self.hp = 12
        self.max_hp = 12
        self.invulnerable_until = 0

    @property
    def hitbox(self):
        return pygame.Rect(round(self.x - 17), round(self.y - 15), 36, 30)

    def move(self, keys, dt):
        dx = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        if dx and dy:
            scale = 1 / math.sqrt(2)
            dx *= scale
            dy *= scale
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        self.x = max(MAP_RECT.left + 20, min(MAP_RECT.right - 20, self.x))
        self.y = max(MAP_RECT.top + 20, min(MAP_RECT.bottom - 20, self.y))

    def draw(self, screen, now):
        if now < self.invulnerable_until and (now // 90) % 2 == 0:
            return
        x, y = round(self.x), round(self.y)
        pygame.draw.polygon(screen, (23, 88, 122), [(x - 20, y - 16), (x + 20, y), (x - 20, y + 16)])
        pygame.draw.polygon(screen, PLAYER_COLOR, [(x - 15, y - 12), (x + 19, y), (x - 15, y + 12), (x - 7, y)])
        pygame.draw.polygon(screen, (195, 255, 255), [(x + 3, y - 5), (x + 14, y), (x + 3, y + 5)])
        pygame.draw.line(screen, (30, 173, 213), (x - 12, y - 10), (x - 12, y + 10), 2)


class Enemy:
    def __init__(self, kind, serial, spawn_offset=0):
        self.kind = kind
        settings = ENEMY_SETTINGS[kind]
        self.serial = serial
        self.A = settings["amplitude"] + serial * 0.31
        self.B = settings["frequency"] + serial * 0.0061
        self.C = settings["phase"] + serial * 0.47
        self.speed = settings["speed"]
        self.max_hp = settings["hp"]
        self.hp = self.max_hp
        self.stop_x = settings["stop_x"]
        half_height = 55 if kind == "boss" else 27
        low = MAP_RECT.top + half_height + self.A
        high = MAP_RECT.bottom - half_height - self.A
        self.D = random.randint(round(low), round(high)) + serial * 0.137
        self.x = MAP_RECT.right + 45 + spawn_offset
        self.y = self.D
        self.elapsed = 0.0

    @property
    def radius(self):
        return 52 if self.kind == "boss" else (30 if self.kind == 3 else 24)

    @property
    def hitbox(self):
        size = 92 if self.kind == "boss" else (54 if self.kind == 3 else 42)
        return pygame.Rect(round(self.x - size / 2), round(self.y - size / 2), size, size)

    def update(self, dt):
        self.elapsed += dt
        self.x = max(self.stop_x, self.x - self.speed * dt)
        self.y = self.A * math.sin(self.B * self.elapsed + self.C) + self.D

    def draw(self, screen, font_small):
        x, y = round(self.x), round(self.y)
        if self.kind == 1:
            pygame.draw.polygon(screen, (56, 193, 225), [(x - 22, y), (x - 35, y - 18), (x - 12, y - 12)])
            pygame.draw.polygon(screen, (56, 193, 225), [(x - 22, y), (x - 35, y + 18), (x - 12, y + 12)])
            pygame.draw.polygon(screen, (38, 105, 153), [(x - 16, y - 13), (x + 13, y - 13), (x + 24, y), (x + 13, y + 13), (x - 16, y + 13), (x - 24, y)])
            pygame.draw.line(screen, (144, 247, 255), (x - 13, y - 8), (x + 9, y - 8), 2)
            pygame.draw.circle(screen, (237, 255, 255), (x + 8, y), 4)
            pygame.draw.line(screen, (77, 202, 233), (x - 15, y - 12), (x - 24, y - 23), 2)
            pygame.draw.line(screen, (77, 202, 233), (x - 15, y + 12), (x - 24, y + 23), 2)
        elif self.kind == 2:
            pygame.draw.polygon(screen, (215, 120, 67), [(x - 21, y - 17), (x + 10, y - 20), (x + 23, y - 8), (x + 23, y + 12), (x + 7, y + 21), (x - 20, y + 15)])
            pygame.draw.rect(screen, (120, 66, 59), (x - 34, y - 8, 14, 16), border_radius=3)
            pygame.draw.rect(screen, (120, 66, 59), (x + 20, y - 8, 14, 16), border_radius=3)
            pygame.draw.polygon(screen, (255, 202, 112), [(x - 9, y - 11), (x + 7, y - 11), (x + 15, y), (x + 7, y + 11), (x - 9, y + 11), (x - 17, y)])
            pygame.draw.circle(screen, (77, 39, 57), (x + 1, y), 5)
            pygame.draw.line(screen, (255, 219, 157), (x - 13, y - 16), (x - 13, y + 15), 2)
        elif self.kind == 3:
            points = []
            for i in range(16):
                angle = i * math.tau / 16
                radius = 32 if i % 2 == 0 else 20
                points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
            pygame.draw.polygon(screen, (149, 75, 201), points)
            pygame.draw.circle(screen, (83, 47, 139), (x, y), 18)
            pygame.draw.circle(screen, (255, 111, 193), (x + 1, y), 9)
            pygame.draw.circle(screen, (255, 224, 246), (x + 2, y - 2), 3)
            pygame.draw.arc(screen, (223, 161, 255), pygame.Rect(x - 13, y - 13, 26, 26), 0.4, 2.8, 2)
        else:
            pygame.draw.polygon(screen, (111, 39, 112), [(x - 34, y - 15), (x - 60, y - 48), (x - 18, y - 36), (x, y - 50), (x + 20, y - 34), (x + 60, y - 46), (x + 39, y - 8), (x + 49, y + 31), (x + 15, y + 40), (x, y + 55), (x - 17, y + 40), (x - 50, y + 26)])
            pygame.draw.ellipse(screen, (187, 57, 151), pygame.Rect(x - 37, y - 28, 74, 58))
            pygame.draw.polygon(screen, (72, 36, 110), [(x - 21, y - 17), (x, y - 31), (x + 22, y - 17), (x + 19, y + 15), (x, y + 29), (x - 20, y + 14)])
            pygame.draw.circle(screen, (255, 116, 209), (x, y - 2), 12)
            pygame.draw.circle(screen, (255, 236, 255), (x + 1, y - 3), 4)
            pygame.draw.line(screen, (255, 173, 228), (x - 43, y - 3), (x - 21, y + 5), 3)
            pygame.draw.line(screen, (255, 173, 228), (x + 43, y - 3), (x + 21, y + 5), 3)

        if self.kind == "boss":
            bar_width = 100
            label = "JEFE"
        else:
            bar_width = 46
            label = f"E{self.kind}"
        bar_x = x - bar_width // 2
        bar_y = y - (68 if self.kind == "boss" else 39)
        pygame.draw.rect(screen, (38, 33, 56), (bar_x, bar_y, bar_width, 6), border_radius=3)
        pygame.draw.rect(screen, (255, 84, 128), (bar_x, bar_y, max(0, int(bar_width * self.hp / self.max_hp)), 6), border_radius=3)
        label_surface = font_small.render(label, True, (255, 225, 247))
        screen.blit(label_surface, (x - label_surface.get_width() // 2, bar_y - 16))


class Projectile:
    def __init__(self, kind, x, y):
        self.kind = kind
        self.origin_x = x
        self.origin_y = y
        self.x = x
        self.y = y
        self.elapsed = 0.0
        self.alive = True
        self.damage = AMMO_DAMAGE[kind]
        self.angle = math.pi

    @property
    def hitbox(self):
        size = 9 if self.kind == "basic" else 13
        return pygame.Rect(round(self.x - size / 2), round(self.y - size / 2), size, size)

    def update(self, dt):
        self.elapsed += dt
        if self.kind == "basic":
            self.x = self.origin_x + 650 * self.elapsed
        elif self.kind == "parabolic":
            self.x = self.origin_x + 560 * self.elapsed
            dx = self.x - self.origin_x
            self.y = self.origin_y + 0.0013 * dx * dx - 0.715 * dx
        else:
            radius = 245
            self.angle = math.pi + 2.9 * self.elapsed
            self.x = self.origin_x + radius + radius * math.cos(self.angle)
            self.y = self.origin_y + radius * math.sin(self.angle)
            if self.angle >= math.tau:
                self.alive = False
        if self.x > MAP_RECT.right + 24 or self.y < MAP_RECT.top - 35 or self.y > MAP_RECT.bottom + 35:
            self.alive = False

    def draw(self, screen):
        x, y = round(self.x), round(self.y)
        if self.kind == "basic":
            pygame.draw.line(screen, (116, 244, 255), (x - 9, y), (x + 5, y), 4)
            pygame.draw.circle(screen, (235, 255, 255), (x + 5, y), 3)
        elif self.kind == "parabolic":
            pygame.draw.circle(screen, (255, 190, 84), (x, y), 7)
            pygame.draw.circle(screen, (255, 244, 187), (x, y), 3)
            pygame.draw.line(screen, (255, 139, 64), (x - 8, y + 7), (x - 14, y + 12), 2)
        else:
            pygame.draw.circle(screen, (213, 141, 255), (x, y), 9)
            pygame.draw.circle(screen, (255, 240, 255), (x, y), 4)
            pygame.draw.circle(screen, (157, 85, 231), (x, y), 12, 1)


def make_round(now):
    return {
        "player": Player(),
        "enemies": [],
        "projectiles": [],
        "wave": 0,
        "spawn_index": 0,
        "next_spawn": now + 900,
        "next_fire": 0,
        "serial": 0,
        "ammo": "basic",
        "status": "playing",
        "phase_message_until": now + 1700,
    }


def draw_background(screen, stars):
    screen.fill(BACKGROUND)
    for x, y, brightness, size in stars:
        pygame.draw.circle(screen, (brightness, brightness + 12, brightness + 25), (x, y), size)
    for x in range(MAP_RECT.left + 28, MAP_RECT.right, 70):
        pygame.draw.line(screen, (13, 28, 52), (x, MAP_RECT.top), (x, MAP_RECT.bottom), 1)
    for y in range(MAP_RECT.top + 24, MAP_RECT.bottom, 70):
        pygame.draw.line(screen, (13, 28, 52), (MAP_RECT.left, y), (MAP_RECT.right, y), 1)
    pygame.draw.rect(screen, (38, 89, 122), MAP_RECT, 2, border_radius=10)


def draw_hud(screen, font, font_small, game, now):
    player = game["player"]
    pygame.draw.rect(screen, (13, 24, 47), (22, 14, WIDTH - 44, 52), border_radius=10)
    wave_text = "VICTORIA" if game["status"] == "won" else f"OLEADA {min(game['wave'] + 1, 4)} / 4"
    if game["wave"] == 3 and game["status"] == "playing":
        wave_text = "JEFE FINAL"
    screen.blit(font.render(wave_text, True, (122, 225, 255)), (40, 24))
    screen.blit(font_small.render("CASCO", True, (180, 202, 224)), (245, 20))
    pygame.draw.rect(screen, (43, 48, 69), (245, 43, 176, 12), border_radius=5)
    health_width = int(176 * max(0, player.hp) / player.max_hp)
    pygame.draw.rect(screen, (74, 225, 181) if player.hp > 4 else (255, 86, 108), (245, 43, health_width, 12), border_radius=5)
    screen.blit(font_small.render(f"{max(0, player.hp)}/{player.max_hp}", True, WHITE), (430, 38))
    ammo_text = f"MUNICIÓN: {AMMO_NAMES[game['ammo']]}  [{1 if game['ammo'] == 'basic' else 2 if game['ammo'] == 'parabolic' else 3}]"
    screen.blit(font_small.render(ammo_text, True, (255, 218, 137)), (565, 21))
    if game["ammo"] != "basic" and now < game["next_fire"]:
        remaining = (game["next_fire"] - now) / 1000
        ready = f"RECARGA {remaining:.1f}s"
    else:
        ready = "LISTA"
    screen.blit(font_small.render(ready, True, (187, 208, 226)), (565, 43))
    guide = "FLECHAS: MOVER    ESPACIO: DISPARAR    1: BÁSICA    2: PARABÓLICA    3: CÓNICA"
    guide_surface = font_small.render(guide, True, (167, 189, 216))
    screen.blit(guide_surface, (WIDTH // 2 - guide_surface.get_width() // 2, HEIGHT - 53))

    if now < game["phase_message_until"] and game["status"] == "playing":
        title = "JEFE FINAL" if game["wave"] == 3 else f"OLEADA {game['wave'] + 1}"
        message = font.render(title, True, WHITE)
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, 91))


def draw_end_screen(screen, font, font_small, status):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((3, 6, 19, 190))
    screen.blit(shade, (0, 0))
    title = "MISIÓN COMPLETADA" if status == "won" else "NAVE DESTRUIDA"
    title_surface = font.render(title, True, (129, 245, 255) if status == "won" else (255, 111, 133))
    prompt = font_small.render("Cierra la ventana para salir", True, WHITE)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, HEIGHT // 2 - 35))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 15))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Órbita de defensa")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 24, bold=True)
    font_small = pygame.font.SysFont("arial", 16, bold=True)
    stars = [(random.randint(MAP_RECT.left, MAP_RECT.right), random.randint(MAP_RECT.top, MAP_RECT.bottom), random.randint(65, 150), random.choice((1, 1, 2))) for _ in range(90)]
    game = make_round(pygame.time.get_ticks())
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000, 0.04)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game["ammo"] = "basic"
                elif event.key == pygame.K_2:
                    game["ammo"] = "parabolic"
                elif event.key == pygame.K_3:
                    game["ammo"] = "conic"

        if game["status"] == "playing":
            keys = pygame.key.get_pressed()
            player = game["player"]
            player.move(keys, dt)

            if keys[pygame.K_SPACE] and (game["ammo"] == "basic" or now >= game["next_fire"]):
                game["projectiles"].append(Projectile(game["ammo"], player.x + 18, player.y))
                if game["ammo"] != "basic":
                    game["next_fire"] = now + AMMO_COOLDOWN[game["ammo"]]

            wave = game["wave"]
            if wave < len(WAVES) and now >= game["next_spawn"]:
                plan = WAVES[wave]
                if wave == 3:
                    for index, kind in enumerate(plan):
                        game["enemies"].append(Enemy(kind, game["serial"], index * 82))
                        game["serial"] += 1
                    game["spawn_index"] = len(plan)
                    game["next_spawn"] = now + 10**9
                elif game["spawn_index"] < len(plan):
                    kind = plan[game["spawn_index"]]
                    game["enemies"].append(Enemy(kind, game["serial"]))
                    game["serial"] += 1
                    game["spawn_index"] += 1
                    game["next_spawn"] = now + 1150

                if game["spawn_index"] >= len(plan) and not game["enemies"]:
                    game["wave"] += 1
                    game["spawn_index"] = 0
                    game["next_spawn"] = now + 2100
                    game["phase_message_until"] = now + 1500
                    if game["wave"] >= len(WAVES):
                        game["status"] = "won"

            for enemy in game["enemies"]:
                enemy.update(dt)
            for projectile in game["projectiles"]:
                projectile.update(dt)
                if projectile.alive:
                    for enemy in game["enemies"]:
                        if projectile.hitbox.colliderect(enemy.hitbox):
                            enemy.hp -= projectile.damage
                            projectile.alive = False
                            break

            game["projectiles"] = [projectile for projectile in game["projectiles"] if projectile.alive]
            game["enemies"] = [enemy for enemy in game["enemies"] if enemy.hp > 0]

            if now >= player.invulnerable_until:
                for enemy in game["enemies"]:
                    if player.hitbox.colliderect(enemy.hitbox):
                        player.hp -= PLAYER_DAMAGE[enemy.kind]
                        player.invulnerable_until = now + 950
                        if player.hp <= 0:
                            game["status"] = "lost"
                        break

            if game["wave"] < len(WAVES) and game["spawn_index"] >= len(WAVES[game["wave"]]) and not game["enemies"]:
                game["wave"] += 1
                game["spawn_index"] = 0
                game["next_spawn"] = now + 2100
                game["phase_message_until"] = now + 1500
                if game["wave"] >= len(WAVES):
                    game["status"] = "won"

        draw_background(screen, stars)
        for projectile in game["projectiles"]:
            projectile.draw(screen)
        for enemy in game["enemies"]:
            enemy.draw(screen, font_small)
        game["player"].draw(screen, now)
        draw_hud(screen, font, font_small, game, now)
        if game["status"] != "playing":
            draw_end_screen(screen, font, font_small, game["status"])
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

import pgzrun
from pgzero.actor import Actor
from pygame import Rect
import random

WIDTH, HEIGHT = 360, 560
GRAVITY, JUMP_STRENGTH, PLAYER_SPEED = 0.5, -12, 3
MENU, PLAYING = 0, 1
game_state, sound_enabled = MENU, True


class Player:
    def __init__(self):
        self.actor = Actor("character_beige_front")
        self.actor.pos = (WIDTH // 2, 390)
        self.velocity_y = 0
        self.is_jumping = self.is_alive = True
        self.death_timer = self.blink_timer = self.idle_timer = self.walk_timer = 0

    def update(self):
        if self.is_alive:
            self.handle_movement()
            self.apply_physics()
            self.update_animation()
        else:
            self.blink_timer += 1
            self.death_timer -= 1
            if self.death_timer <= 0:
                global game_state
                game_state = MENU

    def handle_movement(self):
        if keyboard.right:
            self.actor.x = min(self.actor.x + PLAYER_SPEED, WIDTH)
            if not self.is_jumping:
                self.walk_timer += 1
                self.actor.image = (
                    "character_beige_walk_a"
                    if (self.walk_timer // 10) % 2 == 0
                    else "character_beige_walk_b"
                )
        elif keyboard.left:
            self.actor.x = max(self.actor.x - PLAYER_SPEED, 0)
            if not self.is_jumping:
                self.walk_timer += 1
                self.actor.image = (
                    "character_beige_walk_a2"
                    if (self.walk_timer // 10) % 2 == 0
                    else "character_beige_walk_b2"
                )
        else:
            self.walk_timer = 0
        if keyboard.space and not self.is_jumping:
            self.velocity_y = JUMP_STRENGTH
            self.is_jumping = True
            self.actor.image = (
                "character_beige_jump2" if keyboard.left else "character_beige_jump"
            )
            if sound_enabled:
                sounds.sfx_jump.play()

    def update_animation(self):
        if not self.is_jumping and not keyboard.left and not keyboard.right:
            self.idle_timer += 1
            if self.idle_timer >= 60:
                self.idle_timer = 0
            self.actor.image = (
                "character_beige_front"
                if (self.idle_timer // 30) % 2 == 0
                else "character_beige_front2"
            )

    def apply_physics(self):
        self.velocity_y += GRAVITY
        self.actor.y += self.velocity_y

        for platform in platforms:
            if (
                self.actor.x > platform.actor.x - 35
                and self.actor.x < platform.actor.x + 35
                and self.actor.y > platform.actor.y - 40
                and self.actor.y < platform.actor.y - 20
                and self.velocity_y > 0
            ):
                self.actor.y = platform.actor.y - 30
                self.velocity_y = 0
                self.is_jumping = False
        if self.actor.y > game_manager.camera_y + HEIGHT + 200:
            self.die()

    def die(self):
        self.is_alive = False
        self.death_timer = 120


class Platform:
    def __init__(self, x, y):
        self.actor = Actor("platform_gray")
        self.actor.pos = (x, y)


class Enemy:
    def __init__(self, x, y):
        self.actor = Actor("saw_a")
        self.actor.pos = (x, y)
        self.animation_timer = random.randint(10, 30)
        self.is_dying = False
        self.blink_timer = self.animation_frame = self.idle_timer = 0
        self.direction = random.choice([-1, 1])
        self.is_moving = True
        self.move_timer = random.randint(60, 120)

    def update(self):
        if self.is_dying:
            self.blink_timer += 1
            return self.blink_timer > 30
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.is_moving = not self.is_moving
            self.move_timer = random.randint(60, 120)
        if self.is_moving:
            self.actor.x += self.direction
            if self.actor.x < 20 or self.actor.x > WIDTH - 20:
                self.direction = -self.direction
            self.animation_timer -= 5
            if self.animation_timer <= 0:
                self.animation_frame = 1 - self.animation_frame
                self.actor.image = "saw_a" if self.animation_frame == 0 else "saw_b"
                self.animation_timer = random.randint(15, 25)
        else:
            self.idle_timer += 1
            if self.idle_timer >= 30:
                self.animation_frame = 1 - self.animation_frame
                self.actor.image = (
                    "saw_rest" if self.animation_frame == 0 else "saw_rest2"
                )
                self.idle_timer = 0

    def die(self):
        self.is_dying = True
        self.blink_timer = 0


class GameManager:
    def __init__(self):
        self.camera_y = self.score = 0
        self.highest_enemy_y = 50

    def update_camera(self):
        if player.actor.y < self.camera_y + 200:
            self.camera_y = player.actor.y - 200

    def spawn_new_enemies(self):
        player_height = -player.actor.y
        while self.highest_enemy_y > -(player_height + 800):
            self.highest_enemy_y -= 80
            enemies.append(
                Enemy(
                    random.randint(30, WIDTH - 30),
                    self.highest_enemy_y + random.randint(-30, 30),
                )
            )

    def check_collisions(self):
        enemies_to_remove = []
        for i, enemy in enumerate(enemies):
            if not enemy.is_dying:
                if (
                    abs(player.actor.x - enemy.actor.x) < 20
                    and abs(player.actor.y - enemy.actor.y) < 20
                ):
                    if player.velocity_y > 0 and player.actor.y < enemy.actor.y - 5:
                        enemy.die()
                        player.velocity_y = -8
                        self.score += 10
                        if sound_enabled:
                            sounds.sfx_bump.play()
                    else:
                        player.die()
            if enemy.is_dying and enemy.update():
                enemies_to_remove.append(i)
        for i in reversed(enemies_to_remove):
            enemies.pop(i)


def create_platforms():
    platforms.clear()
    platforms.append(Platform(WIDTH // 2, 420))
    for i in range(20):
        platforms.append(Platform(random.randint(50, WIDTH - 50), 300 - (i * 80)))


def create_enemies():
    enemies.clear()
    for i in range(8):
        enemies.append(
            Enemy(
                random.randint(30, WIDTH - 30), 50 + (i * 80) + random.randint(-30, 30)
            )
        )


def draw_menu():
    screen.fill((20, 30, 40))
    screen.draw.text(
        "Joguinho de Plataforma", center=(WIDTH // 2, 120), fontsize=24, color="white"
    )
    buttons = [
        (Rect((WIDTH // 2 - 50, 200), (100, 40)), (70, 130, 180), "Iniciar Jogo"),
        (
            Rect((WIDTH // 2 - 50, 260), (100, 40)),
            (70, 130, 180) if sound_enabled else (100, 100, 100),
            "Som Ligado" if sound_enabled else "Som Desligado",
        ),
        (Rect((WIDTH // 2 - 50, 320), (100, 40)), (150, 50, 50), "Sair"),
    ]
    for button, color, text in buttons:
        screen.draw.filled_rect(button, color)
        screen.draw.rect(button, "white")
        screen.draw.text(
            text,
            center=button.center,
            fontsize=20 if len(text) < 8 else 16,
            color="white",
        )


def draw_game():
    screen.fill((135, 206, 235))
    for platform in platforms:
        temp_platform = Actor("platform_gray")
        temp_platform.pos = (platform.actor.x, platform.actor.y - game_manager.camera_y)
        temp_platform.draw()
    for enemy in enemies:
        if not enemy.is_dying or enemy.blink_timer % 10 < 5:
            temp_enemy = Actor(enemy.actor.image)
            temp_enemy.pos = (enemy.actor.x, enemy.actor.y - game_manager.camera_y)
            temp_enemy.draw()
    if player.is_alive or player.blink_timer % 10 < 5:
        temp_player = Actor(player.actor.image)
        temp_player.pos = (player.actor.x, player.actor.y - game_manager.camera_y)
        temp_player.draw()
    screen.draw.text(
        f"Score: {game_manager.score}", (10, 10), fontsize=20, color="white"
    )


def draw():
    draw_menu() if game_state == MENU else draw_game()


def update():
    global game_state
    if game_state == PLAYING:
        player.update()
        if player.is_alive:
            game_manager.update_camera()
            game_manager.spawn_new_enemies()
            for enemy in enemies:
                enemy.update()
            game_manager.check_collisions()


def on_mouse_down(pos):
    global game_state, sound_enabled
    if game_state == MENU:
        buttons = [
            (Rect((WIDTH // 2 - 50, 200), (100, 40)), lambda: start_game()),
            (Rect((WIDTH // 2 - 50, 260), (100, 40)), lambda: toggle_sound()),
            (Rect((WIDTH // 2 - 50, 320), (100, 40)), lambda: exit()),
        ]
        for button, action in buttons:
            if button.collidepoint(pos):
                action()


def on_key_down(key):
    global game_state
    if game_state == MENU and key == keys.ENTER:
        start_game()
    elif game_state == PLAYING and key == keys.ESCAPE:
        game_state = MENU


def start_game():
    global game_state, player, platforms, enemies, game_manager
    game_state = PLAYING
    player = Player()
    platforms, enemies = [], []
    game_manager = GameManager()
    create_platforms()
    create_enemies()


def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    if sound_enabled:
        music.play("8bit-music-for-game-68698")
    else:
        music.stop()


player = Player()
platforms, enemies = [], []
game_manager = GameManager()
if sound_enabled:
    music.play("8bit-music-for-game-68698")
pgzrun.go()

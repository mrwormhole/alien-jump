from enum import IntEnum

import pygame as pg
from settings import (
    BLACK,
    WHITE,
    WIDTH,
    HEIGHT,
    PLAYER_GRAVITY,
    PLAYER_FRICTION,
    PLAYER_ACCELERATION,
    PLAYER_JUMP_SPEED,
)
import random
from random import choice
from os import path

Vector2 = pg.math.Vector2
Sprite = pg.sprite.Sprite
img_dir = path.join(path.dirname(__file__), "img")


class Layer(IntEnum):
    BACKGROUND = 0  # Clouds - visual only, no collision
    TERRAIN = 1  # Platforms and powerups
    ENTITY = 2  # Player and mobs


def load_cloud_sprites(img_directory: str) -> list[pg.Surface]:
    return [
        pg.image.load(path.join(img_directory, "cloud1.png")),
        pg.image.load(path.join(img_directory, "cloud2.png")),
        pg.image.load(path.join(img_directory, "cloud3.png")),
    ]


def load_player_sprites(img_filename: str) -> list[pg.Surface]:
    surface: pg.Surface = pg.image.load(img_filename).convert_alpha()

    def get_image(x: float, y: float, width: float, height: float) -> pg.surface:
        image = pg.Surface((width, height), pg.SRCALPHA, 32)
        image.blit(surface, (0, 0), (x, y, width, height))
        return pg.transform.scale(image, (55, 52))

    sprites = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    m = 0  # 0 to 5 are walking left anims, 6 to 11 are walking right anims.
    for y in range(0, 1678, 559):
        for x in range(0, 1061, 530):
            sprites[m] = get_image(x, y, 529, 558)
            m += 1
    return sprites


class Player(Sprite):
    def __init__(self, game):
        self._layer = Layer.ENTITY
        self.groups = game.all_sprites
        super().__init__(self.groups)
        self.spritesheet = load_player_sprites(
            path.join(img_dir, "spritesheet.png")
        )
        self.walking = False
        self.jumping = False
        self.standing_frame = 0
        self.current_frame = 0
        self.last_update = 0
        self.image = self.spritesheet[0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.pos = Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)
        self.now = 0

    def jump(self):
        self.vel.y -= PLAYER_JUMP_SPEED

    def update(self):
        self.acc = Vector2(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        self.animate()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_ACCELERATION
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = PLAYER_ACCELERATION
        """if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_ACCELERATION
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc.y = PLAYER_ACCELERATION"""

        self.acc.x += self.vel.x * PLAYER_FRICTION  # F = k . N
        self.vel += self.acc  # v = at
        self.pos += self.vel + 0.5 * self.acc  # x = vt + 1/2att

        if self.pos.x - self.rect.width / 2 > WIDTH:
            self.pos.x = 0 - self.rect.width / 2
        if self.pos.x + self.rect.width < 0:
            self.pos.x = WIDTH + self.rect.width / 2

        self.rect.midbottom = (int(self.pos.x), int(self.pos.y))

    def animate(self):
        self.now = pg.time.get_ticks()

        if abs(self.vel.x) < 0.5:
            self.vel.x = 0
            self.walking = False
        if self.vel.x != 0:
            self.walking = True

        if self.walking:
            if self.now - self.last_update > 120:
                self.last_update = self.now
                self.current_frame = (self.current_frame + 1) % 6
                if self.vel.x > 0:
                    # walking right
                    self.standing_frame = 6
                    self.image = self.spritesheet[self.current_frame + 6]
                else:
                    # walking left
                    self.standing_frame = 0
                    self.image = self.spritesheet[self.current_frame]
        if not self.jumping and not self.walking:
            self.image = self.spritesheet[self.standing_frame]


class Cloud(Sprite):
    def __init__(self, game):
        self._layer = Layer.BACKGROUND
        self.groups = (game.all_sprites, game.all_clouds)
        super().__init__(*self.groups)
        self.game = game
        self.image = self.game.cloud_sprites[random.randrange(0, 3)]
        self.rect = self.image.get_rect()
        scale = random.randrange(50, 101) / 100
        self.image = pg.transform.scale(
            self.image, (int(self.rect.width * scale), int(self.rect.height * scale))
        )
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-500, -50)

    def update(self):
        if self.rect.top > HEIGHT * 3:
            self.kill()


class Platform(Sprite):
    def __init__(self, game, x, y, filename1, filename2):
        self._layer = Layer.TERRAIN
        self.groups = (game.all_sprites, game.all_platforms)
        super().__init__(*self.groups)
        self.game = game
        self.platforms_images = [
            pg.image.load(filename1).convert_alpha(),
            pg.image.load(filename2).convert_alpha(),
        ]
        self.image = self.platforms_images[random.randint(0, 1)]
        self.xList = [75, 100, 125, 150]
        self.yList = [40, 45, 50]
        self.image = pg.transform.scale(
            self.image,
            (self.xList[random.randint(0, 3)], self.yList[random.randint(0, 2)]),
        )
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        rng = random.randrange(100)
        if rng < 5:
            self.powerup = PowerUp(self.game, self)
        elif 5 <= rng < 20:
            self.coin = Coin(self.game, self)


class PowerUp(Sprite):
    def __init__(self, game, platform):
        self._layer = Layer.TERRAIN
        self.groups = (game.all_sprites, game.all_powerups)
        super().__init__(*self.groups)
        self.game = game
        self.platform = platform
        self.type = "boost"
        self.image = pg.transform.scale(
            pg.image.load(path.join(img_dir, "boost.png")), (40, 40)
        )
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 5

    def update(self):
        self.rect.bottom = self.platform.rect.top - 5
        if not self.game.all_platforms.has(self.platform):
            self.kill()


class Coin(Sprite):
    def __init__(self, game, platform):
        self._layer = Layer.TERRAIN
        self.groups = (game.all_sprites, game.all_powerups)
        super().__init__(*self.groups)
        self.game = game
        self.platform = platform
        self.type = "coin"
        self.image = pg.transform.scale(
            pg.image.load(path.join(img_dir, "coin.png")), (40, 40)
        )
        self.rect = self.image.get_rect()
        self.rect.centerx = self.platform.rect.centerx
        self.rect.bottom = self.platform.rect.top - 5

    def update(self):
        self.rect.bottom = self.platform.rect.top - 5
        if not self.game.all_platforms.has(self.platform):
            self.kill()


class FlyingMob(Sprite):
    def __init__(self, game):
        self._layer = Layer.ENTITY
        self.groups = (game.all_sprites, game.all_mobs)
        super().__init__(*self.groups)
        self.game = game
        self.now = 0
        self.last_update = 0
        self.current_frame = 0
        self.image_idle_frame_1 = pg.transform.scale(
            pg.image.load(path.join(img_dir, "idle-frame-1.png")), (40, 40)
        )
        self.image_idle_frame_2 = pg.transform.scale(
            pg.image.load(path.join(img_dir, "idle-frame-2.png")), (40, 40)
        )
        self.idle_frames = [self.image_idle_frame_1, self.image_idle_frame_2]
        self.image = self.image_idle_frame_1
        self.rect = self.image.get_rect()
        self.rect.centerx = choice([-100, WIDTH + 100])
        self.velocityX = random.randrange(2, 6)
        if self.rect.centerx > WIDTH:
            self.velocityX *= -1
        self.rect.y = random.randrange(0, HEIGHT * 3 // 4)
        self.velocityY = 0
        self.dy = 0.5

    def update(self):
        self.now = pg.time.get_ticks()
        if self.now - self.last_update > 120:
            self.last_update = self.now
            self.current_frame = (self.current_frame + 1) % 2
            if self.velocityX < 0:
                self.image = pg.transform.flip(
                    self.idle_frames[self.current_frame], False, False
                )
            elif self.velocityY < 0:
                self.image = pg.transform.flip(
                    self.idle_frames[self.current_frame], True, False
                )

        self.rect.x += self.velocityX
        self.velocityY += self.dy
        self.rect.y += self.velocityY
        if self.velocityY > 3.5 or self.velocityY < -3.5:
            self.dy *= -1
        if self.rect.left > WIDTH + 150 or self.rect.right < -150:
            self.kill()


class InputBox:
    def __init__(self, x, y, w, h, screen, text=""):
        self.rect = pg.Rect(x, y, w, h)
        self.screen = screen
        self.COLOR_INACTIVE = WHITE
        self.COLOR_ACTIVE = BLACK
        self.FONT = pg.font.Font(None, 32)
        self.color = self.COLOR_INACTIVE
        self.text = text
        self.text_surface = self.FONT.render(text, True, self.color)
        self.active = False
        self.isSubmitted = False
        self.username = ""

    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.COLOR_ACTIVE if self.active else self.COLOR_INACTIVE
        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    if self.text != "":
                        self.isSubmitted = True
                        self.username = self.text
                    self.text = ""
                elif event.key == pg.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.text_surface = self.FONT.render(self.text, True, self.color)

    def update(self):
        width = max(200, self.text_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.text_surface, (self.rect.x + 5, self.rect.y + 5))
        # Blit the rect.
        pg.draw.rect(self.screen, self.color, self.rect, 2)

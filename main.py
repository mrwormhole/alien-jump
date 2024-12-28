import pygame as pg
import random
from os import path

from highscores import HighscoreDB
from settings import (
    WIDTH,
    HEIGHT,
    TITLE,
    FONT,
    JUMP_SOUND,
    MENU_MUSIC,
    THEME_MUSIC,
    PLATFORM_LIST,
    GRASS_TILE,
    STONE_TILE,
    FPS,
    BOOST_POWER,
    GREY,
    WHITE,
    YELLOW,
    BLACK,
)
from sprites import Player, Platform, Cloud, InputBox, FlyingMob, load_cloud_sprites

mixer = pg.mixer
display = pg.display
img_dir = path.join(path.dirname(__file__), "img")
sound_dir = path.join(path.dirname(__file__), "sound")


class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pg.init()
        self.screen = display.set_mode((WIDTH, HEIGHT))
        display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.font = pg.font.match_font(FONT)
        self.running = True
        self.state = GameState.MENU

        self.db = HighscoreDB()

        self.load_assets()
        self.reset()

    def load_assets(self):
        self.cloud_sprites = load_cloud_sprites(img_dir)
        self.jump_sound = mixer.Sound(path.join(sound_dir, JUMP_SOUND))
        self.menu_music = path.join(sound_dir, MENU_MUSIC)
        self.game_music = path.join(sound_dir, THEME_MUSIC)

    def load_highscore(self):
        (name, highscore) = self.db.highest_score()
        self.name = name
        self.highscore = highscore

    def reset(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.all_platforms = pg.sprite.Group()
        self.all_powerups = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_clouds = pg.sprite.Group()
        self.player = Player(self)
        self.score = 0
        self.mob_timer = 0
        self.input_box = InputBox(WIDTH / 2 - 100, HEIGHT * 3 / 4, 140, 32, self.screen, "")
        self.load_highscore()

        for platform in PLATFORM_LIST:
            Platform(
                self,
                platform[0],
                platform[1],
                path.join(img_dir, GRASS_TILE),
                path.join(img_dir, STONE_TILE),
            )

        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500

    def run(self):
        mixer.music.load(self.menu_music)
        mixer.music.play(loops=-1)

        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pg.quit()

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                self.running = False
                return

            if self.state == GameState.PLAYING:
                self.handle_playing_events(event)
            elif self.state == GameState.GAME_OVER:
                self.handle_game_over_events(event)
            elif self.state == GameState.MENU:
                self.handle_menu_events(event)

    def handle_playing_events(self, event):
        if event.type == pg.KEYDOWN:
            hits = pg.sprite.spritecollide(self.player, self.all_platforms, False)
            if hits:
                self.player.walking = True
                self.player.jumping = False
                if event.key == pg.K_SPACE:
                    self.player.jump()
                    self.jump_sound.play()
                    self.player.walking = False
                    self.player.jumping = True

    def handle_game_over_events(self, event):
        if self.score > self.highscore:
            self.input_box.events(event)
            if self.input_box.isSubmitted:
                self.db.add_score(self.input_box.username, self.score)
                self.state = GameState.MENU
                mixer.music.load(self.menu_music)
                mixer.music.play(loops=-1)
        elif event.type == pg.KEYUP:
            self.state = GameState.MENU
            mixer.music.load(self.menu_music)
            mixer.music.play(loops=-1)

    def handle_menu_events(self, event):
        if event.type == pg.KEYUP:
            self.state = GameState.PLAYING
            mixer.music.load(self.game_music)
            mixer.music.play(loops=-1)
            self.reset()

    def update(self):
        if self.state == GameState.PLAYING:
            self.update_playing()
        elif self.state == GameState.GAME_OVER:
            if self.score > self.highscore:
                self.input_box.update()

    def update_playing(self):
        self.all_sprites.update()

        # Spawn mobs
        now = pg.time.get_ticks()
        if now - self.mob_timer > 4000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            FlyingMob(self)

        # Check mob collisions
        mob_hits_bounding_box = pg.sprite.spritecollide(self.player, self.all_mobs, False)
        if mob_hits_bounding_box:
            mob_hits_pixel_perfect = pg.sprite.spritecollide(self.player, self.all_mobs, False, pg.sprite.collide_mask)
            if mob_hits_pixel_perfect:
                self.state = GameState.GAME_OVER
                return

        # check if player hits a platform - only if falling
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.all_platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if lowest.rect.right + 10 > self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0

        # check if player reaches top 1/4 of the screen
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 18:
                Cloud(self)
            scroll_speed = max(abs(self.player.vel.y), 2)
            self.player.pos.y += scroll_speed

            for sprite in [*self.all_clouds, *self.all_mobs]:
                sprite.rect.y += scroll_speed

            for plat in self.all_platforms:
                plat.rect.y += scroll_speed
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += random.randrange(10, 20)

        # if player picks a power up
        powerup_hits = pg.sprite.spritecollide(self.player, self.all_powerups, True)
        for powerup_hit in powerup_hits:
            if powerup_hit.type == "boost":
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
            elif powerup_hit.type == "coin":
                self.score += 100

        # game over for falling
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.all_platforms) == 0:
            self.state = GameState.GAME_OVER
            return

        # spawning new platforms
        while len(self.all_platforms) < 7:
            Platform(
                self,
                random.randrange(0, WIDTH - random.randrange(50, 100)),
                random.randrange(-75, -30),
                path.join(img_dir, GRASS_TILE),
                path.join(img_dir, STONE_TILE),
            )

    def draw(self):
        self.screen.fill(GREY)

        if self.state == GameState.PLAYING:
            self.draw_playing()
        elif self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()

        display.flip()

    def draw_playing(self):
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), WIDTH // 2, 5, 30, YELLOW)

    def draw_menu(self):
        self.draw_text(TITLE, WIDTH // 2, HEIGHT // 4, 48, WHITE)
        self.draw_text("[A] and [D] to move, [SPACE] to jump", WIDTH // 2, HEIGHT // 2, 22, WHITE)
        self.draw_text("Press any key to play", WIDTH // 2, HEIGHT * 3 // 4, 22, WHITE)
        if self.name and self.highscore:
            self.draw_text(f"Highscore ({self.name}:{self.highscore})", WIDTH // 2, 15, 22, BLACK)

    def draw_game_over(self):
        self.draw_text("GAME OVER", WIDTH // 2, HEIGHT // 4, 48, BLACK)
        self.draw_text("Score: " + str(self.score), WIDTH // 2, HEIGHT // 2, 22, BLACK)

        self.load_highscore()
        if self.score > self.highscore:
            self.draw_text("NEW HIGHSCORE!", WIDTH // 2, HEIGHT * 10 // 16, 22, WHITE)
            self.input_box.draw(self.screen)
        else:
            self.draw_text(
                "Press any key to return to menu",
                WIDTH // 2,
                HEIGHT * 3 // 4,
                22,
                BLACK,
            )

    def draw_text(self, text: str, x: int, y: int, size: int, color: tuple[int, int, int]):
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    game = Game()
    game.run()

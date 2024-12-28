import pygame as pg
import random
from os import path

from highscores import HighscoreDB
from settings import *
from sprites import Player, Platform, Cloud, InputBox, FlyingMob, load_cloud_sprites

mixer = pg.mixer
display = pg.display
img_dir = path.join(path.dirname(__file__), "img")
sound_dir = path.join(path.dirname(__file__), "sound")

class Game:
    def __init__(self):
        pg.init()
        self.screen = display.set_mode((WIDTH,HEIGHT))
        display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.font = pg.font.match_font(FONT)
        self.running = True

        self.db = HighscoreDB()
        (name, highscore) = self.db.highest_score()
        self.name = name
        self.highscore = highscore

        self.cloud_sprites = load_cloud_sprites(img_dir)
        self.jump_sound = mixer.Sound(path.join(sound_dir,JUMP_SOUND))
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.all_platforms = pg.sprite.Group()
        self.all_powerups = pg.sprite.Group()
        self.all_mobs = pg.sprite.Group()
        self.all_clouds = pg.sprite.Group()
        self.player = Player(self)
        self.score = 0
        self.mob_timer = 0
        self.input_box = InputBox(WIDTH / 2 - 100, HEIGHT * 3 / 4, 140, 32, self.screen, "enter your name")

        for platform in PLATFORM_LIST:
            Platform(self, platform[0], platform[1], path.join(img_dir, GRASS_TILE), path.join(img_dir, STONE_TILE))

        mixer.music.load(path.join(sound_dir, THEME_MUSIC))

        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500

    def run(self):
        self.playing = True
        mixer.music.play(loops=-1)
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        mixer.stop()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pg.KEYDOWN:
                hits = pg.sprite.spritecollide(self.player,self.all_platforms,False)
                if hits:
                    self.player.walking = True
                    self.player.jumping = False
                if event.key == pg.K_SPACE and hits:
                    self.player.jump()
                    self.jump_sound.play()
                    self.player.walking = False
                    self.player.jumping = True

    def update(self):
        self.all_sprites.update()

        # spawning a mob
        now = pg.time.get_ticks()
        if now - self.mob_timer > 4000 + random.choice([-1000,-500, 0,500,1000]):
            self.mob_timer = now
            FlyingMob(self)

        # check if player hits a mob
        mob_hits_bounding_box = pg.sprite.spritecollide(self.player,self.all_mobs,False)
        if mob_hits_bounding_box:
            mob_hits_pixel_perfect = pg.sprite.spritecollide(self.player,self.all_mobs,False,pg.sprite.collide_mask)
            if mob_hits_pixel_perfect:
                self.playing = False

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
        if self.player.rect.top <= HEIGHT/4:
            if random.randrange(100) < 18:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.all_clouds:
                cloud.rect.y += max(abs(self.player.vel.y/2), 2)
            for mob in self.all_mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.all_platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += random.randrange(10, 20)

        # if player picks a power up
        powerup_hits = pg.sprite.spritecollide(self.player,self.all_powerups, True)
        for powerup_hit in powerup_hits:
            if powerup_hit.type == "boost":
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False
            elif powerup_hit.type == "coin":
                self.score += 100

        # game over for falling
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y,10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.all_platforms) == 0:
            self.playing = False

        # spawning new platforms
        while len(self.all_platforms) < 7:
            Platform(self,random.randrange(0, WIDTH-random.randrange(50,100)),
                     random.randrange(-75, -30),
                     path.join(img_dir,GRASS_TILE),path.join(img_dir,STONE_TILE))

    def draw(self):
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), WIDTH/2, 5, 30, YELLOW)
        display.flip()

    def draw_text(self, text, x, y, size, color):
        font = pg.font.Font(self.font, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_any_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def wait_for_any_submit(self,inputBoxSubmitted):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pg.KEYUP and inputBoxSubmitted:
                    waiting = False

    def show_start_screen(self):
        mixer.music.load(path.join(sound_dir, MENU_MUSIC))
        mixer.music.play(loops=-1)
        self.screen.fill(GREY)
        self.draw_text(TITLE, WIDTH/2, HEIGHT/4, 48, WHITE)
        self.draw_text("[A] and [D] to move, [SPACE] to jump", WIDTH/2, HEIGHT/2, 22, WHITE)
        self.draw_text("Press any key to play", WIDTH / 2, HEIGHT * 3 / 4, 22, WHITE)
        if self.name and self.highscore:
            self.draw_text(f"Highscore | {self.name}:{self.highscore}", WIDTH / 2, 15, 22, BLACK)
        display.flip()
        self.wait_for_any_key()

    def show_game_over_screen(self):
        if not self.running:
            return # bug fix for closing game
        self.screen.fill(GREY)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGHSCORE!", WIDTH/2, HEIGHT/2 + 40, 22, BLACK)
            self.time_to_submit_to_the_database = True
        else:
            self.time_to_submit_to_the_database = False
            self.draw_text("Highscore: " + str(self.highscore), WIDTH / 2, HEIGHT/2 + 40, 22, BLACK)
        self.draw_text("GAME OVER", WIDTH / 2, HEIGHT / 4, 48, WHITE)
        self.draw_text("Score: " + str(self.score), WIDTH / 2, HEIGHT / 2, 22, WHITE)
        display.flip()

        if not self.time_to_submit_to_the_database:
            self.draw_text("Press any key to play again", WIDTH / 2, HEIGHT * 3 / 4, 22, WHITE)
            display.flip()
            self.wait_for_any_key()

        while self.time_to_submit_to_the_database:
            self.screen.fill(GREY)
            self.draw_text("NEW HIGHSCORE!", WIDTH / 2, HEIGHT / 2 + 40, 22, BLACK)
            self.draw_text("Enter your name to submit to the database", WIDTH / 2, HEIGHT / 2 + 100, 22, BLACK)
            self.draw_text("GAME OVER", WIDTH / 2, HEIGHT / 4, 48, BLACK)
            self.draw_text("Score: " + str(self.score), WIDTH / 2, HEIGHT / 2, 22, BLACK)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.time_to_submit_to_the_database = False
                    if self.playing:
                        self.playing = False
                    self.running = False

                self.input_box.events(event)
                self.input_box.update()
                self.input_box.draw(self.screen)
                # self.input_box.text = ""
                display.flip()
                if self.input_box.isSubmitted:
                    self.db.add_score(self.input_box.username, self.score)
                    self.time_to_submit_to_the_database = False
                    break


game = Game()
game.show_start_screen()
while game.running:
    game.run()
    game.show_game_over_screen()

pg.quit()

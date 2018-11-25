import pygame as pg
from settings import *
vector2 = pg.math.Vector2

class Spritesheet:
    def __init__(self,filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self,x,y,width,height):
        # make sure you test the rect boxes and images
        image = pg.Surface((width,height),pg.SRCALPHA,32)
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image,(55,52))
        return image

    def get_image2(self,index):
        return self.all_sprites[index]

    def fill_animation_sprites(self):
        self.all_sprites = [0,0,0,0,0,0,0,0,0,0,0,0]
        m = 0 # 0 to 5 are walking eft anims, 6 to 11 are walking right anims.Use 0 and 6 for left idle and right
        for y in range(0,1678,559):
            for x in range(0,1061,530):
                self.all_sprites[m] = self.get_image(x,y,529,558)
                m += 1

    ''' 
        def store_images(self):
        # defined values for w and h
        p = 0
        w = 529
        h = 558
        self.right_sprites = []
        self.left_sprites = []
        for i in range(0,7):
            self.left_sprites.append(pg.Surface((w,h)))
            #self.right_sprites.append(pg.Surface((w,h)))
        for y in range(0,560,559):
            for x in range(0,1061,530):
                self.left_sprites[p].blit(self.leftspritesheet,(0,0),(x,y,w,h))
                #self.right_sprites[p].blit(self.rightspritesheet,(0,0),(x,y,w,h))
                p += 1
        '''

class Player(pg.sprite.Sprite):
    def __init__(self,size,color,spritesheet):
        pg.sprite.Sprite.__init__(self)
        self.spritesheet = spritesheet
        self.spritesheet.fill_animation_sprites()
        self.walking = False
        self.jumping = False
        self.standing_frame = 0
        self.current_frame = 0
        self.last_update = 0
        self.size = size
        self.image = self.spritesheet.all_sprites[0] # pg.transform.scale(self.spritesheet.get_image(0,0,529,558),(55, 52))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH /2, HEIGHT /2)
        self.pos = vector2(WIDTH /2, HEIGHT/2)
        self.vel = vector2(0, 0)
        self.acc = vector2(0, 0)

    def jump(self):
        # observed a minor bug about jumping it is mostly related with collision detection.
        # set jump speed to 15 and acceleration to 0.25 to see that bug on first platform
        self.vel.y -= PLAYER_JUMP_SPEED

    def update(self):
        self.animate()
        self.acc = vector2(0, PLAYER_GRAVITY)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.acc.x = -PLAYER_ACCELERATION
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.acc.x = PLAYER_ACCELERATION
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.acc.y = -PLAYER_ACCELERATION
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.acc.y = PLAYER_ACCELERATION

        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc # for additional movement. Notice that it is missing time from physics
        '''if abs(self.vel.x) < 0.35:
            self.vel.x = 0'''
        self.pos += self.vel + 0.5 * self.acc # for additional movement Notice that it is missing time from physics

        if self.pos.x - self.size/2 > WIDTH: #self.rect.width / 2 could be better in future??
            self.pos.x = 0 - self.size/2
        if self.pos.x + self.size < 0:
            self.pos.x = WIDTH + self.size/2

        self.rect.midbottom = self.pos

    def animate(self):
        now = pg.time.get_ticks()

        if abs(self.vel.x) < 0.5:
            self.vel.x = 0
            self.walking = False
        if self.vel.x != 0:
            self.walking = True

        if self.walking:
            if now - self.last_update > 120:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % 6
                if self.vel.x > 0:
                    # walking right
                    self.standing_frame = 6
                    self.image = self.spritesheet.all_sprites[self.current_frame + 6]
                else:
                    # walking left
                    self.standing_frame = 0
                    self.image = self.spritesheet.all_sprites[self.current_frame]

        if not self.jumping and not self.walking:
            self.image = self.spritesheet.all_sprites[self.standing_frame]



class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((width,height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

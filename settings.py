TITLE = "Mysterious Jump"
WIDTH = 800
HEIGHT = 600
FPS = 30
FONT_NAME = "arial"
HIGHSCORE_FILE = "highscore.txt"
SPRITESHEET = "spritesheet.png"
GREY = (128, 128, 128)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
TURQUOISE = (0, 255, 255)
PINK = (255, 0, 255)
PLAYER_ACCELERATION = 0.50 # it was 0.25
PLAYER_FRICTION = -0.1
PLAYER_GRAVITY = 0.5
PLAYER_JUMP_SPEED = 18 # it was 12
PLATFORM_LIST = [ (0, HEIGHT-40, WIDTH, 40, PINK), # base ground
                  (WIDTH/2-50, HEIGHT*3/4, 100, 20, PINK), # 450
                  (200, HEIGHT*2/4+50, 100, 20, PINK), # 350
                  (350, HEIGHT*2/4-50, 100, 20, PINK), # 250
                  (200, HEIGHT*1/4, 100, 20, PINK), # 150
                  (350, HEIGHT*1/4-100, 100, 20, PINK), # 50
                  (200, HEIGHT*1/4-200, 100, 20, PINK) ] # -50

TITLE: str = "Alien Jump"
WIDTH: int = 800
HEIGHT: int = 600
FPS: int = 40
FONT: str = "arial"
SPRITESHEET: str = "spritesheet.png"
GRASS_TILE: str = "grass_tile.png"
STONE_TILE: str = "stone_tile.png"
JUMP_SOUND: str = "jump.wav"
THEME_MUSIC: str = "theme.ogg"
MENU_MUSIC: str = "menu.wav"
BACKGROUND_COLOR: tuple[int, int, int] = (0, 168, 255)
GREY: tuple[int, int, int] = BACKGROUND_COLOR  # (128, 128, 128)
WHITE: tuple[int, int, int] = (255, 255, 255)
BLACK: tuple[int, int, int] = (0, 0, 0)
RED: tuple[int, int, int] = (255, 0, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
BLUE: tuple[int, int, int] = (0, 0, 255)
YELLOW: tuple[int, int, int] = (255, 255, 0)
TURQUOISE: tuple[int, int, int] = (0, 255, 255)
PINK: tuple[int, int, int] = (255, 0, 255)
PLAYER_ACCELERATION: float = 0.50
PLAYER_FRICTION: float = -0.1
PLAYER_GRAVITY: float = 0.5
PLAYER_JUMP_SPEED: int = 18
PLATFORM_LIST: list[tuple[int, int]] = [
    (0, HEIGHT - 40),  # base ground
    (WIDTH / 2 - 50, HEIGHT * 3 / 4),  # 450
    (200, HEIGHT * 2 / 4 + 50),  # 350
    (350, HEIGHT * 2 / 4 - 50),  # 250
    (200, HEIGHT * 1 / 4, 100),  # 150
    (350, HEIGHT * 1 / 4 - 100),  # 50
    (200, HEIGHT * 1 / 4 - 200),  # -50
]
BOOST_POWER: int = 40

"""
Cấu hình chung và các hằng số hệ thống cho dự án Treasure Hunt.
Bao gồm thông số màn hình, màu sắc, giá trị điểm số và định nghĩa các thực thể trên bản đồ.
"""

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 60

GRID_ORIGIN_X = 40
GRID_ORIGIN_Y = 60
MAX_BOARD_PIXEL = 600

PANEL_X = 670
PANEL_Y = 34
PANEL_WIDTH = 380
PANEL_HEIGHT = 652

ITEM_SPAWN_INTERVAL_TURNS = 2
MAX_ITEMS_ON_BOARD = 24
FREEZE_DURATION_TURNS = 3
AUTO_BOT_TURN_DELAY_MS = 180

TITLE = "Treasure Hunt"

WHITE = (233, 229, 220)
BLACK = (18, 16, 22)
LIGHT_GRAY = (16, 19, 28)
GRAY = (82, 78, 90)
DARK_GRAY = (38, 34, 44)

WALL_COLOR = (52, 55, 66)
FLOOR_COLOR = (58, 63, 74)
GRID_LINE = (88, 79, 100)
FREEZE_COLOR = (168, 110, 255)

PLAYER_COLORS = [
    (84, 150, 255),
    (214, 88, 88),
]
BOT_COLORS = [
    (231, 110, 86),
    (101, 149, 219),
]

ACCENT = (108, 78, 152)
ACCENT_DARK = (216, 171, 96)
PANEL_BG = (20, 24, 31)
CARD_BG = (31, 36, 46)
CARD_HIGHLIGHT = (42, 47, 61)
PANEL_BORDER = (86, 76, 99)
TEXT_PANEL = PANEL_BG
TEXT_MUTED = (179, 171, 189)
TEXT_SOFT = (137, 130, 148)
SUCCESS = (96, 173, 110)
DANGER = (214, 82, 111)
BOARD_FRAME = (57, 45, 55)
BOARD_SHADOW = (0, 0, 0, 90)

# Ký hiệu map trong grid:
#   # = tường
#   . = ô đi được
# Key/chest/item/player KHÔNG ghi trực tiếp trong grid; chúng nằm trong dict riêng của level/game.
WALL = "#"
EMPTY = "."

KEY_COLORS = [
    {"id": 1, "name": "Red", "rgb": (220, 60, 60)},
    {"id": 2, "name": "Blue", "rgb": (55, 125, 235)},
    {"id": 3, "name": "Yellow", "rgb": (245, 210, 45)},
    {"id": 4, "name": "Green", "rgb": (65, 175, 95)},
    {"id": 5, "name": "Black", "rgb": (30, 30, 35)},
    {"id": 6, "name": "White", "rgb": (240, 240, 235)},
]
KEY_COLOR_LOOKUP = {info["id"]: info for info in KEY_COLORS}

KEY_SCORE_BY_SIZE = {
    "small": 40,
    "medium": 70,
    "large": 110,
}

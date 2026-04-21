"""Các cấu hình và thông số chung của trò chơi"""

# Kích thước màn hình
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
FPS = 60

# Kích thước lưới
GRID_ORIGIN_X = 40
GRID_ORIGIN_Y = 60
MAX_BOARD_PIXEL = 600

# Kích thước ô vuông sẽ được tính toán dựa trên kích thước bản đồ và kích thước tối đa cho phép
PANEL_X = 670
PANEL_Y = 34
PANEL_WIDTH = 380
PANEL_HEIGHT = 652

# Thời gian tồn tại của vật phẩm đóng băng trên bản đồ (tính bằng số lượt)
ITEM_SPAWN_INTERVAL_TURNS = 4
FREEZE_DURATION_TURNS = 3

TITLE = "Treasure Hunt"

# Màu sắc
WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
LIGHT_GRAY = (224, 229, 236)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)

# Màu sắc cho các loại gạch và vật phẩm trên bản đồ, cũng như màu sắc cho người chơi và bot. 
# Các màu sắc này được chọn để tạo ra một thiết kế trực quan hấp dẫn và dễ nhận biết, 
# giúp người chơi dễ dàng phân biệt giữa các yếu tố khác nhau trên bản đồ và tạo ra một trải nghiệm chơi game thú vị.
WALL_COLOR = (111, 111, 118)
FLOOR_COLOR = (133, 233, 89)
GRID_LINE = (185, 197, 171)
KEY_COLOR = (240, 200, 60)
CHEST_COLOR = (150, 95, 40)
FREEZE_COLOR = (150, 110, 255)

# Màu sắc cho người chơi và bot, được sử dụng để tạo ra sự phân biệt rõ ràng giữa các nhân vật trong trò chơi. 
# Mỗi màu sắc được chọn để phù hợp với phong cách nghệ thuật của trò chơi và tạo ra một trải nghiệm trực quan hấp dẫn cho người chơi.
PLAYER_COLORS = [
    (70, 140, 255),
    (255, 140, 80),
    (70, 200, 140),
    (190, 90, 255),
]
BOT_COLORS = [
    (220, 70, 70),
    (220, 110, 70),
    (190, 60, 120),
]

# Màu sắc cho các yếu tố giao diện người dùng như các nút, bảng điều khiển và văn bản. 
# Các màu sắc này được chọn để tạo ra một thiết kế trực quan hấp dẫn và dễ đọc, 
# giúp người chơi dễ dàng tương tác với giao diện người dùng và tạo ra một trải nghiệm chơi game thú vị.
ACCENT = (69, 109, 183)
ACCENT_DARK = (45, 78, 140)
PANEL_BG = (247, 249, 252)
CARD_BG = (255, 255, 255)
CARD_HIGHLIGHT = (240, 245, 252)
PANEL_BORDER = (200, 208, 220)
TEXT_PANEL = PANEL_BG
TEXT_MUTED = (92, 102, 118)
TEXT_SOFT = (130, 138, 148)
SUCCESS = (73, 171, 92)
DANGER = (195, 78, 78)
BOARD_FRAME = (96, 76, 56)
BOARD_SHADOW = (0, 0, 0, 35)

# Ký hiệu cho các loại ô trên bản đồ, giúp người chơi dễ dàng nhận biết và phân biệt giữa các loại ô khác nhau. 
# Các ký hiệu này được sử dụng trong quá trình hiển thị bản đồ và tạo ra một trải nghiệm chơi game trực quan và dễ hiểu.
WALL = "#"
EMPTY = "."
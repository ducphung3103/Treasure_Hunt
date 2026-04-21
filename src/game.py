"""Code chính của trò chơi, bao gồm vòng lặp chính, xử lý sự kiện, cập nhật trạng thái trò chơi, và vẽ giao diện người dùng."""

from __future__ import annotations

import random
import pygame

# Các import từ các module khác trong dự án, bao gồm quản lý tài nguyên (GameAssets), cấu hình chung (config), các thực thể trong trò chơi (entities), quản lý vật phẩm (items), dữ liệu bản đồ (map_data) và giao diện người dùng (ui). Những module này giúp tổ chức mã nguồn một cách rõ ràng và tách biệt các phần khác nhau của trò chơi, làm cho mã dễ đọc và bảo trì hơn.
from .assets import GameAssets
from .config import (
    BLACK,
    BOARD_FRAME,
    BOARD_SHADOW,
    BOT_COLORS,
    FPS,
    GRID_ORIGIN_X,
    GRID_ORIGIN_Y,
    ITEM_SPAWN_INTERVAL_TURNS,
    LIGHT_GRAY,
    PLAYER_COLORS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
)
from .entities import Bot, Player
from .items import ItemSpawner
from .map_data import get_level, get_map_size_option
from .ui import draw_legend, draw_menu, draw_round_rect, draw_side_panel

# Các chế độ về độ khó theo số lượng bước được di chuyển
STEP_OPTIONS = [
    {"label": "60 Turns", "turn_limit": 60},
    {"label": "90 Turns", "turn_limit": 90},
    {"label": "120 Turns", "turn_limit": 120},
    {"label": "150 Turns", "turn_limit": 150},
]

# Các chế độ về số lượng người chơi và bot tham gia
GAME_MODES = [
    {"label": "1 Player + 1 Bot", "humans": 1, "bots": 1},
    {"label": "1 Player + 2 Bots", "humans": 1, "bots": 2},
    {"label": "1 Player + 3 Bots", "humans": 1, "bots": 3},
    {"label": "2-Player Versus", "humans": 2, "bots": 0},
]

# Bảng màu để UI tạo ra người chơi, bot, vật phẩm, chìa khóa, rương, v.v. 
PLAYER_PALETTES = [
    {"skin": (240, 205, 173), "hair": (70, 45, 28), "outfit": (69, 135, 237), "accent": (255, 213, 73), "pants": (40, 66, 122)},
    {"skin": (227, 186, 156), "hair": (48, 38, 34), "outfit": (53, 183, 125), "accent": (255, 244, 171), "pants": (34, 88, 60)},
]
BOT_PALETTES = [
    {"skin": (219, 185, 154), "hair": (43, 28, 25), "outfit": (224, 91, 71), "accent": (67, 17, 17), "pants": (91, 36, 30)},
    {"skin": (223, 196, 166), "hair": (33, 31, 36), "outfit": (176, 77, 209), "accent": (91, 41, 102), "pants": (67, 31, 84)},
    {"skin": (229, 191, 160), "hair": (53, 35, 22), "outfit": (241, 140, 53), "accent": (140, 64, 16), "pants": (99, 55, 24)},
]


class Game:
    def __init__(self):
        """
        Khởi tạo các thiết lập liên quan đến màn hình trò chơi, trạng thái game, fonts, và các thành phần chính.
        - Thiết lập kích thước cố định, sử dụng màn ảo canvas và cho phép thay đổi kích thước bằng RESIZABLE.
        - Quản lý thời gian, tốc độ qua clock.tick(FPS).
        - Quản lý trạng thái, chế độ chơi, người chơi, vật phẩm, rương báu.
        """
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.virtual_width = SCREEN_WIDTH
        self.virtual_height = SCREEN_HEIGHT
        self.canvas = pygame.Surface((self.virtual_width, self.virtual_height))
        self.screen = pygame.display.set_mode((self.virtual_width, self.virtual_height), pygame.RESIZABLE)
        self.viewport = pygame.Rect(0, 0, self.virtual_width, self.virtual_height)
        self.update_viewport()

        self.clock = pygame.time.Clock()
        self.assets = GameAssets(40)
        self.fonts = {
            "tiny": pygame.font.SysFont("arial", 11, bold=True),
            "small": pygame.font.SysFont("arial", 14),
            "normal": pygame.font.SysFont("arial", 18),
            "title": pygame.font.SysFont("arial", 24, bold=True),
            "display": pygame.font.SysFont("arial", 34, bold=True),
            "button": pygame.font.SysFont("arial", 16, bold=True),
        }

        self.running = True
        self.state = "menu"
        self.selected_map_size_index = 0
        self.selected_mode_index = 0
        self.selected_step_index = 1
        self.current_seed = 1
        self.menu_buttons = {}
        self.game_buttons = {}

        self.characters = []
        self.items = []
        self.keys = {}
        self.chests = {}
        self.grid = []
        self.level_name = ""
        self.item_spawner = None
        self.turn_count = 0
        self.game_over = False
        self.winner_text = ""
        self.pending_human_moves = {}
        self.tile_size = 40
        self.rows = 15
        self.cols = 15
        self.grid_pixel_width = self.cols * self.tile_size
        self.grid_pixel_height = self.rows * self.tile_size

    @property
    def current_mode(self):
        """Điều chỉnh chế độ game (chơi với máy hoặc người)"""
        return GAME_MODES[self.selected_mode_index] 

    @property
    def current_map_size(self):
        """Điều chỉnh độ rộng map tùy ý"""
        return get_map_size_option(self.selected_map_size_index) 

    @property
    def current_step_option(self):
        """Điều chỉnh số lượng bước di chuyển tối đa"""
        return STEP_OPTIONS[self.selected_step_index]
    
    def update_viewport(self):
        """Cập nhật viewport để theo dõi kích thước cửa sổ hiện tại, đảm bảo game chạy bình thường, các vị trí, các đối tượng bình thường"""
        win_w, win_h = self.screen.get_size()
        self.viewport = pygame.Rect(0, 0, max(1, win_w), max(1, win_h))

    def to_virtual_pos(self, mouse_pos):
        """Chuyển đổi vị trí chuột từ tọa độ cửa sổ sang tọa độ ảo của trò chơi, đảm bảo các tương tác chuột chính xác bất kể kích thước cửa sổ"""
        if self.viewport.w <= 0 or self.viewport.h <= 0:
            return None
        rel_x = mouse_pos[0] / self.viewport.w
        rel_y = mouse_pos[1] / self.viewport.h
        x = int(rel_x * self.virtual_width)
        y = int(rel_y * self.virtual_height)
        return x, y

    def start_new_game(self):
        """Bắt đầu một trò chơi mới với thiết lập seed ngẫu nhiên, đảm bảo sau mỗi lần chơi lại sẽ có một bản đồ mới"""
        self.state = "playing"
        self.current_seed = random.randint(1, 999999)
        self.reset()

    def reset(self):
        """Thiết lập lại trò chơi về trạng thái ban đầu"""
        level = get_level(self.current_seed, self.selected_map_size_index)
        self.level_name = level["name"]
        self.grid = level["grid"]
        self.keys = level["keys"]
        self.chests = level["chests"]
        self.items = []
        self.characters = []
        self.turn_count = 0
        self.pending_human_moves = {}
        self.tile_size = level["tile_size"]
        self.rows = level["rows"]
        self.cols = level["cols"]
        self.grid_pixel_width = self.cols * self.tile_size
        self.grid_pixel_height = self.rows * self.tile_size
        self.assets = GameAssets(self.tile_size)

        starts = level["start_positions"]
        humans = self.current_mode["humans"]
        bots = self.current_mode["bots"]

        for i in range(humans):
            sprite = self.assets.make_character_sprite(PLAYER_PALETTES[i % len(PLAYER_PALETTES)], kind="player")
            self.characters.append(Player(f"P{i + 1}", starts[i], PLAYER_COLORS[i % len(PLAYER_COLORS)], sprite, control_index=i))

        for i in range(bots):
            sprite = self.assets.make_character_sprite(BOT_PALETTES[i % len(BOT_PALETTES)], kind="bot")
            self.characters.append(Bot(f"Bot {i + 1}", starts[humans + i], BOT_COLORS[i % len(BOT_COLORS)], sprite))

        self.item_spawner = ItemSpawner(level["item_spawn_points"])
        self.game_over = False
        self.winner_text = ""

    def next_map(self):
        """Chuyển sang bản đồ tiếp theo với seed ngẫu nhiên mới"""
        self.current_seed = random.randint(1, 999999)
        if self.state == "playing":
            self.reset()

    def previous_size(self):
        """Hàm điều chỉnh lùi kích thước map, thao tác vòng tròn bằng module (%)"""
        self.selected_map_size_index = (self.selected_map_size_index - 1) % 3

    def next_size(self):
        """Hàm điều chỉnh tiến kích thước map"""
        self.selected_map_size_index = (self.selected_map_size_index + 1) % 3

    def next_mode(self):
        """Hàm điều chỉnh tiến chế độ chơi"""
        self.selected_mode_index = (self.selected_mode_index + 1) % len(GAME_MODES)

    def previous_steps(self):
        """Hàm điều chỉnh lùi số lượng bước di chuyển tối đa"""
        self.selected_step_index = (self.selected_step_index - 1) % len(STEP_OPTIONS)

    def next_steps(self):
        """Hàm điều chỉnh tiến số lượng bước di chuyển tối đa"""
        self.selected_step_index = (self.selected_step_index + 1) % len(STEP_OPTIONS)

    def previous_mode(self):
        """Hàm điều chỉnh lùi chế độ chơi"""
        self.selected_mode_index = (self.selected_mode_index - 1) % len(GAME_MODES)

    def run(self):
        """
        Hàm chính của code, nơi mọi thứ diễn ra, bao gồm:
        - Vòng lặp chính của trò chơi, liên tục chạy cho đến khi tắt màn hình
        - Xử lý thao tác của người dùng (tắt, mở, thay đổi kích thước, nhấn phím, nhấn chuột)
        - Cập nhật trạng thái trò chơi (sau khi người chơi thực hiện, đổi map, ai thắng, hiển thị, ...)
        """
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        """
        Hàm xử lý sự kiện, bao gồm:
        - QUIT: Khi người chơi đóng cửa sổ, trò chơi sẽ dừng lại
        - VIDEORESIZE: Khi người chơi thay đổi kích thước cửa sổ, cập nhật viewport để đảm bảo mọi thứ hiển thị đúng
        - KEYDOWN: Khi người chơi nhấn phím, xử lý theo từng phím đã định nghĩa.
        - MOUSEBUTTONDOWN: Khi người chơi nhấn chuột, kiểm tra vị trí nhấn và thực hiện hành động tương ứng.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
                self.update_viewport()
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)

    def handle_keydown(self, key):
        """
        Hàm xử lý khi người chơi nhấn phím, bao gồm:
            - ESCAPE: Nếu đang chơi, sẽ về menu, nếu đang ở menu sẽ thoát trò chơi
            - R: Reset lại trò chơi hiện tại
            - M: Chuyển sang bản đồ tiếp theo
            - N: Quay về menu chính
            - Enter: Nếu game over, sẽ reset lại trò chơi
            - Các phím di chuyển: Điều khiển sự di chuyển của nhân vật.
        """
        if key == pygame.K_ESCAPE:
            if self.state == "playing":
                self.state = "menu"
            else:
                self.running = False
            return

        if self.state != "playing":
            return

        if key == pygame.K_r:
            self.reset()
            return
        if key == pygame.K_m:
            self.next_map()
            return
        if key == pygame.K_n:
            self.state = "menu"
            return
        if key == pygame.K_RETURN and self.game_over:
            self.reset()
            return
        if self.game_over:
            return

        for character in self.characters:
            if not isinstance(character, Player):
                continue
            direction = character.direction_from_key(key)
            if direction is not None:
                self.pending_human_moves[character.control_index] = direction
                if self.current_mode["humans"] == 1 or self.all_humans_ready():
                    self.execute_turn()
                return

    def handle_click(self, mouse_pos):
        """
        Hàm xử lý khi người chơi nhấn chuột, sẽ kiểm tra vị trí nhấn và thực hiện hành động tương ứng, bao gồm:
        - Nếu đang ở menu, sẽ kiểm tra xem người chơi có nhấn vào nút nào để thay đổi thiết lập
        - Nếu đang chơi, sẽ kiểm tra xem người chơi có nhấn vào nút nào để reset, đổi map, về menu, hoặc replay không.
        """
        virtual_pos = self.to_virtual_pos(mouse_pos)
        if virtual_pos is None:
            return
        if self.state == "menu":
            if self.menu_buttons.get("size_prev") and self.menu_buttons["size_prev"].collidepoint(virtual_pos):
                self.previous_size()
            elif self.menu_buttons.get("size_next") and self.menu_buttons["size_next"].collidepoint(virtual_pos):
                self.next_size()
            elif self.menu_buttons.get("mode_prev") and self.menu_buttons["mode_prev"].collidepoint(virtual_pos):
                self.previous_mode()
            elif self.menu_buttons.get("mode_next") and self.menu_buttons["mode_next"].collidepoint(virtual_pos):
                self.next_mode()
            elif self.menu_buttons.get("steps_prev") and self.menu_buttons["steps_prev"].collidepoint(virtual_pos):
                self.previous_steps()
            elif self.menu_buttons.get("steps_next") and self.menu_buttons["steps_next"].collidepoint(virtual_pos):
                self.next_steps()
            elif self.menu_buttons.get("start") and self.menu_buttons["start"].collidepoint(virtual_pos):
                self.start_new_game()
            return
        if self.game_buttons.get("reset") and self.game_buttons["reset"].collidepoint(virtual_pos):
            self.reset()
        elif self.game_buttons.get("next_map") and self.game_buttons["next_map"].collidepoint(virtual_pos):
            self.next_map()
        elif self.game_buttons.get("menu") and self.game_buttons["menu"].collidepoint(virtual_pos):
            self.state = "menu"
        elif self.game_buttons.get("replay") and self.game_buttons["replay"].collidepoint(virtual_pos):
            self.reset()

    def update(self):
        """Cập nhật các trạng thái (nếu có bổ sung logic chuyển động/hoạt ảnh). Hiện tại giữ trống."""
        return
  
    def all_humans_ready(self):
        """Hàm kiểm tra xem tất cả người chơi đã chọn hướng di chuyển nhằm đảm bảo sự công bằng"""
        humans = [character for character in self.characters if isinstance(character, Player)]
        return all(player.control_index in self.pending_human_moves for player in humans)

    def get_turns_left(self):
        """Hàm tính số lượt còn lại của trò chơi"""
        return max(0, self.current_step_option["turn_limit"] - self.turn_count)

    def execute_turn(self):
        """
        Hàm thực hiện một lượt chơi, bao gồm:
            - Kiểm tra nếu trò chơi đã kết thúc, nếu có thì không thực hiện gì cả
            - Thu thập hướng di chuyển của tất cả nhân vật. 
            - Xác định số bước tối đa mà bất kỳ nhân vật nào sẽ thực hiện trong lượt này.
            - Thực hiện từng bước di chuyển con (substep) cho tất cả nhân vật, đảm bảo công bằng.  
            - Xử lý các tương tác giữa nhân vật và môi trường hoặc giữa các nhân vật với nhau. 
            - Kết thúc lượt chơi, sinh vật phẩm mới nếu cần và kiểm tra điều kiện kết thúc.
        """
        if self.game_over:
            return

        directions = {}
        for character in self.characters:
            if isinstance(character, Player):
                directions[character] = self.pending_human_moves.get(character.control_index)
            else:
                directions[character] = character.choose_direction(self)

        max_steps = max((character.steps_this_turn() for character in self.characters), default=0)
        for step_index in range(max_steps):
            self.resolve_substep(directions, step_index)

        for character in self.characters:
            opponents = [c for c in self.characters if c is not character]
            self.handle_character_interactions(character, opponents)

        for character in self.characters:
            character.finish_turn()

        self.turn_count += 1
        self.pending_human_moves = {}
        self.spawn_items_if_needed()

        if not self.chests or self.get_turns_left() <= 0:
            self.end_game()

    def resolve_substep(self, directions, step_index):
        """Hàm giải quyết một bước di chuyển con (substep) cho tất cả nhân vật, đảm bảo rằng các di chuyển được giải quyết đồng thời và công bằng."""
        current_positions = {character: character.pos for character in self.characters}
        occupied = set(current_positions.values())
        proposals = {}

        for character in self.characters:
            if directions.get(character) is None:
                continue
            if step_index >= character.steps_this_turn():
                continue
            dx, dy = directions[character]
            target = (character.grid_x + dx, character.grid_y + dy)
            if not character.can_enter(target[0], target[1], self.grid, occupied - {character.pos}, self.chests):
                continue
            proposals[character] = target

        counts = {}
        for target in proposals.values():
            counts[target] = counts.get(target, 0) + 1

        for character, target in proposals.items():
            if counts[target] > 1:
                continue
            if target in occupied:
                continue
            character.move_to(target)

    def handle_character_interactions(self, character, opponents):
        """Hàm xử lý các tương tác giữa nhân vật và môi trường (nhặt chìa khóa, mở rương, sử dụng vật phẩm) cũng như giữa các nhân vật với nhau nếu có."""
        if character.held_key_id is None:
            picked_key_id = self.find_key_at_pos(character.pos)
            if picked_key_id is not None:
                character.held_key_id = picked_key_id
                del self.keys[picked_key_id]
        if character.held_key_id is not None:
            chest_id = self.find_chest_at_pos(character.pos)
            if chest_id is not None and chest_id == character.held_key_id:
                character.score += self.chests[chest_id]["score"]
                del self.chests[chest_id]
                character.held_key_id = None
        item = self.find_item_at_pos(character.pos)
        if item is not None:
            character.apply_item(item.type_name, opponents)
            self.items.remove(item)

    def find_key_at_pos(self, pos):
        """Hàm tìm kiếm chìa khóa tại vị trí cụ thể, trả về ID của chìa khóa nếu có, hoặc None nếu không có chìa khóa nào ở đó."""
        for key_id, info in self.keys.items():
            if info["pos"] == pos:
                return key_id
        return None

    def find_chest_at_pos(self, pos):
        """Hàm tìm kiếm rương tại vị trí cụ thể, trả về ID của rương nếu có, hoặc None nếu không có rương nào ở đó."""
        for chest_id, info in self.chests.items():
            if info["pos"] == pos:
                return chest_id
        return None

    def find_item_at_pos(self, pos):
        """Hàm tìm kiếm vật phẩm tại vị trí cụ thể, trả về đối tượng vật phẩm nếu có, hoặc None nếu không có vật phẩm nào ở đó."""
        for item in self.items:
            if item.pos == pos:
                return item
        return None
    
    def spawn_items_if_needed(self):
        """Hàm sinh ra vật phẩm mới trên bản đồ theo thời gian để đảm bảo tính công bằng cho trò chơi, sẽ được gọi sau mỗi lượt chơi."""
        if self.turn_count == 0 or self.turn_count % ITEM_SPAWN_INTERVAL_TURNS != 0:
            return
        if len(self.items) >= 2:
            return
        item = self.item_spawner.spawn_item(
            blocked_positions={c.pos for c in self.characters},
            existing_item_positions={it.pos for it in self.items},
        )
        if item is not None:
            self.items.append(item)

    def end_game(self):
        """Hàm kết thúc trò chơi, xác định người chiến thắng dựa trên điểm số của các nhân vật còn lại, và thiết lập winner_text để hiển thị kết quả."""
        self.game_over = True
        if not self.characters:
            self.winner_text = "No players"
            return
        best_score = max(character.score for character in self.characters)
        winners = [character.name for character in self.characters if character.score == best_score]
        if len(winners) == 1:
            self.winner_text = f"Result: {winners[0]} wins!"
        else:
            self.winner_text = f"Result: Draw between {', '.join(winners)}"

    def draw(self):
        """
        Hàm vẽ tất cả các thành phần của trò chơi, bao gồm:
        - Màn hình menu, lưới bản đồ, chìa khóa, rương, vật phẩm, nhân vật, bảng chú giải, và các nút tương tác trên side panel.
        - Nếu trò chơi kết thúc, sẽ vẽ một thông báo ở giữa màn hình để hiển thị kết quả.
        - Cuối cùng, gọi present để hiển thị tất cả những gì đã vẽ. 
        """
        if self.state == "menu":
            self.draw_menu_screen()
            self.present()
            return

        self.canvas.fill(LIGHT_GRAY)
        self.draw_grid()
        self.draw_keys()
        self.draw_chests()
        self.draw_items()
        for character in self.characters:
            character.draw(self.canvas, self.fonts["tiny"], self.assets, tile_size=self.tile_size, origin=(GRID_ORIGIN_X, GRID_ORIGIN_Y))
        draw_legend(self.canvas, self.fonts)
        self.game_buttons = draw_side_panel(self.canvas, self.fonts, self)
        if self.game_over:
            self.draw_center_message(self.winner_text)
        self.present()

    def present(self):
        """Hàm hiển thị tất cả những gì đã vẽ trên canvas lên màn hình"""
        target_size = self.screen.get_size()
        if target_size == self.canvas.get_size():
            self.screen.blit(self.canvas, (0, 0))
        else:
            scaled = pygame.transform.smoothscale(self.canvas, target_size)
            self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

    def draw_menu_screen(self):
        """Hàm vẽ màn hình chính của trò chơi, bao gồm các nút để thay đổi thiết lập (kích thước bản đồ, chế độ chơi, số lượt) và nút để bắt đầu trò chơi."""
        self.menu_buttons = draw_menu(
            self.canvas,
            self.fonts,
            size_label=self.current_map_size["label"],
            size_description=self.current_map_size["description"],
            mode_label=self.current_mode["label"],
            steps_label=self.current_step_option["label"],
        )

    def draw_grid(self):
        """Hàm vẽ lưới bản đồ, bao gồm việc vẽ nền, tường, và bóng đổ để tạo chiều sâu cho bản đồ."""
        frame = pygame.Rect(GRID_ORIGIN_X - 14, GRID_ORIGIN_Y - 14, self.grid_pixel_width + 28, self.grid_pixel_height + 28)
        shadow = pygame.Rect(frame.x + 6, frame.y + 8, frame.w, frame.h)
        draw_round_rect(self.canvas, shadow, BOARD_SHADOW, None, radius=20)
        draw_round_rect(self.canvas, frame, BOARD_FRAME, None, radius=18)
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                px = GRID_ORIGIN_X + x * self.tile_size
                py = GRID_ORIGIN_Y + y * self.tile_size
                if cell == "#":
                    self.canvas.blit(self.assets.wall_tile, (px, py))
                else:
                    self.canvas.blit(self.assets.floor_tile, (px, py))
                    self.canvas.blit(self.assets.shadow_tile, (px, py))

    def draw_keys(self):
        """Hàm vẽ chìa khóa trên bản đồ, sử dụng thông tin trong self.keys để xác định vị trí và loại chìa khóa, và vẽ chúng lên canvas."""
        for key_id, info in self.keys.items():
            px = GRID_ORIGIN_X + info["pos"][0] * self.tile_size
            py = GRID_ORIGIN_Y + info["pos"][1] * self.tile_size
            self.canvas.blit(self.assets.get_key_surface(key_id), (px, py))

    def draw_chests(self):
        """Hàm vẽ rương trên bản đồ, sử dụng thông tin trong self.chests để xác định vị trí và vẽ chúng lên canvas."""
        for chest_id, info in self.chests.items():
            px = GRID_ORIGIN_X + info["pos"][0] * self.tile_size
            py = GRID_ORIGIN_Y + info["pos"][1] * self.tile_size
            self.canvas.blit(self.assets.get_chest_surface(chest_id), (px, py))

    def draw_items(self):
        """Hàm vẽ vật phẩm trên bản đồ, sử dụng thông tin trong self.items để xác định vị trí và vẽ chúng lên canvas."""
        for item in self.items:
            px = GRID_ORIGIN_X + item.pos[0] * self.tile_size
            py = GRID_ORIGIN_Y + item.pos[1] * self.tile_size
            self.canvas.blit(self.assets.get_item_surface(item.type_name), (px, py))

    def draw_center_message(self, message):
        """Hàm vẽ thông báo kết quả (hoặc văn bản) lên chính giữa màn hình."""
        overlay = pygame.Rect(148, 272, 438, 124)
        draw_round_rect(self.canvas, overlay, (255, 255, 255), BLACK, radius=18, width=2)
        text = self.fonts["title"].render(message, True, BLACK)
        self.canvas.blit(text, text.get_rect(center=(overlay.centerx, overlay.y + 38)))
        tip = self.fonts["small"].render("Use Replay or Main Menu on the right.", True, BLACK)
        self.canvas.blit(tip, tip.get_rect(center=(overlay.centerx, overlay.y + 86)))
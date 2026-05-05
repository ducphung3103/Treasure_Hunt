"""Vòng lặp chính, menu, luật chơi và chế độ 2 player."""

from __future__ import annotations

import math
import random
import pygame

from .assets import GameAssets
from .config import (
    AUTO_BOT_TURN_DELAY_MS,
    BLACK,
    BOARD_FRAME,
    BOARD_SHADOW,
    BOT_COLORS,
    EMPTY,
    FPS,
    ITEM_SPAWN_INTERVAL_TURNS,
    KEY_COLOR_LOOKUP,
    MAX_ITEMS_ON_BOARD,
    PLAYER_COLORS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    TITLE,
)
from .entities import Bot, Player
from .items import ItemSpawner
from .map_data import MAP_SIZE_OPTIONS, get_level, get_map_size_option
from .pathfinding import bfs_shortest_path
from .ui import draw_background, draw_instructions, draw_legend, draw_menu, draw_round_rect, draw_side_panel

STEP_OPTIONS = [
    {"label": "100 Turns", "turn_limit": 100},
    {"label": "200 Turns", "turn_limit": 200},
    {"label": "300 Turns", "turn_limit": 300},
    {"label": "400 Turns", "turn_limit": 400},
]

PLAYER_TYPE_OPTIONS = ["Human", "Easy", "Medium", "Hard"]

PLAYER_PALETTES = [
    {"skin": (240, 205, 173), "hair": (70, 45, 28), "outfit": (69, 135, 237), "accent": (255, 213, 73), "pants": (40, 66, 122)},
    {"skin": (227, 186, 156), "hair": (48, 38, 34), "outfit": (220, 78, 78), "accent": (255, 244, 171), "pants": (105, 42, 42)},
]
BOT_PALETTES = [
    {"skin": (219, 185, 154), "hair": (43, 28, 25), "outfit": (224, 91, 71), "accent": (67, 17, 17), "pants": (91, 36, 30)},
    {"skin": (223, 196, 166), "hair": (33, 31, 36), "outfit": (64, 132, 213), "accent": (208, 233, 255), "pants": (34, 71, 125)},
]


class Game:
    """
    Lớp điều khiển chính của trò chơi Treasure Hunt.
    Quản lý trạng thái game, vòng lặp chính, xử lý sự kiện và vẽ giao diện.
    """
    def __init__(self):
        """Khởi tạo đối tượng Game, thiết lập Pygame, cửa sổ hiển thị và các tài nguyên cơ bản."""
        pygame.init()
        pygame.display.set_caption(TITLE)

        self.virtual_width = SCREEN_WIDTH
        self.virtual_height = SCREEN_HEIGHT
        self.canvas = pygame.Surface((self.virtual_width, self.virtual_height), pygame.SRCALPHA)
        self.screen = pygame.display.set_mode((self.virtual_width, self.virtual_height), pygame.RESIZABLE)
        self.viewport = pygame.Rect(0, 0, self.virtual_width, self.virtual_height)
        self.update_viewport()

        self.clock = pygame.time.Clock()
        self.assets = GameAssets(40)
        self.fonts = {
            "tiny": pygame.font.SysFont("arial", 11, bold=True),
            "small": pygame.font.SysFont("arial", 14),
            "normal": pygame.font.SysFont("arial", 17),
            "title": pygame.font.SysFont("arial", 23, bold=True),
            "display": pygame.font.SysFont("arial", 32, bold=True),
            "button": pygame.font.SysFont("arial", 16, bold=True),
        }

        self.running = True
        self.state = "menu"
        self.selected_map_size_index = 0
        self.selected_step_index = 1
        self.selected_player_type_indices = [0, 2]  # P1 Human, P2 Medium mặc định.
        self.selected_num_colors = 4
        self.selected_num_sizes = 3
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
        self.rows = 20
        self.cols = 20
        self.grid_pixel_width = self.cols * self.tile_size
        self.grid_pixel_height = self.rows * self.tile_size
        self.board_origin_x = 0
        self.board_origin_y = 0
        self.status_message = ""
        self.last_auto_turn_ms = 0
        self.autoplay = False

    @property
    def current_map_size(self):
        """Trả về cấu hình kích thước bản đồ hiện tại dựa trên chỉ mục đã chọn."""
        return get_map_size_option(self.selected_map_size_index)

    @property
    def current_step_option(self):
        """Trả về cấu hình giới hạn số lượt chơi hiện tại dựa trên chỉ mục đã chọn."""
        return STEP_OPTIONS[self.selected_step_index]

    def player_type(self, index):
        """
        Lấy kiểu người chơi (Human/Easy/Medium/Hard) tại vị trí chỉ định.
        
        Args:
            index (int): Chỉ mục của người chơi (0 hoặc 1).
            
        Returns:
            str: Tên kiểu người chơi.
        """
        return PLAYER_TYPE_OPTIONS[self.selected_player_type_indices[index] % len(PLAYER_TYPE_OPTIONS)]

    def mode_label(self):
        """Trả về chuỗi mô tả chế độ chơi hiện tại (ví dụ: 'P1 Human vs P2 Medium')."""
        return f"P1 {self.player_type(0)} vs P2 {self.player_type(1)}"

    def update_viewport(self):
        """Cập nhật kích thước và vị trí của viewport khi cửa sổ ứng dụng thay đổi kích thước."""
        win_w, win_h = self.screen.get_size()
        ratio = min(win_w / self.virtual_width, win_h / self.virtual_height)
        new_w = int(self.virtual_width * ratio)
        new_h = int(self.virtual_height * ratio)
        self.viewport = pygame.Rect((win_w - new_w) // 2, (win_h - new_h) // 2, new_w, new_h)

    def to_virtual_pos(self, mouse_pos):
        """
        Chuyển đổi tọa độ chuột thực tế sang tọa độ trong không gian ảo 1080x720.
        
        Args:
            mouse_pos (tuple): Tọa độ (x, y) của chuột trên cửa sổ.
            
        Returns:
            tuple hoặc None: Tọa độ ảo (x, y) hoặc None nếu viewport không hợp lệ.
        """
        if self.viewport.w <= 0 or self.viewport.h <= 0:
            return None
        return int((mouse_pos[0] - self.viewport.x) / self.viewport.w * self.virtual_width), \
               int((mouse_pos[1] - self.viewport.y) / self.viewport.h * self.virtual_height)

    def update_board_layout(self):
        """Tính toán vị trí gốc (góc trên bên trái) của bàn cờ để căn giữa trên màn hình ảo."""
        self.board_origin_x = (self.virtual_width - self.grid_pixel_width) // 2
        # Đảm bảo không quá cao và chừa chỗ cho legend/UI phía dưới
        self.board_origin_y = (self.virtual_height - self.grid_pixel_height) // 2 + 10

    def get_board_rect(self):
        """Trả về hình chữ nhật đại diện cho toàn bộ vùng bàn cờ trên màn hình ảo."""
        return pygame.Rect(self.board_origin_x, self.board_origin_y, self.grid_pixel_width, self.grid_pixel_height)

    def start_new_game(self):
        """Chuyển trạng thái sang 'playing', tạo seed ngẫu nhiên và khởi động lại trò chơi."""
        self.state = "playing"
        self.current_seed = random.randint(1, 999999)
        self.reset()

    def reset(self):
        """Khởi tạo lại toàn bộ dữ liệu trận đấu dựa trên cấu hình hiện tại (seed, map size, players)."""
        level = get_level(self.current_seed, self.selected_map_size_index, 
                          num_colors=self.selected_num_colors, 
                          num_sizes=self.selected_num_sizes)
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
        self.update_board_layout()

        starts = level["start_positions"]
        for i in range(2):
            p_type = self.player_type(i)
            is_human = p_type == "Human"
            palette = PLAYER_PALETTES[i] if is_human else BOT_PALETTES[i]
            sprite = self.assets.make_character_sprite(palette, kind="player" if is_human else "bot")
            if is_human:
                self.characters.append(Player(f"Player {i + 1}", starts[i], PLAYER_COLORS[i], sprite, control_index=i))
            else:
                self.characters.append(Bot(f"Player {i + 1} Bot", starts[i], BOT_COLORS[i], sprite, difficulty=p_type.lower()))

        self.item_spawner = ItemSpawner(level["item_spawn_points"])
        self.game_over = False
        self.winner_text = ""
        self.status_message = "Keys and chests use colors. Farther keys are larger and give more points."
        self.last_auto_turn_ms = pygame.time.get_ticks()

    def next_map(self):
        """Tạo một seed mới và reset game để chuyển sang bản đồ mới."""
        self.current_seed = random.randint(1, 999999)
        if self.state == "playing":
            self.reset()

    def previous_size(self):
        """Chọn kích thước bản đồ trước đó trong danh sách tùy chọn."""
        self.selected_map_size_index = (self.selected_map_size_index - 1) % 3

    def next_size(self):
        """Chọn kích thước bản đồ tiếp theo trong danh sách tùy chọn."""
        self.selected_map_size_index = (self.selected_map_size_index + 1) % 3

    def set_map_size(self, index):
        """Thiết lập kích thước bản đồ theo chỉ mục cụ thể."""
        self.selected_map_size_index = index % len(MAP_SIZE_OPTIONS)

    def previous_steps(self):
        """Chọn giới hạn lượt đi trước đó trong danh sách tùy chọn."""
        self.selected_step_index = (self.selected_step_index - 1) % len(STEP_OPTIONS)

    def next_steps(self):
        """Chọn giới hạn lượt đi tiếp theo trong danh sách tùy chọn."""
        self.selected_step_index = (self.selected_step_index + 1) % len(STEP_OPTIONS)

    def set_step_count(self, index):
        """Thiết lập giới hạn số lượt đi theo chỉ mục cụ thể."""
        self.selected_step_index = index % len(STEP_OPTIONS)

    def set_player_type(self, player_index, type_index):
        """Thiết lập kiểu người chơi cho một người chơi cụ thể (P1 hoặc P2)."""
        self.selected_player_type_indices[player_index] = type_index % len(PLAYER_TYPE_OPTIONS)

    def previous_player_type(self, index):
        """Chọn kiểu người chơi trước đó cho người chơi chỉ định."""
        self.selected_player_type_indices[index] = (self.selected_player_type_indices[index] - 1) % len(PLAYER_TYPE_OPTIONS)

    def next_player_type(self, index):
        """Chọn kiểu người chơi tiếp theo cho người chơi chỉ định."""
        self.selected_player_type_indices[index] = (self.selected_player_type_indices[index] + 1) % len(PLAYER_TYPE_OPTIONS)

    def run(self):
        """Vòng lặp thực thi chính của game: tick clock, xử lý sự kiện, cập nhật và vẽ màn hình."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()

    def handle_events(self):
        """Xử lý các sự kiện từ hệ thống như thoát, đổi kích thước cửa sổ, nhấn phím và chuột."""
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
        Xử lý sự kiện khi một phím được nhấn. Điều khiển di chuyển, reset, đổi map hoặc thoát.
        
        Args:
            key (int): Mã phím từ pygame.
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
        if key == pygame.K_SPACE and not self.game_over:
            if self.human_count() == 0 or not self.autoplay:
                self.execute_turn()
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
                if self.all_humans_ready():
                    self.execute_turn()
                return

    def handle_click(self, mouse_pos):
        """
        Xử lý sự kiện click chuột trái, xác định nút bấm nào được nhấn tùy theo trạng thái game.
        
        Args:
            mouse_pos (tuple): Tọa độ (x, y) của chuột trên màn hình thực tế.
        """
        virtual_pos = self.to_virtual_pos(mouse_pos)
        if virtual_pos is None:
            return
        if self.state == "menu":
            mapping = {
                "start": self.start_new_game,
                "instructions": lambda: setattr(self, 'state', 'instructions'),
            }
            for idx in range(len(STEP_OPTIONS)):
                mapping[f"steps_{idx}"] = lambda idx=idx: self.set_step_count(idx)
            for idx in range(len(MAP_SIZE_OPTIONS)):
                mapping[f"size_{idx}"] = lambda idx=idx: self.set_map_size(idx)
            for idx in range(len(PLAYER_TYPE_OPTIONS)):
                mapping[f"p1_{idx}"] = lambda idx=idx: self.set_player_type(0, idx)
                mapping[f"p2_{idx}"] = lambda idx=idx: self.set_player_type(1, idx)
            for idx in range(6):
                mapping[f"colors_{idx}"] = lambda idx=idx: setattr(self, 'selected_num_colors', idx + 1)
            for idx in range(3):
                mapping[f"ksizes_{idx}"] = lambda idx=idx: setattr(self, 'selected_num_sizes', idx + 1)
            for key, callback in mapping.items():
                rect = self.menu_buttons.get(key)
                if rect and rect.collidepoint(virtual_pos):
                    callback()
                    return
            return

        if self.state == "instructions":
            rect = self.menu_buttons.get("back")
            if rect and rect.collidepoint(virtual_pos):
                self.state = "menu"
            return

        if self.game_buttons.get("reset") and self.game_buttons["reset"].collidepoint(virtual_pos):
            self.reset()
        elif self.game_buttons.get("new_map") and self.game_buttons["new_map"].collidepoint(virtual_pos):
            self.next_map()
        elif self.game_buttons.get("autoplay") and self.game_buttons["autoplay"].collidepoint(virtual_pos):
            self.autoplay = not self.autoplay
            self.status_message = f"Autoplay: {'ON' if self.autoplay else 'OFF'}"
        elif self.game_buttons.get("menu") and self.game_buttons["menu"].collidepoint(virtual_pos):
            self.state = "menu"

    def update(self):
        """Cập nhật logic game mỗi frame, chủ yếu xử lý việc tự động chạy lượt của Bot."""
        if self.state != "playing" or self.game_over:
            return
        if not self.autoplay:
            return
        if self.human_count() != 0:
            return
        now = pygame.time.get_ticks()
        if now - self.last_auto_turn_ms >= AUTO_BOT_TURN_DELAY_MS:
            self.execute_turn()
            self.last_auto_turn_ms = now

    def human_count(self):
        """Trả về số lượng người chơi là con người hiện có trong game."""
        return sum(isinstance(character, Player) for character in self.characters)

    def all_humans_ready(self):
        """Kiểm tra xem tất cả người chơi con người đã nhập hướng di chuyển cho lượt này chưa."""
        humans = [character for character in self.characters if isinstance(character, Player)]
        return all(player.control_index in self.pending_human_moves for player in humans)

    def get_turns_left(self):
        """Tính toán số lượt chơi còn lại dựa trên giới hạn đã chọn."""
        return max(0, self.current_step_option["turn_limit"] - self.turn_count)

    def execute_turn(self):
        """
        Thực hiện một lượt chơi đầy đủ: thu thập nước đi, giải quyết va chạm,
        tương tác với vật phẩm/chìa khóa/rương và kiểm tra điều kiện kết thúc.
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
        """
        Giải quyết một bước nhỏ trong lượt (nếu một nhân vật có nhiều hơn 1 bước mỗi lượt).
        Xử lý va chạm giữa các nhân vật và với môi trường.
        
        Args:
            directions (dict): Từ điển ánh xạ nhân vật tới hướng di chuyển.
            step_index (int): Chỉ số bước hiện tại trong lượt.
        """
        current_positions = {character: character.pos for character in self.characters}
        occupied = set(current_positions.values())
        proposals = {}
        for character in self.characters:
            direction = directions.get(character)
            if direction is None or step_index >= character.steps_this_turn():
                continue
            dx, dy = direction
            target = (character.grid_x + dx, character.grid_y + dy)
            if not character.can_enter(target[0], target[1], self.grid, occupied - {character.pos}, self.chests):
                character.blocked_moves += 1
                continue
            proposals[character] = target

        counts = {}
        for target in proposals.values():
            counts[target] = counts.get(target, 0) + 1
        for character, target in proposals.items():
            if counts[target] > 1 or target in occupied:
                character.blocked_moves += 1
                continue
            character.move_to(target)

    def handle_character_interactions(self, character, opponents):
        """
        Xử lý khi nhân vật đứng trên các ô đặc biệt như chìa khóa, rương hoặc vật phẩm.
        
        Args:
            character (Character): Nhân vật đang xử lý.
            opponents (list): Danh sách các nhân vật đối thủ.
        """
        picked_key_id = self.find_key_at_pos(character.pos)
        if picked_key_id is not None:
            info = self.keys[picked_key_id]
            new_color_id = info["color_id"]
            new_score = info["score"]
            new_size = info["size"]
            new_color_name = KEY_COLOR_LOOKUP[new_color_id]["name"]

            if character.held_key_id is None:
                character.held_key_id = new_color_id
                character.held_key_score = new_score
                character.held_key_size = new_size
                character.keys_collected += 1
                self.status_message = f"{character.name} picked {new_size} {new_color_name} key (+{new_score} if opened)."
                del self.keys[picked_key_id]
            else:
                old_color_id = character.held_key_id
                old_score = character.held_key_score
                old_size = character.held_key_size
                old_color_name = KEY_COLOR_LOOKUP[old_color_id]["name"]

                character.held_key_id = new_color_id
                character.held_key_score = new_score
                character.held_key_size = new_size

                # Thả chìa cũ xuống đúng ô đang đứng để có thể quay lại đổi tiếp.
                self.keys[picked_key_id] = {
                    "pos": character.pos,
                    "color_id": old_color_id,
                    "score": old_score,
                    "size": old_size,
                }
                self.status_message = (
                    f"{character.name} swapped {old_size} {old_color_name} key "
                    f"for {new_size} {new_color_name} key."
                )

        if character.held_key_id is not None:
            chest_id = self.find_chest_at_pos(character.pos)
            if chest_id is not None and self.chests[chest_id]["color_id"] == character.held_key_id:
                character.score += character.held_key_score
                character.chests_opened += 1
                color_name = KEY_COLOR_LOOKUP[character.held_key_id]["name"]
                self.status_message = f"{character.name} opened a {color_name} chest for {character.held_key_score} points."
                del self.chests[chest_id]
                character.held_key_id = None
                character.held_key_score = 0
                character.held_key_size = "medium"

        item = self.find_item_at_pos(character.pos)
        if item is not None:
            character.apply_item(item.type_name, opponents)
            character.items_used += 1
            self.items.remove(item)
            self.status_message = f"{character.name} used {item.type_name}."

    def find_key_at_pos(self, pos):
        """Tìm và trả về ID của chìa khóa tại vị trí cụ thể (nếu có)."""
        for key_id, info in self.keys.items():
            if info["pos"] == pos:
                return key_id
        return None

    def find_chest_at_pos(self, pos):
        """Tìm và trả về ID của rương tại vị trí cụ thể (nếu có)."""
        for chest_id, info in self.chests.items():
            if info["pos"] == pos:
                return chest_id
        return None

    def find_item_at_pos(self, pos):
        """Tìm và trả về đối tượng Item tại vị trí cụ thể (nếu có)."""
        for item in self.items:
            if item.pos == pos:
                return item
        return None

    def spawn_items_if_needed(self):
        """Tự động sinh vật phẩm mới lên bản đồ sau một số lượt nhất định, nếu chưa đạt giới hạn."""
        if self.turn_count == 0 or self.turn_count % ITEM_SPAWN_INTERVAL_TURNS != 0:
            return
        if len(self.items) >= MAX_ITEMS_ON_BOARD:
            return

        new_items = self.item_spawner.spawn_item_pair(
            blocked_positions={c.pos for c in self.characters},
            existing_item_positions={it.pos for it in self.items},
            cols=self.cols
        )
        self.items.extend(new_items)

    def open_cells(self):
        """Trả về danh sách tất cả các tọa độ ô trống (đi bộ được) trên bản đồ."""
        return [(x, y) for y, row in enumerate(self.grid) for x, cell in enumerate(row) if cell == EMPTY]

    def distance_between(self, start, goal):
        """Tính khoảng cách đường đi ngắn nhất giữa hai điểm bằng BFS."""
        if goal is None:
            return 10**6
        path = bfs_shortest_path(self.grid, start, goal, blocked_positions=set())
        return len(path) - 1 if path else 10**6

    def distance_to_nearest_relevant_object(self, character):
        """Tính khoảng cách từ nhân vật tới mục tiêu gần nhất (chìa khóa hoặc rương tương ứng)."""
        targets = []
        if character.held_key_id is None:
            targets = [info["pos"] for info in self.keys.values()]
        else:
            targets = [info["pos"] for info in self.chests.values() if info["color_id"] == character.held_key_id]
        if not targets:
            return 10**6
        return min(self.distance_between(character.pos, target) for target in targets)

    def tiebreak_tuple(self, character):
        """Trả về tuple dùng để so sánh hạng khi có điểm bằng nhau (theo thứ tự ưu tiên các chỉ số)."""
        return (
            character.score,
            character.chests_opened,
            character.keys_collected,
            character.held_key_score,
            character.items_used,
            -self.distance_to_nearest_relevant_object(character),
            -character.blocked_moves,
            -self.characters.index(character),
        )

    def end_game(self):
        """Kết thúc trò chơi, tính toán người thắng dựa trên điểm số và tie-break."""
        self.game_over = True
        if not self.characters:
            self.winner_text = "No players"
            return
        best = max(self.characters, key=self.tiebreak_tuple)
        best_score = max(c.score for c in self.characters)
        tied = sum(1 for c in self.characters if c.score == best_score) > 1
        if tied:
            self.winner_text = f"Result: {best.name} wins by tie-break!"
        else:
            self.winner_text = f"Result: {best.name} wins!"

    def draw_board_vfx(self):
        """Vẽ hiệu ứng hào quang mờ ảo xung quanh khung bàn cờ."""
        board = self.get_board_rect()
        t = pygame.time.get_ticks() / 1000.0

        outer = board.inflate(34, 34)
        glow = pygame.Surface((outer.w, outer.h), pygame.SRCALPHA)
        colors = [(96, 203, 255), (197, 116, 255), (255, 155, 116)]
        for idx, col in enumerate(colors):
            alpha = int(18 + 8 * (0.5 + 0.5 * math.sin(t * 1.2 + idx)))
            pygame.draw.rect(glow, (*col, alpha), glow.get_rect(), width=4 + idx * 2, border_radius=26)

        cut = pygame.Rect(17, 17, board.w, board.h)
        pygame.draw.rect(glow, (0, 0, 0, 0), cut)
        self.canvas.blit(glow, outer.topleft, special_flags=pygame.BLEND_PREMULTIPLIED)

        corners = [
            (outer.x + 12, outer.y + 12),
            (outer.right - 12, outer.y + 12),
            (outer.x + 12, outer.bottom - 12),
            (outer.right - 12, outer.bottom - 12),
        ]
        for idx, (cx, cy) in enumerate(corners):
            pulse = 0.5 + 0.5 * math.sin(t * 1.7 + idx * 0.9)
            color = colors[idx % len(colors)]
            alpha = int(40 + 40 * pulse)
            pygame.draw.circle(self.canvas, (*color, alpha), (cx, cy), 3)
            pygame.draw.line(self.canvas, (*color, alpha), (cx - 5, cy), (cx + 5, cy), 1)
            pygame.draw.line(self.canvas, (*color, alpha), (cx, cy - 5), (cx, cy + 5), 1)

    def draw(self):
        """Phương thức vẽ chính, điều phối việc vẽ menu, hướng dẫn hoặc màn hình chơi game."""
        if self.state == "menu":
            self.draw_menu_screen()
            self.present()
            return
            
        if self.state == "instructions":
            self.canvas.fill((0, 0, 0, 0))
            self.menu_buttons = draw_instructions(self.canvas, self.fonts)
            self.present()
            return

        self.canvas.fill((0, 0, 0, 0)) # Clear with transparency
        # Note: background is now drawn directly to screen in present()
        self.draw_grid()
        self.draw_board_vfx()
        self.draw_keys()
        self.draw_chests()
        self.draw_items()
        for character in self.characters:
            character.draw(self.canvas, self.fonts["tiny"], self.assets, tile_size=self.tile_size, origin=(self.board_origin_x, self.board_origin_y))
        self.game_buttons = draw_side_panel(self.canvas, self.fonts, self)
        if self.game_over:
            self.draw_center_message(self.winner_text)
        self.present()

    def present(self):
        """Hiển thị canvas ảo lên màn hình thực tế, áp dụng tỷ lệ co giãn phù hợp."""
        # Draw background to full screen once per frame
        draw_background(self.screen, pygame.time.get_ticks())
        
        # Blit the virtual game canvas (which contains the map/UI) on top
        scaled = pygame.transform.smoothscale(self.canvas, (self.viewport.w, self.viewport.h))
        self.screen.blit(scaled, self.viewport.topleft)
        pygame.display.flip()

    def draw_menu_screen(self):
        """Vẽ màn hình menu chính và lấy danh sách các nút bấm."""
        self.canvas.fill((0, 0, 0, 0))
        self.menu_buttons = draw_menu(
            self.canvas,
            self.fonts,
            map_options=MAP_SIZE_OPTIONS,
            selected_map_index=self.selected_map_size_index,
            step_options=STEP_OPTIONS,
            selected_step_index=self.selected_step_index,
            player_type_options=PLAYER_TYPE_OPTIONS,
            selected_player_type_indices=self.selected_player_type_indices,
            selected_num_colors=self.selected_num_colors,
            selected_num_sizes=self.selected_num_sizes,
        )

    def draw_grid(self):
        """Vẽ lưới bản đồ, bao gồm khung bao quanh, bóng đổ và các ô tường/sàn."""
        frame = self.get_board_rect().inflate(24, 24)
        shadow = frame.move(6, 8)
        draw_round_rect(self.canvas, shadow, BOARD_SHADOW, None, radius=20)
        draw_round_rect(self.canvas, frame, BOARD_FRAME, (112, 94, 124), radius=20, width=2)
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                px = self.board_origin_x + x * self.tile_size
                py = self.board_origin_y + y * self.tile_size
                if cell == "#":
                    self.canvas.blit(self.assets.wall_tile, (px, py))
                else:
                    self.canvas.blit(self.assets.floor_tile, (px, py))
                    self.canvas.blit(self.assets.shadow_tile, (px, py))

    def draw_keys(self):
        """Vẽ tất cả các chìa khóa đang có trên bản đồ kèm hiệu ứng phát sáng."""
        for info in self.keys.values():
            px = self.board_origin_x + info["pos"][0] * self.tile_size
            py = self.board_origin_y + info["pos"][1] * self.tile_size
            color = KEY_COLOR_LOOKUP[info["color_id"]]["rgb"]
            glow = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
            center = (self.tile_size // 2, self.tile_size // 2)
            pygame.draw.circle(glow, (*color, 40), center, max(5, self.tile_size // 3))
            pygame.draw.circle(glow, (255, 255, 255, 28), center, max(3, self.tile_size // 5))
            self.canvas.blit(glow, (px, py), special_flags=pygame.BLEND_PREMULTIPLIED)
            self.canvas.blit(self.assets.get_key_surface(info["color_id"], info["size"]), (px, py))

    def draw_chests(self):
        """Vẽ tất cả các rương đang có trên bản đồ."""
        for info in self.chests.values():
            px = self.board_origin_x + info["pos"][0] * self.tile_size
            py = self.board_origin_y + info["pos"][1] * self.tile_size
            self.canvas.blit(self.assets.get_chest_surface(info["color_id"]), (px, py))

    def draw_items(self):
        """Vẽ tất cả các vật phẩm (items) đang có trên bản đồ."""
        for item in self.items:
            px = self.board_origin_x + item.pos[0] * self.tile_size
            py = self.board_origin_y + item.pos[1] * self.tile_size
            self.canvas.blit(self.assets.get_item_surface(item.type_name), (px, py))

    def draw_center_message(self, message):
        """Vẽ một hộp thông báo ở giữa bàn cờ (thường dùng khi kết thúc game)."""
        board_rect = self.get_board_rect()
        overlay = pygame.Rect(board_rect.centerx - 230, board_rect.centery - 72, 460, 144)
        draw_round_rect(self.canvas, overlay, (24, 28, 36, 235), (110, 96, 128), radius=18, width=2)
        text = self.fonts["title"].render(message, True, (233, 229, 220))
        self.canvas.blit(text, text.get_rect(center=(overlay.centerx, overlay.y + 40)))
        tip = self.fonts["small"].render("Use the top-right icons for main menu, new map, or reset.", True, (179, 171, 189))
        self.canvas.blit(tip, tip.get_rect(center=(overlay.centerx, overlay.y + 84)))
        tb = self.fonts["tiny"].render("Tie-break: score, chests, keys, held key value, items, distance.", True, (137, 130, 148))
        self.canvas.blit(tb, tb.get_rect(center=(overlay.centerx, overlay.y + 112)))

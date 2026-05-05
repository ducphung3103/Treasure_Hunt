"""Quản lý người chơi và bot Python.

Nơi thêm thuật toán tìm đường của bạn:
- Sửa các hàm Bot._choose_easy_direction, Bot._choose_medium_direction,
  Bot._choose_hard_direction.
- Mỗi hàm trả về một trong 5 giá trị: (0,-1), (0,1), (-1,0), (1,0), hoặc None.
"""

from __future__ import annotations

import random

import pygame

from .config import FREEZE_DURATION_TURNS, KEY_COLOR_LOOKUP, WALL
from .pathfinding import DIRECTIONS, bfs_shortest_path


class Character:
    """Lớp cơ sở đại diện cho các thực thể di chuyển trong trò chơi (Người chơi và Bot)."""

    def __init__(self, name, grid_pos, color, sprite=None):
        """
        Khởi tạo nhân vật.

        Args:
            name (str): Tên nhân vật.
            grid_pos (tuple): Vị trí ban đầu (x, y) trên lưới.
            color (tuple): Màu sắc đại diện (RGB).
            sprite (pygame.Surface, optional): Hình ảnh hiển thị của nhân vật.
        """
        self.name = name
        self.grid_x, self.grid_y = grid_pos
        self.color = color
        self.sprite = sprite
        self.score = 0
        self.held_key_id = None          # Lưu color_id của chìa khóa đang giữ.
        self.held_key_score = 0
        self.held_key_size = "medium"
        self.freeze_turns = 0
        self.keys_collected = 0
        self.chests_opened = 0
        self.items_used = 0
        self.blocked_moves = 0

    @property
    def pos(self):
        """Trả về vị trí hiện tại của nhân vật dưới dạng tuple (x, y)."""
        return self.grid_x, self.grid_y

    def is_frozen(self):
        """Kiểm tra xem nhân vật có đang bị đóng băng (không thể di chuyển) hay không."""
        return self.freeze_turns > 0

    def steps_this_turn(self):
        """Trả về số bước nhân vật có thể thực hiện trong lượt này (0 nếu bị đóng băng, 1 nếu bình thường)."""
        return 0 if self.is_frozen() else 1

    def can_enter(self, x, y, grid, blocked_positions, chests=None):
        """
        Kiểm tra xem nhân vật có thể đi vào ô (x, y) hay không.
        Điều kiện: Nằm trong bản đồ, không phải tường, không bị nhân vật khác chiếm chỗ, 
        và nếu là rương thì phải có chìa khóa đúng màu.

        Args:
            x (int): Tọa độ x mục tiêu.
            y (int): Tọa độ y mục tiêu.
            grid (list): Lưới bản đồ.
            blocked_positions (set): Tập hợp các vị trí đang bị chiếm giữ.
            chests (dict, optional): Thông tin các rương trên bản đồ.

        Returns:
            bool: True nếu có thể đi vào, False nếu không.
        """
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        if grid[y][x] == WALL:
            return False
        if (x, y) in blocked_positions:
            return False
        if chests is not None:
            for info in chests.values():
                if info["pos"] == (x, y):
                    return self.held_key_id == info["color_id"]
        return True

    def move_to(self, pos):
        """Cập nhật tọa độ của nhân vật sang vị trí mới."""
        self.grid_x, self.grid_y = pos

    def apply_item(self, item_type, opponents):
        """
        Áp dụng hiệu ứng của vật phẩm lên đối thủ. Hiện tại hỗ trợ hiệu ứng 'freeze'.

        Args:
            item_type (str): Loại vật phẩm.
            opponents (list): Danh sách các đối thủ.
        """
        if item_type == "freeze":
            for opponent in opponents:
                opponent.freeze_turns = max(opponent.freeze_turns, FREEZE_DURATION_TURNS + 1)

    def finish_turn(self):
        """Thực hiện các cập nhật cuối lượt, ví dụ: giảm số lượt đóng băng còn lại."""
        if self.freeze_turns > 0:
            self.freeze_turns -= 1

    def held_key_label(self):
        """Trả về chuỗi mô tả chìa khóa đang giữ (Màu sắc, kích thước, điểm số)."""
        if self.held_key_id is None:
            return "None"
        color_name = KEY_COLOR_LOOKUP.get(self.held_key_id, {"name": "Unknown"})["name"]
        return f"{color_name} {self.held_key_size} +{self.held_key_score}"

    def draw(self, surface, font, assets=None, tile_size=40, origin=(40, 60)):
        """
        Vẽ nhân vật lên màn hình ảo.

        Args:
            surface (pygame.Surface): Canvas để vẽ.
            font (pygame.font.Font): Font dùng để vẽ nhãn (nếu không có sprite).
            assets (GameAssets, optional): Quản lý tài nguyên hình ảnh.
            tile_size (int): Kích thước một ô lưới.
            origin (tuple): Tọa độ gốc của bàn cờ trên canvas.
        """
        origin_x, origin_y = origin
        px = origin_x + self.grid_x * tile_size
        py = origin_y + self.grid_y * tile_size
        if self.sprite is not None:
            surface.blit(self.sprite, (px, py))
        else:
            cx = px + tile_size // 2
            cy = py + tile_size // 2
            radius = tile_size // 2 - 6
            pygame.draw.circle(surface, self.color, (cx, cy), radius)
            pygame.draw.circle(surface, (20, 20, 20), (cx, cy), radius, 2)

        if self.held_key_id is not None and assets is not None:
            key_surface = assets.get_key_surface(self.held_key_id, self.held_key_size)
            small = pygame.transform.smoothscale(key_surface, (max(12, tile_size // 2), max(12, tile_size // 2)))
            surface.blit(small, (px + tile_size - small.get_width(), py - max(5, tile_size // 8)))
        elif self.held_key_id is not None:
            label = font.render(str(self.held_key_id), True, (20, 20, 20))
            surface.blit(label, (px + tile_size - 16, py - 6))


class Player(Character):
    """Lớp đại diện cho người chơi con người, điều khiển thông qua bàn phím."""

    CONTROL_SCHEMES = [
        {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d},
        {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT},
    ]

    def __init__(self, name, grid_pos, color, sprite=None, control_index=0):
        """
        Khởi tạo người chơi với sơ đồ phím điều khiển cụ thể.

        Args:
            control_index (int): Chỉ số sơ đồ phím (0: WASD, 1: Phím mũi tên).
        """
        super().__init__(name, grid_pos, color, sprite)
        self.control_index = control_index
        self.controls = self.CONTROL_SCHEMES[control_index % len(self.CONTROL_SCHEMES)]
        self.ai_label = "Human"

    def direction_from_key(self, key):
        """
        Chuyển đổi phím nhấn thành hướng di chuyển tương ứng.

        Args:
            key (int): Mã phím pygame.

        Returns:
            tuple hoặc None: Hướng di chuyển (dx, dy) hoặc None.
        """
        if key == self.controls["up"]:
            return (0, -1)
        if key == self.controls["down"]:
            return (0, 1)
        if key == self.controls["left"]:
            return (-1, 0)
        if key == self.controls["right"]:
            return (1, 0)
        return None

    def control_label(self):
        """Trả về tên sơ đồ phím đang sử dụng ('WASD' hoặc 'Arrow Keys')."""
        return ["WASD", "Arrow Keys"][self.control_index % 2]


class Bot(Character):
    """Lớp đại diện cho người chơi máy (Bot) với các mức độ khó khác nhau (Easy, Medium, Hard)."""

    def __init__(self, name, grid_pos, color, sprite=None, *, difficulty="medium"):
        """Khởi tạo Bot với độ khó cụ thể."""
        super().__init__(name, grid_pos, color, sprite)
        self.difficulty = difficulty
        self.ai_label = difficulty.capitalize()
        self._rng = random.Random(hash((name, grid_pos, difficulty)) & 0xFFFFFFFF)

    def _path_passable(self, game, pos, blocked_positions):
        """Hàm nội bộ kiểm tra xem Bot có thể đi qua một vị trí hay không (dùng cho tìm đường)."""
        x, y = pos
        if y < 0 or y >= len(game.grid) or x < 0 or x >= len(game.grid[0]):
            return False
        if game.grid[y][x] == WALL:
            return False
        if pos in blocked_positions:
            return False
        for info in game.chests.values():
            if info["pos"] == pos:
                return self.held_key_id == info["color_id"]
        return True

    def _legal_directions(self, game):
        """Trả về danh sách tất cả các hướng di chuyển hợp lệ mà Bot có thể thực hiện ngay lúc này."""
        if self.is_frozen():
            return [None]
        occupied = {c.pos for c in game.characters if c is not self}
        legal = [None]
        for dx, dy in DIRECTIONS:
            target = (self.grid_x + dx, self.grid_y + dy)
            if self.can_enter(target[0], target[1], game.grid, occupied, game.chests):
                legal.append((dx, dy))
        return legal

    def _path_to(self, game, goal):
        """Tìm đường đi ngắn nhất từ vị trí hiện tại tới mục tiêu sử dụng thuật toán BFS."""
        blocked = {c.pos for c in game.characters if c is not self}
        passable_fn = lambda pos, blocked_positions: self._path_passable(game, pos, blocked_positions)
        return bfs_shortest_path(game.grid, self.pos, goal, blocked, passable_fn=passable_fn)

    def _direction_from_path(self, path):
        """Lấy hướng di chuyển của bước đầu tiên trong một danh sách các bước đường đi."""
        if not path or len(path) < 2:
            return None
        nxt = path[1]
        return nxt[0] - self.grid_x, nxt[1] - self.grid_y

    def _nearest_path(self, game):
        """Tìm đường đi tới mục tiêu gần nhất (ưu tiên chìa khóa nếu chưa có, rương nếu đã có chìa)."""
        candidates = []
        if self.held_key_id is None:
            for key_id, info in game.keys.items():
                path = self._path_to(game, info["pos"])
                if path:
                    candidates.append((len(path), path))
        else:
            for chest_id, info in game.chests.items():
                if info["color_id"] != self.held_key_id:
                    continue
                path = self._path_to(game, info["pos"])
                if path:
                    candidates.append((len(path) - self.held_key_score / 100, path))
        for item in game.items:
            path = self._path_to(game, item.pos)
            if path:
                candidates.append((len(path) + 3, path))
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _opponent_distance_to(self, game, target):
        """Tính khoảng cách ngắn nhất mà bất kỳ đối thủ nào có thể tới mục tiêu chỉ định."""
        distances = []
        for opponent in game.characters:
            if opponent is self:
                continue
            blocked = {c.pos for c in game.characters if c not in (self, opponent)}
            path = bfs_shortest_path(game.grid, opponent.pos, target, blocked)
            if path:
                distances.append(len(path) - 1)
        return min(distances) if distances else 10**6

    def _score_path(self, game, path, value, target):
        """Tính toán điểm số ưu tiên cho một đường đi dựa trên giá trị mục tiêu và khoảng cách."""
        if not path:
            return None
        distance = max(1, len(path) - 1)
        score = value / distance
        if self._opponent_distance_to(game, target) < distance:
            score *= 0.78
        return score

    def _best_scored_path(self, game, *, aggressive=False):
        """
        Tìm đường đi 'tốt nhất' dựa trên trọng số điểm số.
        Xem xét chìa khóa, rương, vật phẩm và vị trí đối thủ để đưa ra quyết định thông minh hơn.
        """
        candidates = []
        leader_score = max((c.score for c in game.characters), default=0)
        behind = self.score < leader_score

        if self.held_key_id is not None:
            for chest_id, info in game.chests.items():
                if info["color_id"] != self.held_key_id:
                    continue
                path = self._path_to(game, info["pos"])
                value = 500 + self.held_key_score * 5
                candidates.append((self._score_path(game, path, value, info["pos"]), path))
        else:
            for key_id, info in game.keys.items():
                path = self._path_to(game, info["pos"])
                future = info["score"] * 4
                same_color_chests = [c for c in game.chests.values() if c["color_id"] == info["color_id"]]
                if same_color_chests:
                    key_to_chest = []
                    for chest in same_color_chests:
                        p = bfs_shortest_path(game.grid, info["pos"], chest["pos"])
                        if p:
                            key_to_chest.append(len(p) - 1)
                    if key_to_chest:
                        future += max(0, 140 - min(key_to_chest) * 3)
                candidates.append((self._score_path(game, path, future, info["pos"]), path))

        for item in game.items:
            path = self._path_to(game, item.pos)
            value = 60 + (45 if behind else 0)
            candidates.append((self._score_path(game, path, value, item.pos), path))

        if aggressive and behind:
            # Hard bot có xu hướng đi về phía đối thủ đang giữ chìa để gây áp lực chặn đường.
            for opponent in game.characters:
                if opponent is self or opponent.held_key_id is None:
                    continue
                path = self._path_to(game, opponent.pos)
                candidates.append((self._score_path(game, path, 85, opponent.pos), path))

        candidates = [(score, path) for score, path in candidates if score is not None and path]
        if not candidates:
            return self._nearest_path(game)
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def _choose_easy_direction(self, game):
        """Chiến lược Easy: Ưu tiên đường ngắn nhất tới mục tiêu, có 35% xác suất đi ngẫu nhiên."""
        legal = self._legal_directions(game)
        if len(legal) > 1 and self._rng.random() < 0.35:
            return self._rng.choice(legal)
        return self._direction_from_path(self._nearest_path(game))

    def _choose_medium_direction(self, game):
        """Chiến lược Medium: Chọn đường đi có điểm số tối ưu nhất, không quá hung hăng."""
        return self._direction_from_path(self._best_scored_path(game, aggressive=False))

    def _choose_hard_direction(self, game):
        """Chiến lược Hard: Chọn đường đi tối ưu và có xu hướng gây áp lực lên đối thủ khi đang thua."""
        return self._direction_from_path(self._best_scored_path(game, aggressive=True))

    def choose_direction(self, game):
        """
        Quyết định hướng di chuyển tiếp theo cho Bot dựa trên độ khó.

        Returns:
            tuple hoặc None: Hướng di chuyển (dx, dy) hoặc None.
        """
        if self.is_frozen():
            return None
        if self.difficulty == "easy":
            return self._choose_easy_direction(game)
        if self.difficulty == "hard":
            return self._choose_hard_direction(game)
        return self._choose_medium_direction(game)

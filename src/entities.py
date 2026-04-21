"""Quản lý các thực thể trong trò chơi."""

from __future__ import annotations

import pygame

from .config import FREEZE_DURATION_TURNS, WALL
from .pathfinding import bfs_shortest_path


class Character:
    """
    Áp dụng OOP, tạo ra các lớp Character, Player và Bot để quản lý thông tin và hành vi của người chơi và bot trong trò chơi.
    Lớp Character là lớp cơ sở, chứa các thuộc tính và phương thức chung cho cả người chơi và bot, bao gồm vị trí trên lưới, 
    màu sắc, điểm số, trạng thái đóng băng và các phương thức để di chuyển, áp dụng vật phẩm và vẽ nhân vật trên màn hình.
    """

    def __init__(self, name, grid_pos, color, sprite=None):
        """
        Hàm khởi tạo của lớp Character nhận vào tên, vị trí trên lưới, màu sắc và sprite (nếu có) của nhân vật. 
        Nó cũng khởi tạo điểm số, trạng thái giữ chìa khóa và số lượt đóng băng ban đầu.
        """
        self.name = name
        self.grid_x, self.grid_y = grid_pos
        self.color = color
        self.sprite = sprite
        self.score = 0
        self.held_key_id = None
        self.freeze_turns = 0

    @property
    def pos(self):
        """
        Thuộc tính pos trả về vị trí hiện tại của nhân vật dưới dạng một tuple (grid_x, grid_y), 
        giúp dễ dàng truy cập và sử dụng vị trí của nhân vật trong các phần khác của trò chơi.
        """
        return self.grid_x, self.grid_y

    def is_frozen(self):
        """
        Phương thức is_frozen kiểm tra xem nhân vật có đang bị đóng băng hay không bằng cách kiểm tra giá trị của freeze_turns. 
        Nếu freeze_turns lớn hơn 0, nhân vật được coi là đang bị đóng băng và phương thức trả về True, ngược lại trả về False.
        """
        return self.freeze_turns > 0

    def steps_this_turn(self):
        """
        Phương thức steps_this_turn trả về số bước mà nhân vật có thể thực hiện trong lượt hiện tại. 
        Nếu nhân vật đang bị đóng băng, nó sẽ trả về 0, ngược lại trả về 1, cho phép nhân vật di chuyển một bước trong lượt đó.
        """
        if self.is_frozen():
            return 0
        return 1

    def can_enter(self, x, y, grid, blocked_positions, chests=None):
        """
        Phương thức can_enter kiểm tra xem nhân vật có thể di chuyển đến một vị trí cụ thể trên lưới hay không. 
        Nó kiểm tra xem vị trí đó có nằm ngoài ranh giới của lưới, có phải là tường, có bị chặn bởi các vị trí khác hay không, 
        và nếu có một chiếc rương ở đó, nhân vật có chìa khóa phù hợp để mở nó hay không.
        """
        if y < 0 or y >= len(grid) or x < 0 or x >= len(grid[0]):
            return False
        if grid[y][x] == WALL:
            return False
        if (x, y) in blocked_positions:
            return False
        if chests is not None:
            for chest_id, info in chests.items():
                if info["pos"] == (x, y):
                    return self.held_key_id == chest_id
        return True

    def move_to(self, pos):
        """
        Phương thức move_to được sử dụng để cập nhật vị trí của nhân vật trên lưới. Nó nhận vào một tuple pos 
        chứa tọa độ mới (grid_x, grid_y) và cập nhật các thuộc tính grid_x và grid_y của nhân vật tương ứng với tọa độ mới đó.
        """
        self.grid_x, self.grid_y = pos

    def apply_item(self, item_type, opponents):
        """
        Phương thức apply_item được sử dụng để áp dụng hiệu ứng của một vật phẩm lên nhân vật. 
        Trong trường hợp này, nếu loại vật phẩm là "freeze", nó sẽ cập nhật số lượt đóng băng của các đối thủ 
        bằng cách đặt freeze_turns của họ thành giá trị lớn hơn hoặc bằng FREEZE_DURATION_TURNS + 1.
        """
        if item_type == "freeze":
            for opponent in opponents:
                opponent.freeze_turns = max(opponent.freeze_turns, FREEZE_DURATION_TURNS + 1)

    def finish_turn(self):
        """
        Phương thức finish_turn được gọi khi một lượt kết thúc, nó sẽ giảm số lượt đóng băng của nhân vật đi 1 
        nếu nhân vật đang bị đóng băng, giúp quản lý trạng thái đóng băng của nhân vật qua các lượt chơi.
        """
        if self.freeze_turns > 0:
            self.freeze_turns -= 1

    def draw(self, surface, font, assets=None, tile_size=40, origin=(40, 60)):
        """
        Phương thức draw được sử dụng để vẽ nhân vật lên màn hình. Nó tính toán vị trí pixel dựa trên vị trí lưới 
        và kích thước ô vuông, sau đó vẽ sprite của nhân vật nếu có, hoặc vẽ một hình tròn với màu sắc của nhân vật. 
        Ngoài ra, nếu nhân vật đang giữ một chìa khóa, nó sẽ vẽ biểu tượng chìa khóa ở góc trên bên phải của nhân vật.
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
            key_surface = assets.get_key_surface(self.held_key_id)
            offset = max(10, tile_size // 2 - 2)
            surface.blit(key_surface, (px + tile_size - offset, py - max(8, tile_size // 5)))
        elif self.held_key_id is not None:
            label = font.render(str(self.held_key_id), True, (20, 20, 20))
            surface.blit(label, (px + tile_size - 16, py - 6))


class Player(Character):
    """
    Định nghĩa các bộ điều khiển cho người chơi, bao gồm các phím để di chuyển lên, xuống, trái và phải. 
    Mỗi bộ điều khiển được gán cho một chỉ số control_index, cho phép người chơi sử dụng các bộ điều khiển khác nhau.
    """
    CONTROL_SCHEMES = [
        {"up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT},
        {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d},
        {"up": pygame.K_i, "down": pygame.K_k, "left": pygame.K_j, "right": pygame.K_l},
        {"up": pygame.K_t, "down": pygame.K_g, "left": pygame.K_f, "right": pygame.K_h},
    ]

    def __init__(self, name, grid_pos, color, sprite=None, control_index=0):
        """
        Hàm khởi tạo của lớp Player nhận vào tên, vị trí trên lưới, màu sắc, sprite (nếu có) và control_index 
        để xác định bộ điều khiển mà người chơi sẽ sử dụng. Nó kế thừa từ lớp Character và thiết lập các thuộc tính.
        """
        super().__init__(name, grid_pos, color, sprite)
        self.control_index = control_index
        self.controls = self.CONTROL_SCHEMES[control_index % len(self.CONTROL_SCHEMES)]

    def direction_from_key(self, key):
        """
        Phương thức direction_from_key nhận vào một phím bấm và trả về hướng di chuyển tương ứng dưới dạng tuple (dx, dy). 
        Nó so sánh phím bấm với các phím điều khiển đã định nghĩa trong self.controls và trả về hướng di chuyển phù hợp.
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
        """
        Phương thức control_label trả về một nhãn mô tả bộ điều khiển mà người chơi đang sử dụng, 
        giúp người chơi dễ dàng nhận biết và nhớ các phím điều khiển của mình trong trò chơi.
        """
        labels = ["Arrow Keys", "WASD", "IJKL", "TFGH"]
        return labels[self.control_index % len(labels)]


class Bot(Character):
    """
    Lớp Bot kế thừa từ lớp Character và xác định hành vi tự động bằng các thuật toán để tìm đường, nhặt vật phẩm.
    """

    def _path_passable(self, game, pos, blocked_positions):
        """Kiểm tra đường đi dành cho bot có bị chặn bởi tường, người chơi khác hay rương (mà không có chìa khóa) hay không."""
        x, y = pos
        if y < 0 or y >= len(game.grid) or x < 0 or x >= len(game.grid[0]):
            return False
        if game.grid[y][x] == WALL:
            return False
        if pos in blocked_positions:
            return False
        for chest_id, info in game.chests.items():
            if info["pos"] == pos:
                return self.held_key_id == chest_id
        return True

    def choose_target(self, game):
        """
        Phương thức choose_target được sử dụng để xác định mục tiêu mà bot sẽ hướng đến trong lượt chơi hiện tại. 
        Nó kiểm tra các mục tiêu có thể có trên bản đồ, bao gồm chìa khóa, rương và vật phẩm, và sử dụng thuật toán BFS 
        để tìm đường đi ngắn nhất đến từng mục tiêu. Bot sẽ chọn mục tiêu có đường đi ngắn nhất.
        """
        blocked = {c.pos for c in game.characters if c is not self}
        passable_fn = lambda pos, blocked_positions: self._path_passable(game, pos, blocked_positions)

        if self.held_key_id is None and game.keys:
            best_target = None
            best_path = None
            for key_id, key_info in game.keys.items():
                path = bfs_shortest_path(game.grid, self.pos, key_info["pos"], blocked, passable_fn=passable_fn)
                if path and (best_path is None or len(path) < len(best_path)):
                    best_path = path
                    best_target = ("key", key_id, key_info["pos"])
            if best_target is not None:
                return best_target, best_path

        if self.held_key_id is not None and self.held_key_id in game.chests:
            chest = game.chests[self.held_key_id]
            path = bfs_shortest_path(game.grid, self.pos, chest["pos"], blocked, passable_fn=passable_fn)
            if path:
                return ("chest", self.held_key_id, chest["pos"]), path

        best_target = None
        best_path = None
        for item in game.items:
            path = bfs_shortest_path(game.grid, self.pos, item.pos, blocked, passable_fn=passable_fn)
            if path and (best_path is None or len(path) < len(best_path)):
                best_path = path
                best_target = ("item", item.type_name, item.pos)

        return best_target, best_path

    def choose_direction(self, game):
        """
        Phương thức choose_direction được sử dụng để xác định hướng di chuyển của bot trong lượt chơi hiện tại. 
        Nó gọi phương thức choose_target để xác định mục tiêu mà bot sẽ hướng đến, sau đó kiểm tra đường đi đến mục tiêu đó. 
        Nếu có đường đi hợp lệ và dài hơn 1 bước, nó sẽ trả về hướng di chuyển tiếp theo. Ngược lại trả về None.
        """
        if self.is_frozen():
            return None
        _target, path = self.choose_target(game)
        if not path or len(path) < 2:
            return None
        next_pos = path[1]
        return next_pos[0] - self.grid_x, next_pos[1] - self.grid_y
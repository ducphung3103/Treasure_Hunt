"""Quản lý việc sinh bản đồ và các dữ liệu liên quan đến bản đồ"""

from __future__ import annotations

import random
from collections import deque
from typing import Iterable

from .config import EMPTY, WALL

# Thông số và cấu hình liên quan đến các loại bản đồ
MAP_SIZE_OPTIONS = [
    {
        "label": "Small",
        "rows": 15,
        "cols": 15,
        "tile_size": 40,
        "shape_ids": [1, 2, 3],
        "item_spawn_count": 8,
        "description": "15 x 15 grid · 3 chest types",
    },
    {
        "label": "Medium",
        "rows": 19,
        "cols": 19,
        "tile_size": 31,
        "shape_ids": [1, 2, 3, 4],
        "item_spawn_count": 10,
        "description": "19 x 19 grid · + Triangle chest",
    },
    {
        "label": "Large",
        "rows": 23,
        "cols": 23,
        "tile_size": 25,
        "shape_ids": [1, 2, 3, 4, 5],
        "item_spawn_count": 12,
        "description": "23 x 23 grid · + Triangle and Circle chests",
    },
]

# Tên bản đồ
ADJECTIVES = [
    "Amber", "Silver", "Emerald", "Echo", "Moonlit", "Crimson", "Ivory", "Hidden", "Misty", "Storm"
]
NOUNS = [
    "Labyrinth", "Vault", "Bastion", "Passage", "Citadel", "Harbor", "Maze", "Circuit", "Garden", "Sanctum"
]


def get_map_size_option(index: int) -> dict:
    """
    Hàm get_map_size_option trả về một cấu hình bản đồ dựa trên chỉ số được cung cấp. Nó sử dụng toán tử modulo 
    để đảm bảo rằng chỉ số luôn nằm trong phạm vi của danh sách MAP_SIZE_OPTIONS, cho phép người chơi chọn từ 
    các kích thước bản đồ khác nhau một cách linh hoạt.
    """
    return MAP_SIZE_OPTIONS[index % len(MAP_SIZE_OPTIONS)]


def get_map_size_count() -> int:
    """
    Hàm get_map_size_count trả về số lượng cấu hình bản đồ có sẵn trong MAP_SIZE_OPTIONS, 
    giúp người chơi biết được có bao nhiêu kích thước bản đồ khác nhau mà họ có thể chọn khi bắt đầu trò chơi.
    """
    return len(MAP_SIZE_OPTIONS)


def _random_name(rng: random.Random) -> str:
    """
    Hàm trả về một danh sách các nhãn mô tả ngẫu nhiên (tên map) dựa trên bộ từ khóa có sẵn, 
    giúp người chơi dễ dàng nhận biết và tạo sự mới mẻ trong trò chơi.
    """
    return f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}"


def _carve_maze(rows: int, cols: int, rng: random.Random) -> list[list[str]]:
    """
    Hàm _carve_maze sử dụng thuật toán carve maze để tạo ra một bản đồ ngẫu nhiên với các ô trống và tường. 
    Nó bắt đầu với một lưới đầy tường và sau đó "đục" các đường đi bằng cách loại bỏ các bức tường giữa các ô trống. 
    Sau khi tạo ra một bản đồ cơ bản, nó cũng thêm một số đường đi ngẫu nhiên để tạo ra các vòng lặp trên bản đồ, 
    làm cho trò chơi trở nên thú vị hơn.
    """
    grid = [[WALL for _ in range(cols)] for _ in range(rows)]

    def neighbors(x: int, y: int) -> list[tuple[int, int, int, int]]:
        result = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 1 <= nx < cols - 1 and 1 <= ny < rows - 1:
                result.append((nx, ny, dx // 2, dy // 2))
        rng.shuffle(result)
        return result

    stack = [(1, 1)]
    grid[1][1] = EMPTY
    visited = {(1, 1)}

    while stack:
        x, y = stack[-1]
        moved = False
        for nx, ny, wx, wy in neighbors(x, y):
            if (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            grid[y + wy][x + wx] = EMPTY
            grid[ny][nx] = EMPTY
            stack.append((nx, ny))
            moved = True
            break
        if not moved:
            stack.pop()

    loop_attempts = max(10, (rows * cols) // 18)
    for _ in range(loop_attempts):
        x = rng.randrange(1, cols - 1)
        y = rng.randrange(1, rows - 1)
        if grid[y][x] != WALL:
            continue
        horizontal = grid[y][x - 1] == EMPTY and grid[y][x + 1] == EMPTY
        vertical = grid[y - 1][x] == EMPTY and grid[y + 1][x] == EMPTY
        if horizontal or vertical:
            grid[y][x] = EMPTY

    return grid


def _ensure_starts_open(grid: list[list[str]], starts: Iterable[tuple[int, int]]) -> None:
    """
    Hàm _ensure_starts_open đảm bảo rằng các vị trí bắt đầu của người chơi và các ô xung quanh chúng 
    được mở trên bản đồ, giúp người chơi có một khởi đầu thuận lợi khi bắt đầu trò chơi.
    """
    width = len(grid[0])
    height = len(grid)
    for x, y in starts:
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1:
                grid[ny][nx] = EMPTY


def _open_cells(grid: list[list[str]]) -> list[tuple[int, int]]:
    """
    Hàm _open_cells trả về một danh sách các vị trí trên bản đồ mà có ô trống (EMPTY), 
    giúp xác định các vị trí có thể đặt chìa khóa, rương và vật phẩm một cách hợp lệ trên bản đồ.
    """
    return [
        (x, y)
        for y, row in enumerate(grid)
        for x, cell in enumerate(row)
        if cell == EMPTY
    ]


def _open_neighbors(grid: list[list[str]], pos: tuple[int, int]) -> list[tuple[int, int]]:
    """
    Hàm _open_neighbors trả về một danh sách các vị trí lân cận của một ô trống (EMPTY) trên bản đồ, 
    giúp xác định các vị trí có thể di chuyển đến từ một ô trống cụ thể, điều này rất quan trọng 
    trong việc xác định đường đi và khoảng cách giữa các vị trí trên bản đồ.
    """
    x, y = pos
    result = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == EMPTY:
            result.append((nx, ny))
    return result


def _remaining_open_connected(grid: list[list[str]], blocked: set[tuple[int, int]]) -> bool:
    """
    Hàm _remaining_open_connected kiểm tra xem các ô trống còn lại trên bản đồ có kết nối với nhau hay không 
    sau khi chặn một số vị trí nhất định. Điều này giúp đảm bảo rằng việc đặt rương và chìa khóa không tạo ra 
    các khu vực bị cô lập trên bản đồ, làm cho trò chơi trở nên công bằng và thú vị hơn.
    """
    open_cells = [
        (x, y)
        for y, row in enumerate(grid)
        for x, cell in enumerate(row)
        if cell == EMPTY and (x, y) not in blocked
    ]
    if not open_cells:
        return False

    start = open_cells[0]
    queue = deque([start])
    visited = {start}

    while queue:
        cell = queue.popleft()
        for nxt in _open_neighbors(grid, cell):
            if nxt in blocked or nxt in visited:
                continue
            visited.add(nxt)
            queue.append(nxt)

    return len(visited) == len(open_cells)


def _pick_safe_chest_positions(
    grid: list[list[str]],
    rng: random.Random,
    cells: list[tuple[int, int]],
    key_positions: list[tuple[int, int]],
    banned: set[tuple[int, int]],
    anchor_positions: list[tuple[int, int]],
) -> list[tuple[int, int]]:
    """
    Hàm được sử dụng để đặt chest một cách an toàn trên bản đồ, đảm bảo rằng việc đặt chest không tạo ra 
    các khu vực bị cô lập và vẫn giữ cho trò chơi công bằng và thú vị. Nó đánh giá các vị trí ứng viên 
    dựa trên khoảng cách đến chìa khóa, khoảng cách đến các vị trí neo (như vị trí bắt đầu của người chơi), 
    và số lượng ô trống xung quanh để xác định vị trí tốt nhất để đặt chest.
    """
    candidates = [cell for cell in cells if cell not in banned]
    rng.shuffle(candidates)
    chosen: list[tuple[int, int]] = []

    for key_pos in key_positions:
        valid_candidates = []
        for candidate in candidates:
            if candidate in chosen:
                continue
            blocked = set(chosen) | {candidate}
            if not _remaining_open_connected(grid, blocked):
                continue

            degree = len(_open_neighbors(grid, candidate))
            distance_to_key = abs(candidate[0] - key_pos[0]) + abs(candidate[1] - key_pos[1])
            distance_to_anchor = min(
                abs(candidate[0] - ax) + abs(candidate[1] - ay)
                for ax, ay in anchor_positions
            )
            score = distance_to_key * 8 + distance_to_anchor * 2 - degree * 6
            valid_candidates.append((score, candidate))

        if valid_candidates:
            valid_candidates.sort(key=lambda item: item[0], reverse=True)
            best = valid_candidates[0][1]
            chosen.append(best)
            continue

        fallback_candidates = [cell for cell in candidates if cell not in chosen]
        if not fallback_candidates:
            break
        fallback = max(
            fallback_candidates,
            key=lambda pos: abs(pos[0] - key_pos[0]) + abs(pos[1] - key_pos[1]),
        )
        chosen.append(fallback)

    return chosen


def _pick_distinct_positions(rng: random.Random, cells: list[tuple[int, int]], count: int, banned: set[tuple[int, int]], min_distance: int = 4) -> list[tuple[int, int]]:
    """
    Hàm _pick_distinct_positions được sử dụng để chọn một số vị trí ngẫu nhiên trên bản đồ mà không quá gần nhau, 
    giúp đảm bảo rằng các yếu tố như chìa khóa, rương và vật phẩm được phân bố một cách hợp lý trên bản đồ, 
    tạo ra một trải nghiệm chơi game thú vị và công bằng cho người chơi.
    """
    pool = [cell for cell in cells if cell not in banned]
    rng.shuffle(pool)
    picked: list[tuple[int, int]] = []
    while pool and len(picked) < count:
        candidate = pool.pop()
        if any(abs(candidate[0] - other[0]) + abs(candidate[1] - other[1]) < min_distance for other in picked):
            continue
        picked.append(candidate)
    if len(picked) < count:
        for cell in [cell for cell in cells if cell not in banned and cell not in picked]:
            picked.append(cell)
            if len(picked) == count:
                break
    return picked


def generate_level(seed: int, size_index: int) -> dict:
    """
    Đây là hàm chính để tạo ra một bản đồ mới dựa trên một seed và một chỉ số kích thước. Nó sử dụng thuật toán carve maze 
    để tạo ra một bản đồ ngẫu nhiên, sau đó đảm bảo rằng các vị trí bắt đầu của người chơi được mở. Sau đó, nó chọn ngẫu nhiên 
    các vị trí cho chìa khóa và rương, đảm bảo rằng chúng không bị chặn và có khoảng cách hợp lý với nhau. Cuối cùng, 
    nó chọn các điểm sinh vật phẩm trên bản đồ và trả về một cấu trúc dữ liệu chứa tất cả thông tin về bản đồ đã tạo.
    """
    profile = get_map_size_option(size_index)
    rows = profile["rows"]
    cols = profile["cols"]
    shape_ids = profile["shape_ids"]
    rng = random.Random(seed)

    grid = _carve_maze(rows, cols, rng)
    start_positions = [(1, 1), (cols - 2, 1), (1, rows - 2), (cols - 2, rows - 2)]
    _ensure_starts_open(grid, start_positions)

    cells = _open_cells(grid)
    reserved = set(start_positions)

    key_positions = _pick_distinct_positions(rng, cells, len(shape_ids), reserved)
    reserved.update(key_positions)

    chest_positions = _pick_safe_chest_positions(
        grid,
        rng,
        cells,
        key_positions,
        reserved,
        start_positions,
    )
    reserved.update(chest_positions)

    item_spawn_points = _pick_distinct_positions(
        rng,
        cells,
        profile["item_spawn_count"],
        reserved,
        min_distance=3,
    )

    return {
        "name": _random_name(rng),
        "seed": seed,
        "size_label": profile["label"],
        "size_description": profile["description"],
        "rows": rows,
        "cols": cols,
        "tile_size": profile["tile_size"],
        "grid": grid,
        "keys": {shape_id: {"pos": pos} for shape_id, pos in zip(shape_ids, key_positions)},
        "chests": {shape_id: {"pos": pos, "score": 50} for shape_id, pos in zip(shape_ids, chest_positions)},
        "start_positions": start_positions,
        "item_spawn_points": item_spawn_points,
    }


def get_level(seed: int, size_index: int) -> dict:
    """Trả về dữ liệu bản đồ đã được khởi tạo bởi generate_level."""
    return generate_level(seed, size_index)
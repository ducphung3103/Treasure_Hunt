"""Sinh map đối xứng cho chế độ 2 player.

Grid chỉ chứa:
    # = tường
    . = ô đi được
Key/rương/item/player được lưu riêng trong dict/list của level hoặc Game.
"""

from __future__ import annotations

import random
from collections import deque

from .config import EMPTY, KEY_COLORS, KEY_SCORE_BY_SIZE, WALL

MAP_SIZE_OPTIONS = [
    {
        "label": "20 x 20",
        "rows": 20,
        "cols": 20,
        "tile_size": 32,
        "item_spawn_count": 8,
        "description": "20 x 20 symmetric arena · 2 keys/chests per color",
    },
    {
        "label": "30 x 30",
        "rows": 30,
        "cols": 30,
        "tile_size": 21,
        "item_spawn_count": 12,
        "description": "30 x 30 symmetric arena · longer routes",
    },
    {
        "label": "40 x 40",
        "rows": 40,
        "cols": 40,
        "tile_size": 16,
        "item_spawn_count": 16,
        "description": "40 x 40 symmetric arena · hardest navigation",
    },
]

ADJECTIVES = ["Amber", "Silver", "Emerald", "Echo", "Moonlit", "Crimson", "Ivory", "Hidden", "Misty", "Storm"]
NOUNS = ["Labyrinth", "Vault", "Bastion", "Passage", "Citadel", "Harbor", "Maze", "Circuit", "Garden", "Sanctum"]


def get_map_size_option(index: int) -> dict:
    """Trả về tùy chọn kích thước bản đồ dựa trên chỉ mục."""
    return MAP_SIZE_OPTIONS[index % len(MAP_SIZE_OPTIONS)]


def get_map_size_count() -> int:
    """Trả về số lượng tùy chọn kích thước bản đồ hiện có."""
    return len(MAP_SIZE_OPTIONS)


def _random_name(rng: random.Random) -> str:
    """Tạo tên ngẫu nhiên cho màn chơi (ví dụ: 'Moonlit Citadel')."""
    return f"{rng.choice(ADJECTIVES)} {rng.choice(NOUNS)}"


def _mirror_x(cols: int, pos: tuple[int, int]) -> tuple[int, int]:
    """Tính tọa độ đối xứng qua trục dọc giữa màn hình."""
    return cols - 1 - pos[0], pos[1]


def _center_columns(cols: int) -> tuple[int, int]:
    """Trả về chỉ mục của hai cột ở giữa bản đồ."""
    return cols // 2 - 1, cols // 2


def _open_cells(grid: list[list[str]]) -> list[tuple[int, int]]:
    """Trả về danh sách tất cả các ô không phải là tường."""
    return [(x, y) for y, row in enumerate(grid) for x, cell in enumerate(row) if cell == EMPTY]


def _neighbors(grid: list[list[str]], pos: tuple[int, int]):
    """Generator trả về các ô lân cận (4 hướng) có thể đi vào được."""
    x, y = pos
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]) and grid[ny][nx] == EMPTY:
            yield nx, ny


def _component(grid: list[list[str]], start: tuple[int, int], blocked: set[tuple[int, int]] | None = None) -> set[tuple[int, int]]:
    """Tìm tất cả các ô thuộc cùng một vùng liên thông bắt đầu từ một điểm."""
    blocked = blocked or set()
    if start in blocked or grid[start[1]][start[0]] == WALL:
        return set()
    q = deque([start])
    seen = {start}
    while q:
        cell = q.popleft()
        for nxt in _neighbors(grid, cell):
            if nxt in seen or nxt in blocked:
                continue
            seen.add(nxt)
            q.append(nxt)
    return seen


def _is_connected(grid: list[list[str]], blocked: set[tuple[int, int]] | None = None) -> bool:
    """Kiểm tra xem toàn bộ các ô trống trên bản đồ có liên thông với nhau không."""
    blocked = blocked or set()
    cells = [cell for cell in _open_cells(grid) if cell not in blocked]
    if not cells:
        return False
    return len(_component(grid, cells[0], blocked)) == len(cells)


def _open_rect(grid: list[list[str]], center: tuple[int, int], radius: int = 1) -> None:
    """Mở một vùng trống hình chữ nhật xung quanh một điểm tâm."""
    rows, cols = len(grid), len(grid[0])
    cx, cy = center
    for y in range(max(1, cy - radius), min(rows - 1, cy + radius + 1)):
        for x in range(max(1, cx - radius), min(cols - 1, cx + radius + 1)):
            grid[y][x] = EMPTY
            grid[y][cols - 1 - x] = EMPTY


def _make_symmetric_grid(rows: int, cols: int, rng: random.Random) -> list[list[str]]:
    """Tạo lưới bản đồ đối xứng trái-phải với các hành lang chiến thuật."""
    grid = [[EMPTY for _ in range(cols)] for _ in range(rows)]
    for x in range(cols):
        grid[0][x] = WALL
        grid[rows - 1][x] = WALL
    for y in range(rows):
        grid[y][0] = WALL
        grid[y][cols - 1] = WALL

    density = {20: 0.15, 30: 0.18, 40: 0.20}.get(rows, 0.18)
    c1, c2 = _center_columns(cols)
    start_positions = [(1, 1), (cols - 2, 1)]

    for y in range(1, rows - 1):
        for x in range(1, cols // 2):
            mirror = cols - 1 - x
            near_start = (abs(x - 1) + abs(y - 1) <= 4) or (abs(mirror - (cols - 2)) + abs(y - 1) <= 4)
            center_lane = x in (c1, c2) or mirror in (c1, c2)
            horizontal_lane = y in {rows // 3, rows // 2, rows * 2 // 3}
            if near_start or center_lane or horizontal_lane:
                continue
            if rng.random() < density:
                grid[y][x] = WALL
                grid[y][mirror] = WALL

    # Mở các hành lang chiến thuật cố định để rương không dễ khóa toàn bộ map.
    for y in range(1, rows - 1):
        grid[y][c1] = EMPTY
        grid[y][c2] = EMPTY
    for y in (rows // 3, rows // 2, rows * 2 // 3):
        for x in range(1, cols - 1):
            grid[y][x] = EMPTY
    for start in start_positions:
        _open_rect(grid, start, radius=2)

    # Nếu random walls vẫn làm tách vùng, mở dần tường đối xứng cho đến khi connected.
    guard = 0
    while not _is_connected(grid) and guard < rows * cols:
        guard += 1
        cells = _open_cells(grid)
        main = _component(grid, cells[0])
        outside = [cell for cell in cells if cell not in main]
        if not outside:
            break
        target = rng.choice(outside)
        nearest = min(main, key=lambda p: abs(p[0] - target[0]) + abs(p[1] - target[1]))
        x, y = target
        while x != nearest[0]:
            grid[y][x] = EMPTY
            grid[y][cols - 1 - x] = EMPTY
            x += 1 if nearest[0] > x else -1
        while y != nearest[1]:
            grid[y][x] = EMPTY
            grid[y][cols - 1 - x] = EMPTY
            y += 1 if nearest[1] > y else -1
        grid[y][x] = EMPTY
        grid[y][cols - 1 - x] = EMPTY

    return grid


def _bfs_distance(grid: list[list[str]], start: tuple[int, int], goal: tuple[int, int], blocked: set[tuple[int, int]] | None = None) -> int | None:
    """Tính khoảng cách ngắn nhất giữa hai điểm sử dụng BFS đơn giản."""
    blocked = blocked or set()
    if start in blocked or goal in blocked:
        return None
    q = deque([(start, 0)])
    seen = {start}
    while q:
        cell, dist = q.popleft()
        if cell == goal:
            return dist
        for nxt in _neighbors(grid, cell):
            if nxt in seen or nxt in blocked:
                continue
            seen.add(nxt)
            q.append((nxt, dist + 1))
    return None


def _pair_candidates(grid: list[list[str]], banned: set[tuple[int, int]], start_left: tuple[int, int]) -> list[dict]:
    """Tìm tất cả các cặp ô đối xứng có thể đặt vật phẩm/chìa khóa/rương."""
    rows, cols = len(grid), len(grid[0])
    c1, c2 = _center_columns(cols)
    result = []
    for y in range(1, rows - 1):
        for x in range(1, cols // 2):
            if x in (c1, c2):
                continue
            pos = (x, y)
            mirror = _mirror_x(cols, pos)
            if pos in banned or mirror in banned:
                continue
            if grid[y][x] != EMPTY or grid[mirror[1]][mirror[0]] != EMPTY:
                continue
            dist = _bfs_distance(grid, start_left, pos)
            if dist is None:
                continue
            result.append({"pos": pos, "mirror": mirror, "dist": dist})
    return result


def _far_from_existing_score(pos: tuple[int, int], existing: set[tuple[int, int]]) -> int:
    """Tính điểm số dựa trên khoảng cách tới các vật thể đã tồn tại (để phân tán vật phẩm)."""
    if not existing:
        return 10**6
    return min(abs(pos[0] - other[0]) + abs(pos[1] - other[1]) for other in existing)


def _key_size_from_distance(rows: int, cols: int, distance: int) -> str:
    """Quyết định kích thước chìa khóa dựa trên khoảng cách từ điểm xuất phát."""
    near = (rows + cols) * 0.26
    far = (rows + cols) * 0.44
    if distance < near:
        return "small"
    if distance < far:
        return "medium"
    return "large"


def _choose_key_pair(rng: random.Random, candidates: list[dict], banned: set[tuple[int, int]], existing: set[tuple[int, int]], target_rank: float) -> dict:
    """Chọn một cặp vị trí đặt chìa khóa dựa trên thứ hạng khoảng cách mong muốn."""
    usable = [c for c in candidates if c["pos"] not in banned and c["mirror"] not in banned]
    usable.sort(key=lambda c: c["dist"])
    if not usable:
        raise RuntimeError("Không đủ vị trí để đặt chìa khóa")
    target_index = int(target_rank * (len(usable) - 1))
    scored = []
    for i, cand in enumerate(usable):
        rank_penalty = abs(i - target_index)
        spread = _far_from_existing_score(cand["pos"], existing)
        scored.append((-rank_penalty * 5 + spread + rng.random(), cand))
    scored.sort(reverse=True, key=lambda item: item[0])
    return scored[0][1]


def _choose_chest_pair(
    rng: random.Random,
    grid: list[list[str]],
    candidates: list[dict],
    banned: set[tuple[int, int]],
    blocked_chests: set[tuple[int, int]],
    key_left: tuple[int, int],
    existing: set[tuple[int, int]],
) -> dict:
    """Chọn một cặp vị trí đặt rương báu sao cho xa chìa khóa tương ứng và không gây tắc nghẽn bản đồ."""
    rows, cols = len(grid), len(grid[0])
    min_key_chest = max(9, int((rows + cols) * 0.27))
    # Tối ưu: lọc trước bằng Manhattan distance rồi mới chạy BFS/connectivity trên nhóm tốt nhất.
    rough = []
    for cand in candidates:
        pos = cand["pos"]
        mirror = cand["mirror"]
        if pos in banned or mirror in banned:
            continue
        manhattan = abs(pos[0] - key_left[0]) + abs(pos[1] - key_left[1])
        if manhattan < min_key_chest:
            continue
        spread = _far_from_existing_score(pos, existing)
        rough.append((manhattan * 4 + spread + rng.random(), cand))
    rough.sort(reverse=True, key=lambda item: item[0])

    scored = []
    for _, cand in rough[:90]:
        pos = cand["pos"]
        mirror = cand["mirror"]
        dist_key = _bfs_distance(grid, key_left, pos, blocked_chests)
        if dist_key is None or dist_key < min_key_chest:
            continue
        # Rương vẫn là vật cản nếu chưa có chìa, nên tránh đặt ở vị trí làm đứt map.
        if not _is_connected(grid, blocked_chests | {pos, mirror}):
            continue
        spread = _far_from_existing_score(pos, existing)
        scored.append((dist_key * 4 + spread + rng.random(), cand))
    if scored:
        scored.sort(reverse=True, key=lambda item: item[0])
        return scored[0][1]

    # Fallback nếu map quá chật: vẫn chọn xa nhất có thể nhưng không làm đứt map.
    fallback = []
    for _, cand in rough[:160]:
        pos, mirror = cand["pos"], cand["mirror"]
        dist_key = _bfs_distance(grid, key_left, pos, blocked_chests) or 0
        if _is_connected(grid, blocked_chests | {pos, mirror}):
            fallback.append((dist_key, cand))
    if not fallback:
        raise RuntimeError("Không đủ vị trí để đặt rương")
    fallback.sort(reverse=True, key=lambda item: item[0])
    return fallback[0][1]


def _pick_item_spawn_points(rng: random.Random, grid: list[list[str]], count: int, banned: set[tuple[int, int]]) -> list[tuple[int, int]]:
    """Chọn các điểm cố định trên bản đồ để sinh vật phẩm ngẫu nhiên trong suốt trận đấu."""
    rows, cols = len(grid), len(grid[0])
    center_x, center_y = cols / 2.0, rows / 2.0
    candidates = []
    
    # We want points far from the center, and they must be symmetric.
    # We'll pick points in the left half and mirror them.
    for y in range(1, rows - 1):
        for x in range(1, cols // 2):
            pos = (x, y)
            mirror = _mirror_x(cols, pos)
            if grid[y][x] == EMPTY and grid[mirror[1]][mirror[0]] == EMPTY:
                if pos not in banned and mirror not in banned:
                    # Calculate distance from center to prioritize far points
                    dist_from_center = abs(x - center_x) + abs(y - center_y)
                    candidates.append((dist_from_center, pos, mirror))
    
    # Sort by distance from center (descending) and add some randomness
    candidates.sort(key=lambda c: c[0] + rng.random() * 5, reverse=True)
    
    picked = []
    for _, pos, mirror in candidates:
        # Ensure we don't pick points too close to each other
        if any(abs(pos[0] - p[0]) + abs(pos[1] - p[1]) < 4 for p in picked):
            continue
        picked.append(pos)
        picked.append(mirror)
        if len(picked) >= count:
            break
    return picked


def generate_level(seed: int, size_index: int, num_colors: int = 4, num_sizes: int = 3) -> dict:
    """
    Hàm chính để tạo một màn chơi hoàn chỉnh dựa trên seed.
    Xây dựng lưới, đặt chìa khóa, rương và các điểm sinh vật phẩm một cách đối xứng.
    """
    profile = get_map_size_option(size_index)
    rows = profile["rows"]
    cols = profile["cols"]
    rng = random.Random(seed)
    grid = _make_symmetric_grid(rows, cols, rng)

    start_positions = [(1, 1), (cols - 2, 1)]
    for start in start_positions:
        _open_rect(grid, start, radius=2)

    banned = set(start_positions)
    key_objects = {}
    chest_objects = {}
    existing_objects: set[tuple[int, int]] = set(banned)
    blocked_chests: set[tuple[int, int]] = set()

    candidates = _pair_candidates(grid, banned, start_positions[0])
    color_ids = [info["id"] for info in KEY_COLORS[:num_colors]]

    for index, color_id in enumerate(color_ids):
        target_rank = (index + 0.5) / len(color_ids)
        key_pair = _choose_key_pair(rng, candidates, banned, existing_objects, target_rank)
        
        # Determine key size based on distance and num_sizes
        actual_size = _key_size_from_distance(rows, cols, key_pair["dist"])
        if num_sizes == 1:
            key_size = "medium"
        elif num_sizes == 2:
            # Map small/medium to small, large to large? Or just omit medium?
            # Let's say: small distance -> small, else large.
            key_size = "small" if actual_size in ("small", "medium") else "large"
        else:
            key_size = actual_size
            
        key_score = KEY_SCORE_BY_SIZE[key_size]

        left_key_id = color_id * 10 + 1
        right_key_id = color_id * 10 + 2
        key_objects[left_key_id] = {"pos": key_pair["pos"], "color_id": color_id, "size": key_size, "score": key_score}
        key_objects[right_key_id] = {"pos": key_pair["mirror"], "color_id": color_id, "size": key_size, "score": key_score}
        banned.update({key_pair["pos"], key_pair["mirror"]})
        existing_objects.update({key_pair["pos"], key_pair["mirror"]})

        chest_pair = _choose_chest_pair(rng, grid, candidates, banned, blocked_chests, key_pair["pos"], existing_objects)
        left_chest_id = color_id * 10 + 1
        right_chest_id = color_id * 10 + 2
        chest_objects[left_chest_id] = {"pos": chest_pair["pos"], "color_id": color_id}
        chest_objects[right_chest_id] = {"pos": chest_pair["mirror"], "color_id": color_id}
        banned.update({chest_pair["pos"], chest_pair["mirror"]})
        existing_objects.update({chest_pair["pos"], chest_pair["mirror"]})
        blocked_chests.update({chest_pair["pos"], chest_pair["mirror"]})

    item_spawn_points = _pick_item_spawn_points(rng, grid, profile["item_spawn_count"], banned)

    return {
        "name": _random_name(rng),
        "seed": seed,
        "size_label": profile["label"],
        "size_description": profile["description"],
        "rows": rows,
        "cols": cols,
        "tile_size": profile["tile_size"],
        "grid": grid,
        "keys": key_objects,
        "chests": chest_objects,
        "start_positions": start_positions,
        "item_spawn_points": item_spawn_points,
    }


def get_level(seed: int, size_index: int, num_colors: int = 4, num_sizes: int = 3) -> dict:
    """Wrapper để tạo level (có thể mở rộng thêm logic cache nếu cần)."""
    return generate_level(seed, size_index, num_colors=num_colors, num_sizes=num_sizes)

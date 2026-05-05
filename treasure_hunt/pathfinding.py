"""Code chứa các thuật toán tìm đường - Bộ não của các nhân vật trong trò chơi"""

from collections import deque
from .config import WALL

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def in_bounds(grid, pos):
    """
    Kiểm tra xem một vị trí (x, y) có nằm trong ranh giới của lưới hay không.

    Args:
        grid (list): Lưới bản đồ.
        pos (tuple): Vị trí cần kiểm tra (x, y).

    Returns:
        bool: True nếu nằm trong ranh giới, False nếu không.
    """
    x, y = pos
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])

def passable(grid, pos, blocked_positions=None):
    """
    Kiểm tra xem một ô có thể đi qua được hay không (không phải tường và không bị chặn).

    Args:
        grid (list): Lưới bản đồ.
        pos (tuple): Vị trí (x, y).
        blocked_positions (set, optional): Tập hợp các vị trí bị chiếm bởi nhân vật khác.

    Returns:
        bool: True nếu có thể đi qua, False nếu không.
    """
    if blocked_positions is None:
        blocked_positions = set()
    x, y = pos
    return grid[y][x] != WALL and pos not in blocked_positions

def bfs_shortest_path(grid, start, goal, blocked_positions=None, passable_fn=None):
    """
    Tìm đường đi ngắn nhất từ start đến goal sử dụng thuật toán tìm kiếm theo chiều rộng (BFS).

    Args:
        grid (list): Lưới bản đồ.
        start (tuple): Vị trí bắt đầu (x, y).
        goal (tuple): Vị trí mục tiêu (x, y).
        blocked_positions (set, optional): Các vị trí tạm thời bị chặn.
        passable_fn (callable, optional): Hàm tùy chỉnh để kiểm tra tính khả dụng của ô.

    Returns:
        list hoặc None: Danh sách các tọa độ tạo thành đường đi, hoặc None nếu không tìm thấy.
    """
    if start == goal:
        return [start]
    if blocked_positions is None:
        blocked_positions = set()
    blocked_positions = set(blocked_positions)
    blocked_positions.discard(goal)

    queue = deque([start])
    visited = {start}
    parent = {start: None}

    while queue:
        current = queue.popleft()
        for dx, dy in DIRECTIONS:
            nxt = (current[0] + dx, current[1] + dy)
            if not in_bounds(grid, nxt):
                continue
            if nxt in visited:
                continue
            is_passable = passable_fn(nxt, blocked_positions) if passable_fn is not None else passable(grid, nxt, blocked_positions)
            if not is_passable:
                continue
            visited.add(nxt)
            parent[nxt] = current
            if nxt == goal:
                return build_path(parent, goal)
            queue.append(nxt)
    return None

def build_path(parent, goal):
    """
    Xây dựng lại đường đi từ từ điển parent của BFS.

    Args:
        parent (dict): Ánh xạ từ ô con tới ô cha.
        goal (tuple): Điểm kết thúc.

    Returns:
        list: Danh sách tọa độ từ bắt đầu đến kết thúc.
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path
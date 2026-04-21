"""Code chứa các thuật toán tìm đường - Bộ não của các nhân vật trong trò chơi"""

from collections import deque
from .config import WALL

DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def in_bounds(grid, pos):
    """
    Hàm in_bounds được sử dụng để kiểm tra xem một vị trí có nằm trong phạm vi của bản đồ hay không. 
    Điều này giúp đảm bảo rằng các nhân vật trong trò chơi không di chuyển ra ngoài ranh giới của bản đồ.
    """
    x, y = pos
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])

def passable(grid, pos, blocked_positions=None):
    """
    Hàm passable được sử dụng để kiểm tra xem một vị trí trên bản đồ có thể đi qua hay không. 
    Nó kiểm tra xem ô đó có phải là tường hay không và cũng kiểm tra xem vị trí đó có bị chặn bởi các yếu tố khác 
    (như vật phẩm hoặc người chơi khác) hay không. Điều này giúp đảm bảo rằng các nhân vật trong trò chơi 
    chỉ di chuyển qua các ô hợp lệ.
    """
    if blocked_positions is None:
        blocked_positions = set()
    x, y = pos
    return grid[y][x] != WALL and pos not in blocked_positions

def bfs_shortest_path(grid, start, goal, blocked_positions=None, passable_fn=None):
    """
    Thuật toán bfs_shortest_path được sử dụng để tìm đường đi ngắn nhất từ một vị trí bắt đầu đến một vị trí mục tiêu 
    trên bản đồ. Nó sử dụng thuật toán tìm kiếm theo chiều rộng (BFS) để duyệt qua các ô trên bản đồ, kiểm tra xem 
    các ô đó có thể đi qua hay không (không phải là tường hoặc bị chặn), và xây dựng một cây đường đi để theo dõi 
    các bước di chuyển. Khi tìm thấy mục tiêu, nó sẽ xây dựng lại đường đi từ cây đường đi và trả về kết quả.
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
    Hàm build_path được sử dụng để xây dựng lại đường đi từ cây đường đi được tạo ra bởi thuật toán BFS. 
    Nó bắt đầu từ vị trí mục tiêu và theo dõi ngược lại đến vị trí bắt đầu bằng cách sử dụng thông tin về cha của mỗi ô 
    trong cây đường đi. Cuối cùng, nó đảo ngược đường đi để trả về kết quả theo thứ tự từ vị trí bắt đầu đến vị trí mục tiêu.
    """
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path
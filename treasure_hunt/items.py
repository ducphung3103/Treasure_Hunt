"""Code chứa items và quản lý việc sinh ra items trên bản đồ"""

import heapq
import random

class Item:
    """Đại diện cho một vật phẩm (ví dụ: freeze) xuất hiện trên bản đồ."""
    def __init__(self, pos, type_name):
        """
        Khởi tạo vật phẩm.

        Args:
            pos (tuple): Vị trí (x, y) trên lưới.
            type_name (str): Tên loại vật phẩm (ví dụ: 'freeze').
        """
        self.pos = pos
        self.type_name = type_name


class ItemSpawner:
    """Quản lý việc sinh vật phẩm ngẫu nhiên và đối xứng trên bản đồ."""
    def __init__(self, candidate_positions):
        """
        Khởi tạo ItemSpawner với danh sách các vị trí tiềm năng.
        Sử dụng heap để ưu tiên các vị trí ít được sử dụng nhất.

        Args:
            candidate_positions (list): Danh sách các tọa độ (x, y) có thể đặt vật phẩm.
        """
        self.candidate_positions = list(candidate_positions)
        self.usage_count = {pos: 0 for pos in self.candidate_positions}
        self.heap = []
        self._rebuild_heap()

    def _rebuild_heap(self):
        """Xây dựng lại heap dựa trên số lần sử dụng hiện tại của từng vị trí."""
        self.heap = []
        for pos, count in self.usage_count.items():
            heapq.heappush(self.heap, (count, random.random(), pos))

    def spawn_item_pair(self, blocked_positions, existing_item_positions, cols):
        """
        Sinh ra một cặp vật phẩm đối xứng trái-phải.

        Args:
            blocked_positions (set): Các vị trí bị nhân vật chiếm giữ.
            existing_item_positions (set): Các vị trí đã có vật phẩm.
            cols (int): Số cột của bản đồ để tính vị trí đối xứng.

        Returns:
            list: Danh sách các đối tượng Item mới được sinh ra.
        """
        blocked_positions = set(blocked_positions)
        existing_item_positions = set(existing_item_positions)

        temp = []
        chosen_pair = None

        while self.heap:
            count, tie_breaker, pos = heapq.heappop(self.heap)
            mirror_pos = (cols - 1 - pos[0], pos[1])

            # Kiểm tra xem cả vị trí gốc và vị trí đối xứng có hợp lệ không
            if (pos in blocked_positions or pos in existing_item_positions or
                mirror_pos in blocked_positions or mirror_pos in existing_item_positions):
                temp.append((count, tie_breaker, pos))
                continue

            chosen_pair = (pos, mirror_pos)
            break

        for entry in temp:
            heapq.heappush(self.heap, entry)

        if chosen_pair is None:
            return []

        pos1, pos2 = chosen_pair
        self.usage_count[pos1] += 1
        heapq.heappush(self.heap, (self.usage_count[pos1], random.random(), pos1))

        if pos1 == pos2:
            return [Item(pos1, "freeze")]
        return [Item(pos1, "freeze"), Item(pos2, "freeze")]
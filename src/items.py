"""Code chứa items và quản lý việc sinh ra items trên bản đồ"""

import heapq
import random

class Item:
    def __init__(self, pos, type_name):
        self.pos = pos
        self.type_name = type_name


class ItemSpawner:
    def __init__(self, candidate_positions):
        """
        Hàm khởi tạo của ItemSpawner nhận vào một tập hợp các vị trí có thể sinh vật phẩm. 
        Nó tạo ra một heap để theo dõi số lần sử dụng của mỗi vị trí, với mục đích đảm bảo rằng các vị trí ít được sử dụng 
        hơn sẽ có cơ hội cao hơn để sinh vật phẩm mới. Heap này được xây dựng dựa trên số lần sử dụng và một giá trị ngẫu nhiên 
        để phá vỡ tình huống hòa khi có nhiều vị trí có cùng số lần sử dụng.
        """
        self.candidate_positions = list(candidate_positions)
        self.usage_count = {pos: 0 for pos in self.candidate_positions}
        self.heap = []
        self._rebuild_heap()

    def _rebuild_heap(self):
        """Hàm _rebuild_heap được sử dụng để xây dựng lại heap dựa trên số lần sử dụng hiện tại của các vị trí."""
        self.heap = []
        for pos, count in self.usage_count.items():
            heapq.heappush(self.heap, (count, random.random(), pos))

    def spawn_item(self, blocked_positions, existing_item_positions):
        """
        Hàm spawn_item được sử dụng để sinh ra một vật phẩm mới trên bản đồ. 
        Nó sẽ lấy một vị trí từ heap, kiểm tra xem vị trí đó có bị chặn hay đã có vật phẩm khác không. 
        Nếu vị trí hợp lệ, nó sẽ chọn vị trí đó để sinh vật phẩm, cập nhật số lần sử dụng và đưa vị trí đó 
        trở lại heap với số lần sử dụng mới. Nếu không tìm thấy vị trí hợp lệ nào, hàm sẽ trả về None.
        """
        blocked_positions = set(blocked_positions)
        existing_item_positions = set(existing_item_positions)
        temp = []
        chosen_pos = None
        while self.heap:
            count, tie_breaker, pos = heapq.heappop(self.heap)
            if pos in blocked_positions or pos in existing_item_positions:
                temp.append((count, tie_breaker, pos))
                continue
            chosen_pos = pos
            break
        for entry in temp:
            heapq.heappush(self.heap, entry)
        if chosen_pos is None:
            return None
        self.usage_count[chosen_pos] += 1
        heapq.heappush(self.heap, (self.usage_count[chosen_pos], random.random(), chosen_pos))
        return Item(chosen_pos, "freeze")
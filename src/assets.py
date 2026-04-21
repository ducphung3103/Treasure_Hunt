import math
import pygame

SHAPE_NAMES = {
    1: "Crown",
    2: "Diamond",
    3: "Sword",
    4: "Triangle",
    5: "Circle",
}


def _clamp(value):
    """
    Giới hạn giá trị màu trong khoảng từ 0 đến 255 để đảm bảo mã màu hợp lệ.
    """
    return max(0, min(255, int(value)))


def shade(color, delta):
    """
    Điều chỉnh độ sáng/tối của một màu sắc dựa trên giá trị delta được cung cấp.
    """
    return tuple(_clamp(channel + delta) for channel in color)


class GameAssets:
    """
    Lớp quản lý và tạo tài nguyên hình ảnh (assets) cho trò chơi.
    """
    def __init__(self, tile_size=40):
        """
        Hàm khởi tạo của GameAssets tạo ra các bề mặt hình ảnh cho các loại gạch khác nhau 
        (sàn, tường, bóng) và các vật phẩm (chìa khóa, rương, vật phẩm đóng băng). 
        Các bề mặt này được lưu trong bộ nhớ đệm (cache) để tránh phải tạo lại chúng nhiều lần, 
        giúp cải thiện hiệu suất khi vẽ trò chơi.
        """
        self.tile_size = tile_size
        self.floor_tile = self._make_floor_tile()
        self.wall_tile = self._make_wall_tile()
        self.shadow_tile = self._make_shadow_tile()
        self.key_cache = {}
        self.chest_cache = {}
        self.item_cache = {
            "freeze": self._make_freeze_item(),
        }

    def make_character_sprite(self, palette, *, kind="player"):
        """
        Hàm make_character_sprite tạo ra một sprite nhân vật dựa trên một bảng màu 
        được cung cấp và loại nhân vật (người chơi hoặc bot).
        """
        size = self.tile_size
        surface = pygame.Surface((size, size), pygame.SRCALPHA)

        # Vẽ bóng dưới chân nhân vật để tạo cảm giác chiều sâu và giúp nhân vật nổi bật hơn trên nền.
        shadow = pygame.Rect(int(size*0.2), size - int(size*0.28), size - int(size*0.4), max(4, int(size*0.2)))
        pygame.draw.ellipse(surface, (18, 20, 24, 70), shadow)

        # Các thông số của từng nhân vật (đã được quy định ở trên)
        skin = palette["skin"]
        hair = palette["hair"]
        outfit = palette["outfit"]
        accent = palette["accent"]
        pants = palette["pants"]

        # Vẽ đầu và tóc của nhân vật, sử dụng các hình dạng cơ bản như hình tròn và hình chữ nhật để tạo ra một thiết kế đơn giản nhưng dễ nhận biết.
        head_r = max(5, size // 6)
        head_y = max(10, size // 3)
        cx = size // 2
        pygame.draw.circle(surface, skin, (cx, head_y), head_r)
        pygame.draw.circle(surface, hair, (cx, head_y - 2), head_r)
        pygame.draw.rect(surface, hair, (cx - head_r, head_y - 2, head_r * 2, max(3, head_r // 2 + 1)), border_radius=3)

        # Vẽ thân và các chi của nhân vật, sử dụng hình chữ nhật để tạo ra một thiết kế đơn giản nhưng hiệu quả. Các chi tiết như bóng và điểm nhấn được thêm vào để tăng cường độ sâu và sự hấp dẫn trực quan của sprite.
        torso_w = max(14, int(size * 0.5))
        torso_h = max(10, int(size * 0.3))
        torso_x = cx - torso_w // 2
        torso_y = head_y + head_r - 1
        pygame.draw.rect(surface, outfit, (torso_x, torso_y, torso_w, torso_h), border_radius=4)
        pygame.draw.rect(surface, accent, (cx - 3, torso_y, 6, torso_h), border_radius=2)
        pygame.draw.rect(surface, shade(outfit, -35), (torso_x, torso_y + torso_h - 3, torso_w, 3), border_radius=1)

        # Vẽ tay và chân của nhân vật, sử dụng hình chữ nhật để tạo ra các chi tiết đơn giản nhưng hiệu quả. Các chi tiết như bóng và điểm nhấn được thêm vào để tăng cường độ sâu và sự hấp dẫn trực quan của sprite.
        arm_w = max(4, size // 8)
        pygame.draw.rect(surface, skin, (torso_x - arm_w + 1, torso_y + 1, arm_w, torso_h - 2), border_radius=2)
        pygame.draw.rect(surface, skin, (torso_x + torso_w - 1, torso_y + 1, arm_w, torso_h - 2), border_radius=2)

        leg_w = max(4, size // 7)
        leg_h = max(7, int(size * 0.2))
        leg_y = torso_y + torso_h
        pygame.draw.rect(surface, pants, (cx - leg_w - 1, leg_y, leg_w, leg_h), border_radius=2)
        pygame.draw.rect(surface, pants, (cx + 1, leg_y, leg_w, leg_h), border_radius=2)
        pygame.draw.rect(surface, (46, 39, 34), (cx - leg_w - 2, leg_y + leg_h - 1, leg_w + 1, 3), border_radius=1)
        pygame.draw.rect(surface, (46, 39, 34), (cx + 1, leg_y + leg_h - 1, leg_w + 1, 3), border_radius=1)

        # Vẽ mắt của nhân vật, sử dụng các hình tròn nhỏ để tạo ra các chi tiết đơn giản nhưng hiệu quả. Màu sắc và vị trí của mắt được thiết kế để tạo ra một biểu cảm thân thiện và dễ nhận biết.
        pygame.draw.circle(surface, (35, 30, 26), (cx - 2, head_y + 1), 1)
        pygame.draw.circle(surface, (35, 30, 26), (cx + 2, head_y + 1), 1)

        # Vẽ sừng cho bot, sử dụng hình tam giác để tạo ra một chi tiết đặc trưng giúp phân biệt bot với người chơi. Sự kết hợp của màu sắc và hình dạng được thiết kế để tạo ra một biểu cảm độc đáo và dễ nhận biết cho bot.
        if kind == "bot":
            horn_y = torso_y - 6
            pygame.draw.polygon(surface, shade(accent, -25), [(cx - 12, horn_y + 8), (cx, horn_y), (cx + 12, horn_y + 8), (cx + 8, horn_y + 12), (cx - 8, horn_y + 12)])
            pygame.draw.rect(surface, shade(outfit, -18), (torso_x, torso_y, torso_w, max(4, torso_h // 2)), border_radius=3)

        pygame.draw.rect(surface, (0, 0, 0, 65), (torso_x, torso_y, torso_w, torso_h), 1, border_radius=4)
        return surface

    def get_key_surface(self, key_id):
        """
        Quản lý chìa khóa bằng cách lưu trữ chúng trong bộ nhớ đệm (cache) để tránh phải tạo lại nhiều lần, 
        giúp cải thiện hiệu suất khi vẽ trò chơi. Kiểm tra xem bề mặt đã tồn tại trong bộ nhớ đệm hay chưa, 
        nếu chưa thì sẽ tạo mới và lưu vào bộ nhớ đệm trước khi trả về.
        """
        if key_id not in self.key_cache:
            self.key_cache[key_id] = self._make_key(key_id)
        return self.key_cache[key_id]

    def get_chest_surface(self, chest_id):
        """
        Quản lý rương bằng cách lưu trữ chúng trong bộ nhớ đệm (cache) tương tự như chìa khóa. 
        Nếu rương chưa có trong cache thì tiến hành tạo mới.
        """
        if chest_id not in self.chest_cache:
            self.chest_cache[chest_id] = self._make_chest(chest_id)
        return self.chest_cache[chest_id]

    def get_item_surface(self, item_type):
        """
        Trả về bề mặt hình ảnh của các vật phẩm (ví dụ: vật phẩm đóng băng) từ bộ nhớ đệm.
        """
        return self.item_cache[item_type]

    def _make_floor_tile(self):
        """
        Tạo bề mặt hình ảnh cho gạch sàn với họa tiết kẻ sọc caro và các điểm nhấn nhỏ.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        base = (132, 234, 86)
        alt = (118, 220, 72)
        pygame.draw.rect(surf, base, (0, 0, s, s), border_radius=2)

        cell = max(4, s // 4)
        for row in range(0, s, cell):
            for col in range(0, s, cell):
                color = alt if ((row // cell) + (col // cell)) % 2 == 0 else base
                pygame.draw.rect(surf, color, (col, row, min(cell, s-col), min(cell, s-row)))

        pygame.draw.rect(surf, (187, 255, 156), (0, 0, s, max(2, s // 10)))
        pygame.draw.rect(surf, (80, 165, 48), (0, s - max(2, s // 10), s, max(2, s // 10)))
        pygame.draw.rect(surf, (255, 255, 255, 26), (0, 0, s, s), 1)

        sparkle_points = [(int(s*0.2), int(s*0.25)), (int(s*0.62), int(s*0.18)), (int(s*0.78), int(s*0.45)), (int(s*0.3), int(s*0.72))]
        for x, y in sparkle_points:
            pygame.draw.circle(surf, (255, 255, 255, 50), (x, y), 1)
        return surf

    def _make_wall_tile(self):
        """
        Vẽ tường với các chi tiết như gạch và bóng để tạo ra một thiết kế trực quan hấp dẫn và dễ nhận biết. 
        Các chi tiết như bóng và điểm nhấn được thêm vào để tăng cường độ sâu và sự hấp dẫn trực quan của bề mặt tường.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        base = (128, 128, 126)
        block_light = (162, 162, 158)
        block_dark = (86, 86, 84)
        border = (66, 66, 64)

        pygame.draw.rect(surf, base, (0, 0, s, s))
        pygame.draw.rect(surf, block_light, (0, 0, s, max(2, s // 10)))
        pygame.draw.rect(surf, block_dark, (0, s - max(3, s // 8), s, max(3, s // 8)))

        brick_h = max(8, s // 2)
        brick_w = max(8, s // 2)
        for row in range(2):
            offset = 0 if row == 0 else brick_w // 2
            y = row * brick_h
            x = -offset
            while x < s:
                rect = pygame.Rect(x, y, brick_w, min(brick_h, s-y))
                pygame.draw.rect(surf, shade(base, 8 if (row + max(0, x) // max(1, brick_w)) % 2 == 0 else -8), rect)
                pygame.draw.rect(surf, border, rect, 1)
                x += brick_w

        dot_color = (218, 218, 216)
        for x, y in [(int(s*0.18), int(s*0.22)), (int(s*0.6), int(s*0.3)), (int(s*0.35), int(s*0.58)), (int(s*0.78), int(s*0.72))]:
            pygame.draw.circle(surf, dot_color, (x, y), 1)
        pygame.draw.rect(surf, (255, 255, 255, 30), (0, 0, s, s), 1)
        return surf

    def _make_shadow_tile(self):
        """
        Vẽ bóng cho gạch sàn để tạo cảm giác chiều sâu và giúp các yếu tố trên bản đồ nổi bật hơn. 
        Bóng được thiết kế để phù hợp với phong cách nghệ thuật của trò chơi, sử dụng màu sắc 
        và độ trong suốt để tạo ra hiệu ứng trực quan hấp dẫn.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 18), (0, s - max(2, s // 10), s, max(2, s // 10)))
        pygame.draw.rect(surf, (0, 0, 0, 9), (s - max(2, s // 10), 0, max(2, s // 10), s))
        return surf

    def _draw_shape_emblem(self, surface, center, shape_id, color, outline):
        """
        Hàm _draw_shape_emblem được sử dụng để vẽ các biểu tượng hình dạng khác nhau trên rương, 
        giúp phân biệt các loại rương khác nhau và tạo thêm sự hấp dẫn trực quan cho trò chơi. 
        Các biểu tượng được thiết kế với các hình dạng cơ bản như vương miện, kim cương, kiếm, 
        tam giác và vòng tròn, mỗi loại có một kiểu dáng đặc trưng và màu sắc riêng biệt.
        """
        cx, cy = center
        if shape_id == 1:
            points = [(cx - 5, cy + 4), (cx - 4, cy - 2), (cx - 1, cy + 1), (cx, cy - 4), (cx + 1, cy + 1), (cx + 4, cy - 2), (cx + 5, cy + 4)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, outline, points, 1)
            pygame.draw.line(surface, outline, (cx - 5, cy + 4), (cx + 5, cy + 4), 1)
        elif shape_id == 2:
            points = [(cx, cy - 5), (cx + 5, cy), (cx, cy + 5), (cx - 5, cy)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, outline, points, 1)
        elif shape_id == 3:
            pygame.draw.rect(surface, color, (cx - 1, cy - 5, 2, 8), border_radius=1)
            pygame.draw.rect(surface, color, (cx - 4, cy + 1, 8, 2), border_radius=1)
            pygame.draw.polygon(surface, color, [(cx, cy - 7), (cx + 2, cy - 4), (cx, cy - 2), (cx - 2, cy - 4)])
            pygame.draw.rect(surface, color, (cx - 2, cy + 3, 4, 2), border_radius=1)
            pygame.draw.rect(surface, color, (cx - 1, cy + 5, 2, 2), border_radius=1)
            pygame.draw.rect(surface, outline, (cx - 1, cy - 5, 2, 8), 1, border_radius=1)
            pygame.draw.rect(surface, outline, (cx - 4, cy + 1, 8, 2), 1, border_radius=1)
            pygame.draw.polygon(surface, outline, [(cx, cy - 7), (cx + 2, cy - 4), (cx, cy - 2), (cx - 2, cy - 4)], 1)
        elif shape_id == 4:
            points = [(cx, cy - 6), (cx + 6, cy + 5), (cx - 6, cy + 5)]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, outline, points, 1)
        elif shape_id == 5:
            pygame.draw.circle(surface, color, (cx, cy), 5)
            pygame.draw.circle(surface, outline, (cx, cy), 5, 1)

    def _make_key(self, key_id):
        """
        Hàm _make_key được sử dụng để tạo bề mặt hình ảnh cho chìa khóa, với các thiết kế 
        khác nhau dựa trên loại chìa khóa (được xác định bởi key_id). Mỗi loại chìa khóa 
        có một thiết kế đặc trưng, sử dụng các hình dạng cơ bản như vương miện, kim cương, 
        kiếm, tam giác và vòng tròn, cùng với các chi tiết như bóng và điểm nhấn để tạo ra 
        một thiết kế trực quan hấp dẫn và dễ nhận biết.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        gold = (243, 183, 33)
        dark_gold = (182, 130, 18)
        shine = (255, 230, 114)
        outline = (97, 70, 8)

        pygame.draw.ellipse(surf, (18, 20, 24, 60), (int(s*0.22), int(s*0.68), int(s*0.5), max(4, int(s*0.16))))

        center = (int(s*0.35), int(s*0.42))
        if key_id == 1:
            crown = [(center[0] - 8, center[1] + 5), (center[0] - 6, center[1] - 5), (center[0] - 2, center[1]), center, (center[0] + 2, center[1]), (center[0] + 6, center[1] - 5), (center[0] + 8, center[1] + 5)]
            pygame.draw.polygon(surf, gold, crown)
            pygame.draw.polygon(surf, outline, crown, 2)
            pygame.draw.rect(surf, gold, (center[0] - 7, center[1] + 3, 14, 4), border_radius=2)
        elif key_id == 2:
            diamond = [(center[0], center[1] - 8), (center[0] + 8, center[1]), (center[0], center[1] + 8), (center[0] - 8, center[1])]
            pygame.draw.polygon(surf, gold, diamond)
            pygame.draw.polygon(surf, outline, diamond, 2)
            inner = [(center[0], center[1] - 4), (center[0] + 4, center[1]), (center[0], center[1] + 4), (center[0] - 4, center[1])]
            pygame.draw.polygon(surf, shine, inner)
        elif key_id == 3:
            pygame.draw.polygon(surf, gold, [(center[0], center[1] - 10), (center[0] + 5, center[1] - 2), (center[0], center[1] + 1), (center[0] - 5, center[1] - 2)])
            pygame.draw.polygon(surf, outline, [(center[0], center[1] - 10), (center[0] + 5, center[1] - 2), (center[0], center[1] + 1), (center[0] - 5, center[1] - 2)], 2)
            pygame.draw.rect(surf, gold, (center[0] - 1, center[1] + 1, 2, 11), border_radius=1)
            pygame.draw.rect(surf, gold, (center[0] - 6, center[1] + 4, 12, 3), border_radius=1)
        elif key_id == 4:
            points = [(center[0], center[1] - 8), (center[0] + 8, center[1] + 6), (center[0] - 8, center[1] + 6)]
            pygame.draw.polygon(surf, gold, points)
            pygame.draw.polygon(surf, outline, points, 2)
        else:
            pygame.draw.circle(surf, gold, center, 8)
            pygame.draw.circle(surf, outline, center, 8, 2)
            pygame.draw.circle(surf, shine, center, 3)

        shaft_x = int(s*0.48)
        shaft_y = int(s*0.4)
        shaft_w = max(10, int(s*0.32))
        pygame.draw.rect(surf, gold, (shaft_x, shaft_y, shaft_w, 4), border_radius=2)
        pygame.draw.rect(surf, gold, (shaft_x + shaft_w - 2, shaft_y, 4, 10), border_radius=2)
        pygame.draw.rect(surf, gold, (shaft_x + shaft_w - 6, shaft_y + 4, 4, 6), border_radius=2)
        pygame.draw.rect(surf, gold, (shaft_x + shaft_w, shaft_y + 6, 3, 4), border_radius=2)
        pygame.draw.rect(surf, dark_gold, (shaft_x, shaft_y + 3, shaft_w + 4, 2), border_radius=1)
        return surf

    def _make_chest(self, chest_id):
        """
        Hàm _make_chest được sử dụng để tạo bề mặt hình ảnh cho rương, với các thiết kế khác nhau 
        dựa trên loại rương (được xác định bởi chest_id). Mỗi loại rương có một thiết kế đặc trưng, 
        sử dụng các hình dạng cơ bản như hình chữ nhật và hình elip, cùng với các chi tiết như bóng 
        và điểm nhấn để tạo ra một thiết kế trực quan hấp dẫn và dễ nhận biết. Các biểu tượng 
        hình dạng khác nhau được vẽ trên rương để giúp phân biệt các loại rương khác nhau.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        wood = (134, 86, 45)
        wood_dark = (95, 59, 30)
        gold = (233, 183, 43)

        pygame.draw.ellipse(surf, (18, 20, 24, 65), (int(s*0.2), int(s*0.72), int(s*0.6), max(4, int(s*0.16))))
        body = pygame.Rect(int(s*0.18), int(s*0.38), int(s*0.65), int(s*0.4))
        lid = pygame.Rect(int(s*0.18), int(s*0.24), int(s*0.65), int(s*0.24))
        pygame.draw.rect(surf, wood, body, border_radius=4)
        pygame.draw.rect(surf, wood_dark, body, 2, border_radius=4)
        pygame.draw.rect(surf, shade(wood, 16), lid, border_radius=6)
        pygame.draw.rect(surf, wood_dark, lid, 2, border_radius=6)
        pygame.draw.rect(surf, gold, (int(s*0.42), int(s*0.28), max(5, int(s*0.14)), int(s*0.42)), border_radius=2)
        pygame.draw.line(surf, wood_dark, (body.x, int(s*0.52)), (body.right, int(s*0.52)), 2)
        self._draw_shape_emblem(surf, (int(s*0.7), int(s*0.34)), chest_id, (244, 228, 154), (120, 85, 10))
        return surf

    def _make_freeze_item(self):
        """
        Hàm _make_freeze_item được sử dụng để tạo bề mặt hình ảnh cho vật phẩm đóng băng, 
        với một thiết kế đặc trưng sử dụng các hình dạng cơ bản như hình elip và đường thẳng, 
        cùng với các chi tiết như bóng và điểm nhấn để tạo ra một thiết kế trực quan hấp dẫn 
        và dễ nhận biết. Thiết kế của vật phẩm đóng băng được lấy cảm hứng từ hình dạng của 
        một bông tuyết, với các đường thẳng tỏa ra từ trung tâm và một vòng tròn bao quanh 
        để tạo ra hiệu ứng đóng băng.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        cyan = (85, 224, 255)
        deep = (36, 139, 171)
        pygame.draw.ellipse(surf, (18, 20, 24, 60), (int(s*0.2), int(s*0.68), int(s*0.6), max(4, int(s*0.16))))
        center = (s // 2, int(s * 0.45))
        for angle in range(0, 180, 45):
            rad = math.radians(angle)
            dx = int(math.cos(rad) * (s * 0.22))
            dy = int(math.sin(rad) * (s * 0.22))
            pygame.draw.line(surf, cyan, (center[0] - dx, center[1] - dy), (center[0] + dx, center[1] + dy), max(2, s // 12))
        pygame.draw.circle(surf, deep, center, max(6, s // 5), 2)
        return surf
import math
import pygame

from .config import KEY_COLOR_LOOKUP


def _clamp(value):
    return max(0, min(255, int(value)))


def shade(color, delta):
    return tuple(_clamp(channel + delta) for channel in color)


class GameAssets:
    """
    Lớp quản lý và tạo tài nguyên hình ảnh (sprites) cho trò chơi.
    Hỗ trợ cache để tối ưu hiệu năng, tránh tạo lại hình ảnh nhiều lần.
    """

    def __init__(self, tile_size=40):
        """
        Khởi tạo GameAssets và tạo các tile cơ bản.

        Args:
            tile_size (int): Kích thước của mỗi ô vuông (pixel).
        """
        self.tile_size = tile_size
        self.floor_tile = self._make_floor_tile()
        self.wall_tile = self._make_wall_tile()
        self.shadow_tile = self._make_shadow_tile()
        self.key_cache = {}
        self.chest_cache = {}
        self.item_cache = {"freeze": self._make_freeze_item()}

    def make_character_sprite(self, palette, *, kind="player"):
        """
        Tạo hình ảnh (sprite) cho nhân vật dựa trên bảng màu và loại nhân vật.

        Args:
            palette (dict): Bảng màu cho da, tóc, trang phục...
            kind (str): 'player' hoặc 'bot'.

        Returns:
            pygame.Surface: Hình ảnh nhân vật đã vẽ xong.
        """
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (18, 20, 24, 70), (int(s * 0.2), int(s * 0.73), int(s * 0.6), max(4, int(s * 0.18))))

        skin = palette["skin"]
        hair = palette["hair"]
        outfit = palette["outfit"]
        accent = palette["accent"]
        pants = palette["pants"]
        cx = s // 2
        head_r = max(4, s // 6)
        head_y = max(8, s // 3)
        pygame.draw.circle(surf, skin, (cx, head_y), head_r)
        pygame.draw.rect(surf, hair, (cx - head_r, head_y - head_r, head_r * 2, max(4, head_r)), border_radius=3)

        torso_w = max(10, int(s * 0.5))
        torso_h = max(8, int(s * 0.3))
        torso_x = cx - torso_w // 2
        torso_y = head_y + head_r - 1
        pygame.draw.rect(surf, outfit, (torso_x, torso_y, torso_w, torso_h), border_radius=4)
        pygame.draw.rect(surf, accent, (cx - max(1, s // 18), torso_y, max(2, s // 9), torso_h), border_radius=2)

        arm_w = max(3, s // 8)
        pygame.draw.rect(surf, skin, (torso_x - arm_w + 1, torso_y + 1, arm_w, torso_h - 2), border_radius=2)
        pygame.draw.rect(surf, skin, (torso_x + torso_w - 1, torso_y + 1, arm_w, torso_h - 2), border_radius=2)

        leg_w = max(3, s // 7)
        leg_h = max(5, int(s * 0.2))
        leg_y = torso_y + torso_h
        pygame.draw.rect(surf, pants, (cx - leg_w - 1, leg_y, leg_w, leg_h), border_radius=2)
        pygame.draw.rect(surf, pants, (cx + 1, leg_y, leg_w, leg_h), border_radius=2)
        pygame.draw.circle(surf, (35, 30, 26), (cx - max(1, s // 18), head_y + 1), max(1, s // 35))
        pygame.draw.circle(surf, (35, 30, 26), (cx + max(1, s // 18), head_y + 1), max(1, s // 35))

        if kind == "bot":
            horn_y = torso_y - max(3, s // 7)
            pygame.draw.polygon(surf, shade(accent, -25), [(cx - s // 4, horn_y + s // 5), (cx, horn_y), (cx + s // 4, horn_y + s // 5)])
            pygame.draw.rect(surf, shade(outfit, -18), (torso_x, torso_y, torso_w, max(4, torso_h // 2)), border_radius=3)

        pygame.draw.rect(surf, (0, 0, 0, 70), (torso_x, torso_y, torso_w, torso_h), 1, border_radius=4)
        return surf

    def get_key_surface(self, color_id, size_tier="medium"):
        """Lấy sprite chìa khóa từ cache hoặc tạo mới nếu chưa có."""
        cache_key = (color_id, size_tier)
        if cache_key not in self.key_cache:
            self.key_cache[cache_key] = self._make_key(color_id, size_tier)
        return self.key_cache[cache_key]

    def get_chest_surface(self, color_id):
        """Lấy sprite rương từ cache hoặc tạo mới nếu chưa có."""
        if color_id not in self.chest_cache:
            self.chest_cache[color_id] = self._make_chest(color_id)
        return self.chest_cache[color_id]

    def get_item_surface(self, item_type):
        """Lấy sprite vật phẩm dựa trên loại."""
        return self.item_cache[item_type]

    def _make_floor_tile(self):
        """Hàm nội bộ vẽ tile sàn nhà."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        base = (92, 98, 122)
        alt = (84, 90, 114)
        mortar = (128, 118, 150)
        pygame.draw.rect(surf, base, (0, 0, s, s), border_radius=2)
        block = max(4, s // 2)
        for y in range(0, s, block):
            for x in range(0, s, block):
                color = alt if ((x // block) + (y // block)) % 2 == 0 else base
                pygame.draw.rect(surf, color, (x, y, min(block, s - x), min(block, s - y)))
        for i in range(0, s + 1, block):
            pygame.draw.line(surf, mortar, (i, 0), (i, s), 1)
            pygame.draw.line(surf, mortar, (0, i), (s, i), 1)
        pygame.draw.circle(surf, (104, 233, 255, 18), (int(s * 0.28), int(s * 0.22)), max(2, s // 9))
        pygame.draw.circle(surf, (197, 122, 255, 15), (int(s * 0.75), int(s * 0.74)), max(2, s // 10))
        pygame.draw.rect(surf, (255, 255, 255, 14), (0, 0, s, s), 1)
        return surf

    def _make_wall_tile(self):
        """Hàm nội bộ vẽ tile tường."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        base = (43, 46, 56)
        dark = (24, 26, 33)
        light = (74, 78, 92)
        pygame.draw.rect(surf, base, (0, 0, s, s))
        pygame.draw.rect(surf, light, (0, 0, s, max(2, s // 10)))
        pygame.draw.rect(surf, dark, (0, s - max(2, s // 8), s, max(2, s // 8)))
        bw = max(7, s // 2)
        bh = max(7, s // 2)
        for row in range(2):
            off = 0 if row == 0 else bw // 2
            for x in range(-off, s, bw):
                rect = pygame.Rect(x, row * bh, bw, bh)
                pygame.draw.rect(surf, (56, 60, 72), rect, 0)
                pygame.draw.rect(surf, dark, rect, 1)
        pygame.draw.circle(surf, (86, 67, 108, 26), (int(s * 0.28), int(s * 0.32)), max(2, s // 8))
        pygame.draw.circle(surf, (61, 119, 125, 20), (int(s * 0.72), int(s * 0.68)), max(2, s // 10))
        return surf

    def _make_shadow_tile(self):
        """Hàm nội bộ vẽ hiệu ứng bóng đổ cho các ô sàn."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 0, 0, 32), (0, s - max(2, s // 10), s, max(2, s // 10)))
        pygame.draw.rect(surf, (38, 25, 56, 14), (0, 0, s, s))
        return surf

    def _make_key(self, color_id, size_tier):
        """Hàm nội bộ vẽ hình chìa khóa."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        color = KEY_COLOR_LOOKUP[color_id]["rgb"]
        outline = (245, 242, 235)
        halo = color if color_id != 5 else (194, 160, 255)
        factor = {"small": 0.80, "medium": 0.96, "large": 1.10}.get(size_tier, 0.96)
        cx = int(s * 0.36)
        cy = int(s * 0.44)
        r = max(4, int(s * 0.17 * factor))
        shaft_len = max(7, int(s * 0.34 * factor))
        shaft_h = max(2, int(s * 0.11 * factor))
        for rr, alpha in ((int(s * 0.34 * factor), 26), (int(s * 0.26 * factor), 36), (int(s * 0.20 * factor), 48)):
            pygame.draw.circle(surf, (*halo, alpha), (cx, cy), rr)
        pygame.draw.ellipse(surf, (18, 20, 24, 68), (int(s * 0.18), int(s * 0.72), int(s * 0.58), max(3, int(s * 0.12))))
        pygame.draw.circle(surf, color, (cx, cy), r)
        pygame.draw.circle(surf, outline, (cx, cy), r, max(2, s // 18))
        pygame.draw.circle(surf, (255, 255, 255, 150), (cx - r // 3, cy - r // 3), max(1, r // 4))
        sx = cx + r - 1
        sy = cy - shaft_h // 2
        pygame.draw.rect(surf, color, (sx, sy, shaft_len, shaft_h), border_radius=max(1, shaft_h // 2))
        pygame.draw.rect(surf, outline, (sx, sy, shaft_len, shaft_h), max(2, s // 24), border_radius=max(1, shaft_h // 2))
        tooth_w = max(2, shaft_h)
        pygame.draw.rect(surf, color, (sx + shaft_len - tooth_w, sy, tooth_w, max(4, shaft_h * 3)), border_radius=1)
        pygame.draw.rect(surf, color, (sx + shaft_len - tooth_w * 3, sy + shaft_h, tooth_w, max(3, shaft_h * 2)), border_radius=1)
        pygame.draw.rect(surf, outline, (sx + shaft_len - tooth_w, sy, tooth_w, max(4, shaft_h * 3)), max(1, s // 28), border_radius=1)
        pygame.draw.rect(surf, outline, (sx + shaft_len - tooth_w * 3, sy + shaft_h, tooth_w, max(3, shaft_h * 2)), max(1, s // 28), border_radius=1)
        return surf

    def _make_chest(self, color_id):
        """Hàm nội bộ vẽ hình rương báu."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        color = KEY_COLOR_LOOKUP[color_id]["rgb"]
        outline = (20, 20, 20) if color_id != 5 else (235, 235, 235)
        wood = shade(color, -20)
        lid = shade(color, 25)
        if color_id == 6:
            wood = (230, 230, 225)
            lid = (255, 255, 255)
        pygame.draw.ellipse(surf, (18, 20, 24, 65), (int(s * 0.19), int(s * 0.73), int(s * 0.62), max(4, int(s * 0.15))))
        body = pygame.Rect(int(s * 0.18), int(s * 0.40), int(s * 0.65), int(s * 0.38))
        top = pygame.Rect(int(s * 0.18), int(s * 0.25), int(s * 0.65), int(s * 0.24))
        pygame.draw.rect(surf, wood, body, border_radius=max(3, s // 9))
        pygame.draw.rect(surf, outline, body, max(1, s // 20), border_radius=max(3, s // 9))
        pygame.draw.rect(surf, lid, top, border_radius=max(3, s // 8))
        pygame.draw.rect(surf, outline, top, max(1, s // 20), border_radius=max(3, s // 8))
        lock = pygame.Rect(int(s * 0.44), int(s * 0.45), max(4, int(s * 0.13)), max(4, int(s * 0.16)))
        pygame.draw.rect(surf, (240, 205, 76), lock, border_radius=2)
        pygame.draw.rect(surf, outline, lock, 1, border_radius=2)
        return surf

    def _make_freeze_item(self):
        """Hàm nội bộ vẽ hình vật phẩm đóng băng (bông tuyết)."""
        s = self.tile_size
        surf = pygame.Surface((s, s), pygame.SRCALPHA)
        cyan = (112, 233, 255)
        deep = (137, 88, 194)
        pygame.draw.ellipse(surf, (18, 20, 24, 70), (int(s * 0.2), int(s * 0.68), int(s * 0.6), max(4, int(s * 0.16))))
        center = (s // 2, int(s * 0.45))
        for angle in range(0, 180, 45):
            rad = math.radians(angle)
            dx = int(math.cos(rad) * (s * 0.22))
            dy = int(math.sin(rad) * (s * 0.22))
            pygame.draw.line(surf, cyan, (center[0] - dx, center[1] - dy), (center[0] + dx, center[1] + dy), max(2, s // 12))
        pygame.draw.circle(surf, deep, center, max(5, s // 5), max(1, s // 20))
        pygame.draw.circle(surf, (255, 255, 255, 90), center, max(2, s // 10))
        return surf

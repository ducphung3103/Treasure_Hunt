"""Phần UI của trò chơi"""

from __future__ import annotations

import pygame

from .assets import SHAPE_NAMES
from .config import (
    ACCENT_DARK,
    BLACK,
    CARD_BG,
    DANGER,
    PANEL_BG,
    PANEL_BORDER,
    PANEL_HEIGHT,
    PANEL_WIDTH,
    PANEL_X,
    PANEL_Y,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SUCCESS,
    TEXT_MUTED,
    TEXT_SOFT,
    WHITE,
)


def fit_text(font, text, max_width):
    """
    Hàm fit_text được sử dụng để điều chỉnh văn bản sao cho vừa với một chiều rộng tối đa nhất định. 
    Nếu văn bản quá dài để vừa với chiều rộng đó, nó sẽ cắt bớt văn bản và thêm dấu "..." vào cuối 
    để chỉ ra rằng văn bản đã bị cắt ngắn. Điều này giúp đảm bảo rằng giao diện người dùng vẫn gọn gàng và dễ đọc.
    """
    if font.size(text)[0] <= max_width:
        return text
    trimmed = text
    while trimmed and font.size(trimmed + "...")[0] > max_width:
        trimmed = trimmed[:-1]
    return trimmed + "..." if trimmed else "..."


def draw_text(surface, text, font, color, pos):
    """
    Hàm draw_text được sử dụng để vẽ văn bản lên một bề mặt (surface) trong Pygame. 
    Nó nhận vào bề mặt, chuỗi văn bản, font chữ, màu sắc và vị trí để vẽ văn bản. 
    Hàm này giúp đơn giản hóa quá trình hiển thị văn bản trong trò chơi.
    """
    image = font.render(text, True, color)
    surface.blit(image, pos)


def draw_round_rect(surface, rect, fill, border=None, radius=16, width=1):
    """
    Hàm draw_round_rect được sử dụng để vẽ một hình chữ nhật có các góc bo tròn lên một bề mặt trong Pygame. 
    Nó nhận vào bề mặt, hình chữ nhật (dưới dạng pygame.Rect), màu sắc điền, màu sắc viền, bán kính góc và độ dày viền.
    """
    if isinstance(fill, (tuple, list)) and len(fill) == 4:
        temp = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(temp, fill, temp.get_rect(), border_radius=radius)
        surface.blit(temp, rect.topleft)
    else:
        pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border is not None:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)


def draw_button(surface, rect, text, fonts, *, fill=WHITE, border=PANEL_BORDER, text_color=BLACK):
    """
    Hàm draw_button được sử dụng để vẽ một nút có thiết kế bo tròn lên một bề mặt trong Pygame. 
    Nó nhận vào bề mặt, hình chữ nhật xác định vị trí và kích thước của nút, văn bản hiển thị trên nút, 
    font chữ, màu sắc điền, màu sắc viền và màu sắc của văn bản. Hàm này giúp tạo ra các nút giao diện người dùng hấp dẫn.
    """
    draw_round_rect(surface, rect, fill, border, radius=14, width=2)
    label = fonts.get("button", fonts["small"]).render(text, True, text_color)
    surface.blit(label, label.get_rect(center=rect.center))
    return rect


def draw_background(surface):
    """
    Hàm draw_background được sử dụng để vẽ nền cho trò chơi bằng cách tạo ra một gradient màu sắc từ trên xuống dưới. 
    Nó sử dụng hai màu sắc (top và bottom) và vẽ các đường ngang liên tiếp với màu sắc được pha trộn giữa hai màu đó 
    dựa trên vị trí y của đường. Điều này giúp tạo ra một nền đẹp mắt và trực quan cho trò chơi.
    """
    top = pygame.Color(69, 109, 183)
    bottom = pygame.Color(43, 74, 125)
    width, height = surface.get_size()
    for y in range(height):
        blend = y / max(1, height - 1)
        color = top.lerp(bottom, blend)
        pygame.draw.line(surface, color, (0, y), (width, y))


def _shape_label(shape_id):
    """
    Hàm _shape_label được sử dụng để tạo ra một nhãn mô tả cho một loại chìa khóa dựa trên ID của nó. 
    Nó tra cứu tên của hình dạng tương ứng với ID trong một từ điển SHAPE_NAMES và trả về một chuỗi 
    có định dạng "{Tên Hình} Key". Điều này giúp người chơi dễ dàng nhận biết loại chìa khóa mà họ đang giữ.
    """
    return f"{SHAPE_NAMES.get(shape_id, 'Unknown')} Key"


def _effect_label(character):
    """
    Hàm _effect_label được sử dụng để tạo ra một nhãn mô tả cho hiệu ứng hiện tại của một nhân vật trong trò chơi. 
    Nếu nhân vật đang bị đóng băng, nó sẽ trả về một chuỗi có định dạng "Frozen ({số lượt đóng băng còn lại})". 
    Nếu không có hiệu ứng nào đang hoạt động, nó sẽ trả về "None".
    """
    if character.is_frozen():
        return f"Frozen ({character.freeze_turns})"
    return "None"


def _turn_status_text(game):
    """
    Hàm _turn_status_text được sử dụng để tạo ra một chuỗi văn bản mô tả trạng thái hiện tại của lượt chơi trong trò chơi. 
    Nó kiểm tra xem có bao nhiêu người chơi đang tham gia và liệu họ đã sẵn sàng cho lượt tiếp theo hay chưa.
    Nếu có nhiều người chơi, nó sẽ hiển thị tên của mỗi người chơi cùng với trạng thái "Ready" hoặc "Waiting".
    """
    humans = [character for character in game.characters if hasattr(character, "control_index")]
    if game.game_over:
        return "Match finished. Use Replay or Main Menu to continue."
    if len(humans) == 1:
        player = humans[0]
        if game.pending_human_moves.get(player.control_index) is None:
            return f"{player.name}: choose one direction to resolve the next turn."
        return f"{player.name}: ready. Bots will move on the same turn."
    pieces = []
    for player in humans:
        ready = game.pending_human_moves.get(player.control_index) is not None
        pieces.append(f"{player.name} {'Ready' if ready else 'Waiting'}")
    return " | ".join(pieces)


def draw_side_panel(surface, fonts, game):
    """
    Đây là hàm chính để vẽ bảng điều khiển bên cạnh bản đồ trong trò chơi. Nó hiển thị thông tin về trận đấu hiện tại, 
    bao gồm tên bản đồ, kích thước bản đồ, số lượt còn lại, trạng thái của từng nhân vật (người chơi và bot), 
    và các nút hành động nhanh như "Reset", "New Maze", "Main Menu" và "Replay".
    """
    # Vẽ nền và khung cho bảng điều khiển bên cạnh bản đồ
    panel = pygame.Rect(PANEL_X, PANEL_Y, PANEL_WIDTH, PANEL_HEIGHT)
    shadow = pygame.Rect(panel.x + 6, panel.y + 8, panel.w, panel.h)
    draw_round_rect(surface, shadow, (0, 0, 0, 40), None, radius=24)
    draw_round_rect(surface, panel, PANEL_BG, PANEL_BORDER, radius=24, width=2)

    # Căn chỉnh văn bản và thông số tổng quan
    left = panel.x + 18
    width = panel.w - 36

    draw_text(surface, "Match Overview", fonts["title"], BLACK, (left, panel.y + 16))
    draw_text(surface, fit_text(fonts["normal"], game.level_name, width), fonts["normal"], ACCENT_DARK, (left, panel.y + 46))
    draw_text(surface, f"Map Size: {game.current_map_size['label']}", fonts["small"], TEXT_MUTED, (left, panel.y + 76))
    draw_text(surface, f"Seed: {game.current_seed}", fonts["small"], TEXT_MUTED, (left + 145, panel.y + 76))
    draw_text(surface, fit_text(fonts["small"], f"Mode: {game.current_mode['label']}", width), fonts["small"], TEXT_MUTED, (left, panel.y + 98))
    draw_text(surface, f"Turns Left: {game.get_turns_left()}/{game.current_step_option['turn_limit']}", fonts["small"], BLACK, (left, panel.y + 120))

    status_card = pygame.Rect(left, panel.y + 144, width, 48)
    draw_round_rect(surface, status_card, CARD_BG, PANEL_BORDER, radius=16)
    draw_text(surface, fit_text(fonts["small"], _turn_status_text(game), status_card.w - 20), fonts["small"], BLACK, (status_card.x + 10, status_card.y + 15))

    # Căn chỉnh các thẻ thông tin (player cards)
    characters = game.characters
    y = panel.y + 206
    gap = 8
    reserved_bottom = 144
    available = panel.bottom - reserved_bottom - y
    card_count = max(1, len(characters))
    card_h = max(46, min(58, (available - gap * (card_count - 1)) // card_count))

    for index, character in enumerate(characters):
        card = pygame.Rect(left, y, width, card_h)
        draw_round_rect(surface, card, CARD_BG, PANEL_BORDER, radius=16)
        color_bar = pygame.Rect(card.x + 10, card.y + 10, 8, card_h - 20)
        pygame.draw.rect(surface, character.color, color_bar, border_radius=5)

        role = "Player" if index < game.current_mode["humans"] else "Bot"
        draw_text(surface, fit_text(fonts["normal"], character.name, 108), fonts["normal"], BLACK, (card.x + 28, card.y + 4))
        draw_text(surface, role, fonts["tiny"], TEXT_MUTED, (card.x + 28, card.y + 26))

        draw_text(surface, f"Score: {character.score}", fonts["small"], BLACK, (card.x + 132, card.y + 6))
        if character.held_key_id is not None:
            icon = pygame.transform.smoothscale(game.assets.get_key_surface(character.held_key_id), (16, 16))
            surface.blit(icon, (card.x + 132, card.y + 26))
            draw_text(surface, fit_text(fonts["small"], _shape_label(character.held_key_id), 92), fonts["small"], BLACK, (card.x + 152, card.y + 25))
        else:
            draw_text(surface, "Key: None", fonts["small"], BLACK, (card.x + 132, card.y + 24))

        effect = _effect_label(character)
        effect_color = DANGER if effect.startswith("Frozen") else TEXT_SOFT
        draw_text(surface, fit_text(fonts["small"], effect, 84), fonts["small"], effect_color, (card.right - 96, card.y + 6))
        if hasattr(character, "control_label"):
            draw_text(surface, fit_text(fonts["tiny"], character.control_label(), 84), fonts["tiny"], TEXT_SOFT, (card.right - 96, card.y + 25))
        y += card_h + gap

    # Căn chỉnh phần "Quick Actions"
    action_y = panel.bottom - 128
    draw_text(surface, "Quick Actions", fonts["normal"], BLACK, (left, action_y))
    draw_text(surface, fit_text(fonts["tiny"], "Reset keeps the same maze. New Maze generates a fresh random map.", width), fonts["tiny"], TEXT_MUTED, (left, action_y + 22))

    # Căn chỉnh các nút hành động nhanh
    buttons = {}
    row1_y = action_y + 42
    row2_y = action_y + 82
    btn_w = (width - 14) // 2
    btn_h = 32
    x1 = left
    x2 = left + btn_w + 14

    buttons["reset"] = draw_button(surface, pygame.Rect(x1, row1_y, btn_w, btn_h), "Reset", fonts)
    buttons["next_map"] = draw_button(surface, pygame.Rect(x2, row1_y, btn_w, btn_h), "New Maze", fonts)
    buttons["menu"] = draw_button(surface, pygame.Rect(x1, row2_y, btn_w, btn_h), "Main Menu", fonts)
    buttons["replay"] = draw_button(surface, pygame.Rect(x2, row2_y, btn_w, btn_h), "Replay", fonts)

    hint = "The entire UI scales with the window. Resize or maximize the app normally."
    draw_text(surface, fit_text(fonts["tiny"], hint, width), fonts["tiny"], TEXT_MUTED, (left, panel.bottom - 16))
    return buttons


def draw_legend(surface, fonts):
    """
    Hàm draw_legend được sử dụng để vẽ một chú giải (legend) lên một bề mặt trong Pygame, 
    cung cấp thông tin về ý nghĩa của các biểu tượng hoặc màu sắc được sử dụng trong trò chơi.
    """
    draw_text(surface, "Purple item = Freeze every other character for 3 turns", fonts["small"], BLACK, (40, 20))


def draw_menu(surface, fonts, size_label, size_description, mode_label, steps_label):
    """
    Đây là hàm chính để vẽ menu chính của trò chơi, nơi người chơi có thể chọn kích thước bản đồ, 
    chế độ chơi và số lượt trước khi bắt đầu trận đấu. Menu này được thiết kế với một giao diện 
    trực quan và hấp dẫn, sử dụng các thẻ (cards) để hiển thị các tùy chọn và các nút điều hướng.
    """
    draw_background(surface)

    # Căn chỉnh kích thước và vị trí cho menu chính
    surface_w, surface_h = surface.get_size()
    box_margin_x = max(36, int(surface_w * 0.065))
    box_margin_y = max(26, int(surface_h * 0.045))
    box = pygame.Rect(box_margin_x, box_margin_y, surface_w - box_margin_x * 2, surface_h - box_margin_y * 2)
    draw_round_rect(surface, box, (247, 249, 252), PANEL_BORDER, radius=30, width=2)

    # Căn chỉnh tiêu đề và thông tin phụ trong menu chính
    title_x = box.x + 30
    draw_text(surface, "Treasure Hunt", fonts["display"], BLACK, (title_x, box.y + 22))
    subtitle = "Choose the map size, game mode, and turn count. A new random maze will be generated when you start."
    draw_text(surface, fit_text(fonts["small"], subtitle, box.w - 60), fonts["small"], TEXT_MUTED, (title_x, box.y + 72))

    # Căn chỉnh các thẻ thông tin
    buttons = {}
    inner_x = box.x + 22
    inner_w = box.w - 44
    card_gap = 14
    card_h = 108
    card1 = pygame.Rect(inner_x, box.y + 112, inner_w, card_h)
    card2 = pygame.Rect(inner_x, card1.bottom + card_gap, inner_w, card_h)
    card3 = pygame.Rect(inner_x, card2.bottom + card_gap, inner_w, card_h)
    card4 = pygame.Rect(inner_x, card3.bottom + card_gap, inner_w, 88)
    for card in (card1, card2, card3, card4):
        draw_round_rect(surface, card, CARD_BG, PANEL_BORDER, radius=20)

    arrow_w = 42
    arrow_h = 42

    def selector_card(card, title, value, prev_key, next_key, subtitle_text=None):
        # Căn chỉnh phần tử bên trong thẻ (selector cards)
        title_y = card.y + 12
        draw_text(surface, title, fonts["small"], BLACK, (card.x + 20, title_y))

        value_box_y = title_y + 24
        value_box = pygame.Rect(card.x + 72, value_box_y, card.w - 144, 38)
        draw_round_rect(surface, value_box, (236, 241, 249), PANEL_BORDER, radius=18)

        value_font = fonts["title"] if fonts["title"].size(value)[0] <= value_box.w - 24 else fonts["normal"]
        draw_text(surface, fit_text(value_font, value, value_box.w - 24), value_font, ACCENT_DARK, (value_box.x + 14, value_box.y + 5))

        buttons[prev_key] = draw_button(surface, pygame.Rect(card.x + 16, value_box.y - 2, arrow_w, arrow_h), "<", fonts, fill=(255, 245, 224))
        buttons[next_key] = draw_button(surface, pygame.Rect(card.right - 16 - arrow_w, value_box.y - 2, arrow_w, arrow_h), ">", fonts, fill=(255, 245, 224))

        if subtitle_text:
            subtitle_y = value_box.bottom + 8
            draw_text(surface, fit_text(fonts["small"], subtitle_text, card.w - 108), fonts["small"], TEXT_MUTED, (card.x + 76, subtitle_y))

    selector_card(card1, "Map Size", size_label, "size_prev", "size_next", size_description)
    selector_card(card2, "Game Mode", mode_label, "mode_prev", "mode_next", "Choose how many human players and bots join the match.")
    selector_card(card3, "Step Count", steps_label, "steps_prev", "steps_next", "More turns create longer matches and larger comeback windows.")

    draw_text(surface, "Window", fonts["small"], BLACK, (card4.x + 20, card4.y + 14))
    draw_text(surface, fit_text(fonts["small"], "UI panels resize with the window, just like a normal desktop app.", card4.w - 40), fonts["small"], TEXT_MUTED, (card4.x + 20, card4.y + 40))
    draw_text(surface, fit_text(fonts["small"], "You can drag the window edges or maximize it. The layout will adapt.", card4.w - 40), fonts["small"], TEXT_MUTED, (card4.x + 20, card4.y + 60))

    # Căn chỉnh nút Start Game
    start_w = min(240, inner_w)
    buttons["start"] = draw_button(
        surface,
        pygame.Rect(box.centerx - start_w // 2, box.bottom - 62, start_w, 44),
        "Start Game",
        fonts,
        fill=(228, 246, 230),
        border=SUCCESS,
    )
    return buttons
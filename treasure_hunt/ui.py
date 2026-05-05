"""Vẽ giao diện menu và HUD trận đấu."""

from __future__ import annotations

import math
import pygame

from .config import (
    ACCENT_DARK,
    CARD_BG,
    CARD_HIGHLIGHT,
    DANGER,
    KEY_COLOR_LOOKUP,
    PANEL_BG,
    PANEL_BORDER,
    SUCCESS,
    TEXT_MUTED,
    TEXT_SOFT,
    WHITE,
)


def fit_text(font, text, max_width):
    """
    Cắt ngắn chuỗi văn bản và thêm dấu '...' nếu nó vượt quá độ rộng cho phép.

    Args:
        font (pygame.font.Font): Font chữ sử dụng.
        text (str): Văn bản cần kiểm tra.
        max_width (int): Độ rộng tối đa (pixel).

    Returns:
        str: Văn bản đã được xử lý để vừa khít.
    """
    if font.size(text)[0] <= max_width:
        return text
    trimmed = text
    while trimmed and font.size(trimmed + "...")[0] > max_width:
        trimmed = trimmed[:-1]
    return trimmed + "..." if trimmed else "..."


def draw_text(surface, text, font, color, pos):
    """
    Vẽ văn bản lên bề mặt surface.

    Args:
        surface (pygame.Surface): Bề mặt để vẽ.
        text (str): Nội dung văn bản.
        font (pygame.font.Font): Font chữ.
        color (tuple): Màu sắc (RGB).
        pos (tuple): Tọa độ (x, y).
    """
    image = font.render(text, True, color)
    surface.blit(image, pos)


def draw_round_rect(surface, rect, fill, border=None, radius=16, width=1):
    """
    Vẽ một hình chữ nhật bo góc, hỗ trợ cả màu đặc và màu có độ trong suốt (alpha).

    Args:
        surface (pygame.Surface): Bề mặt để vẽ.
        rect (pygame.Rect): Kích thước và vị trí.
        fill (tuple): Màu nền.
        border (tuple, optional): Màu viền.
        radius (int): Bán kính bo góc.
        width (int): Độ dày viền.
    """
    if isinstance(fill, (tuple, list)) and len(fill) == 4:
        temp = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        pygame.draw.rect(temp, fill, temp.get_rect(), border_radius=radius)
        surface.blit(temp, rect.topleft)
    else:
        pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if border is not None:
        pygame.draw.rect(surface, border, rect, width, border_radius=radius)


def draw_button(surface, rect, text, fonts, *, fill=WHITE, border=PANEL_BORDER, text_color=(20, 20, 20)):
    """
    Vẽ một nút bấm có văn bản ở giữa.

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        rect (pygame.Rect): Vùng nút bấm.
        text (str): Nhãn nút bấm.
        fonts (dict): Từ điển chứa các font chữ.
        fill (tuple): Màu nền nút.
        border (tuple): Màu viền nút.
        text_color (tuple): Màu chữ.

    Returns:
        pygame.Rect: Trả về chính rect của nút để dùng cho xử lý va chạm.
    """
    draw_round_rect(surface, rect, fill, border, radius=14, width=2)
    label = fonts.get("button", fonts["small"]).render(text, True, text_color)
    surface.blit(label, label.get_rect(center=rect.center))
    return rect


def draw_background(surface, tick_ms=None):
    """
    Vẽ nền động với hiệu ứng gradient và các ngôi sao lấp lánh trôi nhẹ.

    Args:
        surface (pygame.Surface): Bề mặt vẽ nền.
        tick_ms (int, optional): Thời gian hiện tại tính bằng mili giây.
    """
    if tick_ms is None:
        tick_ms = pygame.time.get_ticks()
    width, height = surface.get_size()
    t = tick_ms / 1000.0

    # 1. Smooth Colorful Gradient (Deep Navy to Purple/Blue)
    grad_surf = pygame.Surface((1, 3), pygame.SRCALPHA)
    colors = [
        (10, 8, 24),   # Deep Purple-Black (Top)
        (15, 20, 50),  # Deep Blue (Mid)
        (25, 10, 45)   # Muted Violet (Bottom)
    ]
    for i, col in enumerate(colors):
        grad_surf.set_at((0, i), col)
    pygame.transform.smoothscale(grad_surf, (width, height), surface)

    # 2. Dense, non-tiling starfield with slow parallax drift
    for i in range(500):
        seed = i * 12345.67
        speed = 3.0 + (i % 8) * 0.8
        px = int((seed + t * speed) % width)
        py = int((seed * 0.618 + math.sin(i + t * 0.2) * 8) % height)
        
        twinkle = 0.5 + 0.5 * math.sin(t * (1.0 + (i % 5) * 0.2) + i)
        if i % 12 == 0: col = (255, 240, 210) # Yellowish
        elif i % 5 == 0: col = (180, 200, 255) # Blueish
        elif i % 5 == 1: col = (220, 180, 255) # Purplish
        else: col = (235, 240, 255) # Whiteish
        
        alpha = int(40 + 75 * twinkle)
        pygame.draw.circle(surface, (*col, alpha), (px, py), 1)
        
        if i % 30 == 0:
            pygame.draw.circle(surface, (*col, alpha + 30), (px, py), 2)

def draw_instructions(surface, fonts):
    """
    Vẽ màn hình hướng dẫn cách chơi.

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        fonts (dict): Các font chữ.

    Returns:
        dict: Ánh xạ tên nút tới vị trí rect của nút.
    """
    draw_background(surface)
    sw, sh = surface.get_size()
    box = pygame.Rect(sw * 0.1, sh * 0.1, sw * 0.8, sh * 0.8)
    draw_round_rect(surface, box, PANEL_BG, (110, 96, 128), radius=30, width=2)
    
    draw_text(surface, "How to Play", fonts['display'], WHITE, (box.x + 40, box.y + 30))
    
    lines = [
        "1. Objective: Collect keys and open matching chests for points.",
        "2. P1 Controls: WASD to move.",
        "3. P2 Controls: Arrow keys to move.",
        "4. Bot Control: Toggle 'Autoplay' via button, or 'SPACE' to step move.",
        "5. Keys: Larger keys are further away and worth more points.",
        "6. Chests: You must hold the matching colored key to open a chest.",
        "7. Items: Pick up items like 'Freeze' to hinder your opponent.",
    ]
    
    for i, line in enumerate(lines):
        draw_text(surface, line, fonts['normal'], WHITE, (box.x + 45, box.y + 100 + i * 40))
    
    btn_w = 200
    back_rect = pygame.Rect(box.centerx - btn_w // 2, box.bottom - 70, btn_w, 40)
    draw_button(surface, back_rect, "Back to Menu", fonts, fill=(84, 61, 114), text_color=WHITE)
    return {"back": back_rect}

def draw_menu(surface, fonts, map_options, selected_map_index, step_options, selected_step_index, 
              player_type_options, selected_player_type_indices, 
              selected_num_colors, selected_num_sizes):
    """
    Vẽ màn hình menu chính với tất cả các tùy chọn cấu hình game.

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        fonts (dict): Các font chữ.
        map_options (list): Danh sách các kích thước bản đồ.
        selected_map_index (int): Chỉ mục bản đồ đang chọn.
        step_options (list): Các tùy chọn số lượt đi.
        selected_step_index (int): Chỉ mục số lượt đi đang chọn.
        player_type_options (list): Các loại người chơi (Human/AI).
        selected_player_type_indices (list): Danh sách chỉ mục loại người chơi cho P1 và P2.
        selected_num_colors (int): Số lượng màu chìa khóa.
        selected_num_sizes (int): Số lượng kích cỡ chìa khóa.

    Returns:
        dict: Ánh xạ tên nút tới vị trí rect của nút.
    """
    draw_background(surface)
    surface_w, surface_h = surface.get_size()
    box_margin_x = max(36, int(surface_w * 0.065))
    box_margin_y = max(26, int(surface_h * 0.045))
    box = pygame.Rect(box_margin_x, box_margin_y, surface_w - box_margin_x * 2, surface_h - box_margin_y * 2)
    draw_round_rect(surface, box, PANEL_BG, (110, 96, 128), radius=30, width=2)

    title_x = box.x + 30
    draw_text(surface, 'Treasure Hunt', fonts['display'], WHITE, (title_x, box.y + 25))

    buttons = {}
    inner_x = box.x + 22
    inner_w = box.w - 44
    card_gap = 6
    card_h = 74
    y = box.y + 80
    
    # 6 settings cards
    cards = []
    for _ in range(6):
        card = pygame.Rect(inner_x, y, inner_w, card_h)
        draw_round_rect(surface, card, CARD_BG, (92, 82, 111), radius=16)
        cards.append(card)
        y += card_h + card_gap

    def option_button_row(card, title, options, selected_index, prefix, subtitle_text=''):
        draw_text(surface, title, fonts['small'], WHITE, (card.x + 20, card.y + 8))
        if subtitle_text:
            draw_text(surface, fit_text(fonts['tiny'], subtitle_text, card.w - 40), fonts['tiny'], TEXT_MUTED, (card.x + 20, card.y + 24))
        row_y = card.y + 36
        gap = 10
        count = len(options)
        button_w = (card.w - 40 - gap * (count - 1)) // count
        for idx, label in enumerate(options):
            rect = pygame.Rect(card.x + 20 + idx * (button_w + gap), row_y, button_w, 28)
            # Support both index-based and value-based selection
            if isinstance(options[0], int):
                selected = options[idx] == selected_index
            else:
                selected = idx == selected_index
                
            fill = (84, 61, 114) if selected else CARD_HIGHLIGHT
            border = ACCENT_DARK if selected else (92, 82, 111)
            text_color = WHITE if selected else TEXT_MUTED
            buttons[f'{prefix}_{idx}'] = draw_button(surface, rect, str(label), fonts, fill=fill, border=border, text_color=text_color)

    option_button_row(cards[0], 'Step Count', [opt['label'].replace(' Turns', '') for opt in step_options], selected_step_index, 'steps')
    option_button_row(cards[1], 'Map Size', [opt['label'] for opt in map_options], selected_map_index, 'size')
    option_button_row(cards[2], 'Player 1 Mode', player_type_options, selected_player_type_indices[0], 'p1')
    option_button_row(cards[3], 'Player 2 Mode', player_type_options, selected_player_type_indices[1], 'p2')
    option_button_row(cards[4], 'Key Colors', [1, 2, 3, 4, 5, 6], selected_num_colors, 'colors')
    option_button_row(cards[5], 'Key Sizes (Variety)', [1, 2, 3], selected_num_sizes, 'ksizes')

    btn_w = 200
    instr_rect = pygame.Rect(box.centerx - btn_w - 10, box.bottom - 55, btn_w, 40)
    buttons['instructions'] = draw_button(surface, instr_rect, 'Instructions', fonts, fill=CARD_HIGHLIGHT, border=PANEL_BORDER, text_color=WHITE)
    
    start_rect = pygame.Rect(box.centerx + 10, box.bottom - 55, btn_w, 40)
    buttons['start'] = draw_button(surface, start_rect, 'Start Game', fonts, fill=(46, 79, 58), border=SUCCESS, text_color=WHITE)
    
    return buttons


def _color_label(color_id):
    """Hàm nội bộ lấy tên màu dựa trên ID."""
    return KEY_COLOR_LOOKUP.get(color_id, {"name": "Unknown"})["name"]


def _effect_label(character):
    """Hàm nội bộ trả về chuỗi mô tả hiệu ứng hiện tại của nhân vật."""
    if character.is_frozen():
        return f"Frozen ({character.freeze_turns})"
    return "None"


def _turn_status_text(game):
    """Hàm nội bộ trả về thông tin trạng thái lượt đi và người chơi."""
    turns_left = game.get_turns_left()
    if game.game_over:
        return f"Finished · {turns_left} turns left"
    
    from .entities import Player
    is_bot_game = all(not isinstance(c, Player) for c in game.characters)

    status = ""
    if is_bot_game:
        status = "Bot battle"
        if not game.autoplay:
            status += " (PAUSED)"
    else:
        pieces = []
        for character in game.characters:
            if isinstance(character, Player):
                ready = game.pending_human_moves.get(character.control_index) is not None
                pieces.append(f"{character.name} {'Ready' if ready else 'Wait'}")
        status = " | ".join(pieces)
    
    return f"Turns: {turns_left} | {status}"


def _draw_icon(surface, rect, icon, color):
    """Hàm nội bộ vẽ các biểu tượng đồ họa (menu, map, reset, autoplay)."""
    cx, cy = rect.center
    if icon == 'menu':
        roof = [(cx, rect.y + 10), (rect.x + 10, rect.y + 21), (rect.right - 10, rect.y + 21)]
        pygame.draw.polygon(surface, color, roof, 3)
        pygame.draw.rect(surface, color, (cx - 10, rect.y + 21, 20, 14), 3, border_radius=2)
        pygame.draw.rect(surface, color, (cx - 3, rect.y + 27, 6, 8), 2, border_radius=1)
    elif icon == 'new_map':
        pygame.draw.line(surface, color, (cx, rect.y + 10), (cx, rect.bottom - 10), 4)
        pygame.draw.line(surface, color, (rect.x + 10, cy), (rect.right - 10, cy), 4)
    elif icon == 'reset':
        arc_rect = pygame.Rect(rect.x + 8, rect.y + 8, rect.w - 16, rect.h - 16)
        pygame.draw.arc(surface, color, arc_rect, 0.7, 5.4, 4)
        arrow = [(rect.x + 14, cy - 9), (rect.x + 9, cy - 1), (rect.x + 19, cy)]
        pygame.draw.polygon(surface, color, arrow)
    elif icon == 'autoplay':
        # Draw a play/pause combo icon
        # Play triangle
        tri = [(cx - 5, cy - 8), (cx - 5, cy + 8), (cx + 7, cy)]
        pygame.draw.polygon(surface, color, tri)
        # Small indicator for 'auto'
        pygame.draw.circle(surface, color, (cx + 8, cy + 8), 3)


def draw_icon_button(surface, rect, icon, *, active=False):
    """
    Vẽ một nút bấm hình vuông nhỏ chứa biểu tượng.

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        rect (pygame.Rect): Vùng nút bấm.
        icon (str): Tên biểu tượng cần vẽ.
        active (bool): Trạng thái nút (đang bật hay tắt).

    Returns:
        pygame.Rect: Rect của nút.
    """
    fill = (41, 47, 63, 220) if not active else (64, 128, 80, 240) # Greener when active
    draw_round_rect(surface, rect, fill, (112, 96, 138) if not active else SUCCESS, radius=14, width=2)
    _draw_icon(surface, rect, icon, (235, 232, 225))
    return rect


def draw_player_card(surface, fonts, rect, character):
    """
    Vẽ thẻ thông tin người chơi (tên, điểm, chìa khóa, trạng thái).

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        fonts (dict): Các font chữ.
        rect (pygame.Rect): Vùng thẻ thông tin.
        character (Character): Nhân vật cần hiển thị thông tin.
    """
    shadow = rect.move(4, 6)
    draw_round_rect(surface, shadow, (0, 0, 0, 78), None, radius=18)
    draw_round_rect(surface, rect, PANEL_BG, (110, 96, 128), radius=18, width=2)
    pygame.draw.rect(surface, character.color, (rect.x + 8, rect.y + 10, 8, rect.h - 20), border_radius=5)

    left = rect.x + 24
    draw_text(surface, fit_text(fonts['normal'], character.name, rect.w - 34), fonts['normal'], WHITE, (left, rect.y + 10))
    draw_text(surface, getattr(character, 'ai_label', 'Human'), fonts['tiny'], TEXT_MUTED, (left, rect.y + 32))

    score_img = fonts['title'].render(str(character.score), True, WHITE)
    surface.blit(score_img, (left, rect.y + 54))
    draw_text(surface, 'Score', fonts['tiny'], TEXT_SOFT, (left, rect.y + 82))

    draw_text(surface, f"Opened: {character.chests_opened}", fonts['small'], TEXT_MUTED, (left, rect.y + 104))
    eff_col = DANGER if character.is_frozen() else TEXT_MUTED
    draw_text(surface, f"Effect: {_effect_label(character)}", fonts['small'], eff_col, (left, rect.y + 124))

    if character.held_key_id is not None:
        color_name = _color_label(character.held_key_id)
        draw_text(surface, fit_text(fonts['small'], f"Key: {color_name} {character.held_key_size}", rect.w - 36), fonts['small'], WHITE, (left, rect.y + 146))
        draw_text(surface, f"+{character.held_key_score}", fonts['small'], ACCENT_DARK, (left, rect.y + 166))
    else:
        draw_text(surface, 'Key: None', fonts['small'], WHITE, (left, rect.y + 146))

    if hasattr(character, 'control_label'):
        badge = pygame.Rect(rect.right - 68, rect.y + 12, 52, 20)
        draw_round_rect(surface, badge, CARD_HIGHLIGHT, (112, 96, 138), radius=10, width=1)
        draw_text(surface, fit_text(fonts['tiny'], character.control_label(), 42), fonts['tiny'], WHITE, (badge.x + 6, badge.y + 4))


def draw_side_panel(surface, fonts, game):
    """
    Vẽ toàn bộ panel giao diện khi đang trong trận đấu (thông tin cấp độ, người chơi, các nút chức năng).

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        fonts (dict): Các font chữ.
        game (Game): Đối tượng game chính để lấy dữ liệu.

    Returns:
        dict: Ánh xạ tên nút tới vị trí rect của nút.
    """
    buttons = {}
    board_rect = game.get_board_rect()

    # compact control icons in top-right corner
    btn_size = 40
    top_y = 16
    # 4 buttons now: menu, new_map, reset, autoplay
    right_x = surface.get_width() - (btn_size * 4 + 14 * 3 + 18)
    for i, (key, icon) in enumerate((('menu', 'menu'), ('new_map', 'new_map'), ('reset', 'reset'), ('autoplay', 'autoplay'))):
        rect = pygame.Rect(right_x + i * (btn_size + 14), top_y, btn_size, btn_size)
        active = (key == 'autoplay' and game.autoplay)
        buttons[key] = draw_icon_button(surface, rect, icon, active=active)

    pill_w = min(460, board_rect.w + 110)
    pill = pygame.Rect(board_rect.centerx - pill_w // 2, 14, pill_w, 46)
    draw_round_rect(surface, pill, (18, 22, 31, 226), (100, 87, 123), radius=22, width=2)
    draw_text(surface, fit_text(fonts['title'], game.level_name, pill_w - 170), fonts['title'], ACCENT_DARK, (pill.x + 18, pill.y + 10))
    draw_text(surface, fit_text(fonts['tiny'], _turn_status_text(game), 130), fonts['tiny'], WHITE, (pill.right - 136, pill.y + 16))

    side_margin = 14
    side_gap = 14
    side_w = max(126, min(154, board_rect.x - side_margin - side_gap))
    card_h = 196
    top_cards_y = board_rect.y + max(18, board_rect.h // 2 - card_h // 2)
    left_rect = pygame.Rect(side_margin, top_cards_y, side_w, card_h)
    right_rect = pygame.Rect(surface.get_width() - side_margin - side_w, top_cards_y, side_w, card_h)
    if len(game.characters) >= 1:
        draw_player_card(surface, fonts, left_rect, game.characters[0])
    if len(game.characters) >= 2:
        draw_player_card(surface, fonts, right_rect, game.characters[1])
    return buttons


def draw_legend(surface, fonts, game):
    """
    Vẽ phần chú giải các ký hiệu trên bản đồ ở ngay trên bàn cờ.

    Args:
        surface (pygame.Surface): Bề mặt vẽ.
        fonts (dict): Các font chữ.
        game (Game): Đối tượng game.
    """
    board_rect = game.get_board_rect()
    text = '# wall  ·  . floor  ·  glowing keys/chests match by color  ·  purple snowflake = freeze'
    draw_text(surface, fit_text(fonts['small'], text, board_rect.w), fonts['small'], WHITE, (board_rect.x, board_rect.y - 26))

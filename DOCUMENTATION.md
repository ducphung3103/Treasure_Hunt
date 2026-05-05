# Tài liệu kỹ thuật dự án Treasure Hunt

Tài liệu này tổng hợp toàn bộ docstring của các hàm, lớp và phương thức trong dự án.

---

## 1. File: `main.py`
Điểm khởi đầu của ứng dụng Treasure Hunt. Khởi tạo đối tượng Game và bắt đầu vòng lặp trò chơi.

---

## 2. Module: `treasure_hunt.game` (File: `treasure_hunt/game.py`)
Lớp điều khiển chính của trò chơi.

- **Class `Game`**: Lớp điều khiển chính. Quản lý trạng thái game, vòng lặp chính, xử lý sự kiện và vẽ giao diện.
    - `__init__`: Khởi tạo Pygame, cửa sổ hiển thị và các tài nguyên cơ bản.
    - `current_map_size`: (Property) Trả về cấu hình kích thước bản đồ hiện tại.
    - `current_step_option`: (Property) Trả về cấu hình giới hạn số lượt chơi hiện tại.
    - `player_type(index)`: Lấy kiểu người chơi (Human/Easy/Medium/Hard).
    - `mode_label()`: Trả về chuỗi mô tả chế độ chơi hiện tại.
    - `update_viewport()`: Cập nhật kích thước viewport khi đổi kích thước cửa sổ.
    - `to_virtual_pos(mouse_pos)`: Chuyển đổi tọa độ chuột sang tọa độ không gian ảo 1080x720.
    - `update_board_layout()`: Tính toán vị trí gốc của bàn cờ để căn giữa.
    - `start_new_game()`: Khởi động màn chơi mới với seed ngẫu nhiên.
    - `reset()`: Khởi tạo lại dữ liệu trận đấu dựa trên cấu hình hiện tại.
    - `execute_turn()`: Thực hiện một lượt chơi đầy đủ (xử lý di chuyển, va chạm, tương tác).
    - `resolve_substep(...)`: Giải quyết các bước nhỏ trong một lượt đi.
    - `handle_character_interactions(...)`: Xử lý khi nhân vật đứng trên ô chìa khóa, rương hoặc vật phẩm.
    - `end_game()`: Kết thúc trò chơi và xác định người thắng cuộc.

---

## 3. Module: `treasure_hunt.entities` (File: `treasure_hunt/entities.py`)
Định nghĩa các nhân vật trong game.

- **Class `Character`**: Lớp cơ sở cho Người chơi và Bot.
    - `can_enter(x, y, ...)`: Kiểm tra xem nhân vật có thể đi vào ô mục tiêu không.
    - `apply_item(item_type, ...)`: Áp dụng hiệu ứng vật phẩm (ví dụ: freeze).
- **Class `Player`**: Đại diện cho người chơi con người (điều khiển bằng bàn phím).
    - `direction_from_key(key)`: Chuyển phím nhấn thành hướng di chuyển.
- **Class `Bot`**: Đại diện cho người chơi máy với các độ khó Easy, Medium, Hard.
    - `_best_scored_path(...)`: Thuật toán tìm đường thông minh dựa trên trọng số điểm.
    - `choose_direction(game)`: Quyết định hướng đi tiếp theo dựa trên độ khó.

---

## 4. Module: `treasure_hunt.map_data` (File: `treasure_hunt/map_data.py`)
Xử lý việc sinh bản đồ đối xứng.

- `_make_symmetric_grid(...)`: Tạo lưới bản đồ đối xứng trái-phải.
- `_is_connected(...)`: Kiểm tra tính liên thông của bản đồ (đảm bảo đi được mọi nơi).
- `generate_level(...)`: Hàm chính tạo level hoàn chỉnh (lưới, chìa khóa, rương).

---

## 5. Module: `treasure_hunt.pathfinding` (File: `treasure_hunt/pathfinding.py`)
Các thuật toán tìm đường.

- `bfs_shortest_path(...)`: Tìm đường đi ngắn nhất từ A đến B bằng thuật toán BFS.
- `in_bounds(grid, pos)`: Kiểm tra vị trí có nằm trong bản đồ không.
- `passable(grid, pos, ...)`: Kiểm tra ô có thể đi qua không.

---

## 6. Module: `treasure_hunt.ui` (File: `treasure_hunt/ui.py`)
Vẽ giao diện người dùng.

- `draw_background(surface, ...)`: Vẽ nền thiên hà động.
- `draw_menu(...)`: Vẽ màn hình menu chính với các nút cấu hình.
- `draw_side_panel(...)`: Vẽ bảng thông tin người chơi trong trận đấu.
- `draw_round_rect(...)`: Vẽ hình chữ nhật bo góc (hỗ trợ độ trong suốt).

---

## 7. Module: `treasure_hunt.assets` (File: `treasure_hunt/assets.py`)
Quản lý tài nguyên hình ảnh.

- **Class `GameAssets`**: Tạo và cache các sprite.
    - `make_character_sprite(...)`: Vẽ sprite nhân vật từ bảng màu.
    - `get_key_surface(...)`: Lấy hình ảnh chìa khóa (có cache).

---

## 8. Module: `treasure_hunt.items` (File: `treasure_hunt/items.py`)
Quản lý vật phẩm trên bản đồ.

- **Class `ItemSpawner`**: Quản lý việc sinh vật phẩm đối xứng.
    - `spawn_item_pair(...)`: Sinh một cặp vật phẩm ở hai bên bản đồ.

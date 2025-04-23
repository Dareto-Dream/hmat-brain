import pygame
import sys

# === UI Config ===
WIDTH, HEIGHT = 800, 600
BG_COLOR = (15, 15, 15)
GRID_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (100, 255, 100)
PAD_COLOR = (0, 255, 0)
VIA_COLOR = (0, 150, 255)
GHOST_COLOR = (100, 100, 100)
TEXT_COLOR = (255, 255, 255)
CELL_SIZE = 30

def get_45_route_segments(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    abs_dx = abs(dx)
    abs_dy = abs(dy)

    if dx == 0 or dy == 0 or abs_dx == abs_dy:
        return [(start, end)]

    if abs_dx > abs_dy:
        mid = (start[0] + (CELL_SIZE if dx > 0 else -CELL_SIZE) * (abs_dy // CELL_SIZE), end[1])
    else:
        mid = (end[0], start[1] + (CELL_SIZE if dy > 0 else -CELL_SIZE) * (abs_dx // CELL_SIZE))

    return [(start, mid), (mid, end)]

def launch_pcb_maker():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Holomat - PCB Maker")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 24)

    pcb_state = {
        "pads": set(),
        "via_paths": [],
        "via_mode": False,
        "via_start": None,
        "pending_target": None
    }

    menu_rect = pygame.Rect(10, 10, 40, 40)  # ☰ button
    menu_open = False
    menu_items = [
        {"label": "Exit", "action": "EXIT"},
        {"label": "Undo", "action": "UNDO"},
    ]

    running = True
    while running:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        grid_x = (mouse_pos[0] // CELL_SIZE) * CELL_SIZE
        grid_y = (mouse_pos[1] // CELL_SIZE) * CELL_SIZE
        grid_pos = (grid_x, grid_y)

        # === Draw Grid ===
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))

        # === Draw Pads ===
        for pad in pcb_state["pads"]:
            pygame.draw.circle(screen, PAD_COLOR, (pad[0] + CELL_SIZE // 2, pad[1] + CELL_SIZE // 2), 8)

        # === Draw Traces ===
        for start, end in pcb_state["via_paths"]:
            for s, e in get_45_route_segments(start, end):
                s_center = (s[0] + CELL_SIZE // 2, s[1] + CELL_SIZE // 2)
                e_center = (e[0] + CELL_SIZE // 2, e[1] + CELL_SIZE // 2)
                pygame.draw.line(screen, VIA_COLOR, s_center, e_center, 3)
            end_center = (end[0] + CELL_SIZE // 2, end[1] + CELL_SIZE // 2)
            pygame.draw.circle(screen, VIA_COLOR, end_center, 4)

        # === Draw Ghost Segment ===
        if pcb_state["via_mode"] and pcb_state["via_start"] and pcb_state["pending_target"]:
            for s, e in get_45_route_segments(pcb_state["via_start"], pcb_state["pending_target"]):
                s_center = (s[0] + CELL_SIZE // 2, s[1] + CELL_SIZE // 2)
                e_center = (e[0] + CELL_SIZE // 2, e[1] + CELL_SIZE // 2)
                pygame.draw.line(screen, GHOST_COLOR, s_center, e_center, 2)

        # === Hover Highlight Box (snap grid)
        hover_rect = pygame.Rect(grid_x, grid_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, hover_rect, 2)

        # === Draw ☰ Menu Button ===
        pygame.draw.rect(screen, (30, 30, 30), menu_rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, menu_rect, 2)
        bar_y = menu_rect.y + 8
        for _ in range(3):
            pygame.draw.line(screen, TEXT_COLOR, (menu_rect.x + 8, bar_y), (menu_rect.x + 32, bar_y), 3)
            bar_y += 8

        # === Draw Expanded Menu Panel ===
        if menu_open:
            for i, item in enumerate(menu_items):
                item_rect = pygame.Rect(menu_rect.x, menu_rect.bottom + i * 40, 120, 35)
                pygame.draw.rect(screen, (40, 40, 40), item_rect)
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, item_rect, 1)
                label = font.render(item["label"], True, TEXT_COLOR)
                screen.blit(label, label.get_rect(center=item_rect.center))
                item["rect"] = item_rect

        # === Event Handling ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # ☰ Toggle Menu
                if menu_rect.collidepoint(event.pos):
                    menu_open = not menu_open

                # Menu Actions
                elif menu_open:
                    for item in menu_items:
                        if "rect" in item and item["rect"].collidepoint(event.pos):
                            if item["action"] == "EXIT":
                                running = False
                            elif item["action"] == "UNDO" and pcb_state["via_paths"]:
                                pcb_state["via_paths"].pop()
                            break

                # === Routing Logic ===
                elif grid_pos in pcb_state["pads"]:
                    if not pcb_state["via_mode"]:
                        pcb_state["via_mode"] = True
                        pcb_state["via_start"] = grid_pos
                        pcb_state["pending_target"] = None
                    else:
                        if pcb_state["via_start"] != grid_pos:
                            pcb_state["via_paths"].append((pcb_state["via_start"], grid_pos))
                        pcb_state["via_mode"] = False
                        pcb_state["via_start"] = None
                        pcb_state["pending_target"] = None
                else:
                    if pcb_state["via_mode"] and pcb_state["via_start"]:
                        if pcb_state["pending_target"] == grid_pos:
                            pcb_state["via_paths"].append((pcb_state["via_start"], grid_pos))
                            pcb_state["via_start"] = grid_pos
                            pcb_state["pending_target"] = None
                        else:
                            pcb_state["pending_target"] = grid_pos
                    else:
                        pcb_state["pads"].add(grid_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    launch_pcb_maker()
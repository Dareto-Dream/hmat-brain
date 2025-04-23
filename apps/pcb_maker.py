import pygame
import sys

# === UI Config ===
WIDTH, HEIGHT = 800, 600
BG_COLOR = (15, 15, 15)
GRID_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (100, 255, 100)
PAD_COLOR = (0, 255, 0)
VIA_COLOR = (0, 150, 255)
CELL_SIZE = 30

def launch_pcb_maker():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Holomat - PCB Maker")
    clock = pygame.time.Clock()

    pcb_state = {
        "pads": set(),        # {(x, y)}
        "via_paths": [],      # [(start, end), ...]
        "via_mode": False,    # True if we're drawing a via
        "via_start": None
    }

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

        # === Draw Vias ===
        for start, end in pcb_state["via_paths"]:
            start_center = (start[0] + CELL_SIZE // 2, start[1] + CELL_SIZE // 2)
            end_center = (end[0] + CELL_SIZE // 2, end[1] + CELL_SIZE // 2)
            pygame.draw.line(screen, VIA_COLOR, start_center, end_center, 3)
            pygame.draw.circle(screen, VIA_COLOR, end_center, 4)

        # === Hover Highlight ===
        hover_rect = pygame.Rect(grid_x, grid_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, hover_rect, 2)

        # === Tap Event Logic ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # === Clicked Pad ===
                if grid_pos in pcb_state["pads"]:
                    if not pcb_state["via_mode"]:
                        pcb_state["via_mode"] = True
                        pcb_state["via_start"] = grid_pos
                    else:
                        if pcb_state["via_start"] != grid_pos:
                            pcb_state["via_paths"].append((pcb_state["via_start"], grid_pos))
                        pcb_state["via_mode"] = False
                        pcb_state["via_start"] = None

                # === Clicked Empty Cell ===
                else:
                    if pcb_state["via_mode"] and pcb_state["via_start"]:
                        pcb_state["via_paths"].append((pcb_state["via_start"], grid_pos))
                        pcb_state["via_start"] = grid_pos  # 🔧 continue from this new point
                    else:
                        pcb_state["pads"].add(grid_pos)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    launch_pcb_maker()
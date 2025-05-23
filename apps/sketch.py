import math
import sys

import pygame


def launch_sketch(state):
    # === Constants ===
    WIDTH, HEIGHT = 1000, 600
    TOOLBAR_WIDTH = 200
    GRID_SIZE = 20
    BG_COLOR = (30, 30, 30)
    GRID_COLOR = (50, 50, 50)
    DRAW_COLOR = (0, 255, 0)
    CURSOR_COLOR = (255, 255, 0)
    FONT_COLOR = (200, 200, 200)
    TOOLBAR_COLOR = (40, 40, 40)
    TOOL_ACTIVE_COLOR = (60, 60, 60)
    BUTTON_HEIGHT = 40

    # === State ===
    lines = state["lines"]
    rects = state["rects"]
    circles = state["circles"]
    current_tool = "line"
    click_stage = 0
    point_a = None

    # === Setup ===
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Holomat Sketch")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    tool_options = ["line", "rect", "circle", "clear", "back"]

    def draw_grid():
        for x in range(TOOLBAR_WIDTH, WIDTH, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (TOOLBAR_WIDTH, y), (WIDTH, y))

    def draw_shapes():
        for line in lines:
            pygame.draw.line(screen, DRAW_COLOR, line[0], line[1], 2)
        for rect in rects:
            pygame.draw.rect(screen, DRAW_COLOR, rect, 2)
        for circle in circles:
            pygame.draw.circle(screen, DRAW_COLOR, circle[0], circle[1], 2)

    def draw_cursor(pos):
        x, y = pos
        label = font.render(f"({x}, {y})", True, FONT_COLOR)
        screen.blit(label, (TOOLBAR_WIDTH + 10, HEIGHT - 30))
        pygame.draw.circle(screen, CURSOR_COLOR, pos, 3)

    def draw_toolbar():
        for i, tool in enumerate(tool_options):
            rect = pygame.Rect(0, i * BUTTON_HEIGHT, TOOLBAR_WIDTH, BUTTON_HEIGHT)
            color = TOOL_ACTIVE_COLOR if tool == current_tool else TOOLBAR_COLOR
            pygame.draw.rect(screen, color, rect)
            label = font.render(tool.capitalize(), True, FONT_COLOR)
            screen.blit(label, (10, i * BUTTON_HEIGHT + 10))

    def handle_toolbar_click(pos):
        nonlocal current_tool
        x, y = pos
        if x >= TOOLBAR_WIDTH:
            return False
        index = y // BUTTON_HEIGHT
        if index < len(tool_options):
            selected = tool_options[index]
            if selected == "clear":
                lines.clear()
                rects.clear()
                circles.clear()
            elif selected == "back":
                return "BACK"
            else:
                current_tool = selected
            return True
        return False

    # === Main Loop ===
    running = True
    while running:
        screen.fill(BG_COLOR)
        draw_toolbar()
        draw_grid()
        draw_shapes()

        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos[0] > TOOLBAR_WIDTH:
            draw_cursor(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                action = handle_toolbar_click(event.pos)
                if action == "BACK":
                    return
                if action:
                    continue

                if mouse_pos[0] < TOOLBAR_WIDTH:
                    continue

                if click_stage == 0:
                    point_a = mouse_pos
                    click_stage = 1
                else:
                    point_b = mouse_pos
                    if current_tool == "line":
                        lines.append((point_a, point_b))
                    elif current_tool == "rect":
                        x1, y1 = point_a
                        x2, y2 = point_b
                        rect = pygame.Rect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
                        rects.append(rect)
                    elif current_tool == "circle":
                        dx = point_b[0] - point_a[0]
                        dy = point_b[1] - point_a[1]
                        radius = int(math.hypot(dx, dy))
                        circles.append((point_a, radius))
                    click_stage = 0
                    point_a = None

        pygame.display.flip()
        clock.tick(60)

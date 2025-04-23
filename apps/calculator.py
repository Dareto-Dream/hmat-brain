# apps/calculator.py

import pygame
import sys
from sympy import sympify

# === UI Setup ===
WIDTH, HEIGHT = 800, 600
BG_COLOR = (10, 10, 10)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (30, 30, 30)
OUTLINE_COLOR = (100, 100, 100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Holomat - Calculator")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 24)


def draw_button(rect, label, selected=False):
    color = (60, 60, 60) if selected else BTN_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, OUTLINE_COLOR, rect, 2)
    text = small_font.render(label, True, TEXT_COLOR)
    screen.blit(text, text.get_rect(center=rect.center))


def safe_eval(expr):
    try:
        return str(sympify(expr).evalf())
    except Exception:
        return "Error"


def launch_calculator_app():
    mode = "CALC"
    calc_tab = pygame.Rect(100, 20, 150, 40)
    convert_tab = pygame.Rect(300, 20, 150, 40)
    graph_tab = pygame.Rect(500, 20, 150, 40)
    back_button = pygame.Rect(20, 20, 40, 40)

    while True:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()
        events = pygame.event.get()

        draw_button(back_button, "<")
        draw_button(calc_tab, "CALC", selected=(mode == "CALC"))
        draw_button(convert_tab, "CONVERT", selected=(mode == "CONVERT"))
        draw_button(graph_tab, "GRAPH", selected=(mode == "GRAPH"))

        if mode == "CALC":
            render_calculator_tab(screen, font, small_font, mouse_pos, events)
        elif mode == "CONVERT":
            render_converter_tab(screen, font, small_font, mouse_pos, events)
        elif mode == "GRAPH":
            placeholder = font.render("Graphing Coming Soon...", True, TEXT_COLOR)
            screen.blit(placeholder, placeholder.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        for event in events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(mouse_pos):
                    return
                if calc_tab.collidepoint(mouse_pos):
                    mode = "CALC"
                elif convert_tab.collidepoint(mouse_pos):
                    mode = "CONVERT"
                elif graph_tab.collidepoint(mouse_pos):
                    mode = "GRAPH"

        pygame.display.flip()
        clock.tick(30)


def render_calculator_tab(surface, font, small_font, mouse_pos, events):
    if "calc_state" not in render_calculator_tab.__dict__:
        render_calculator_tab.calc_state = {
            "input_expr": "",
            "result": ""
        }

    state = render_calculator_tab.calc_state

    # Calculator buttons
    layout = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "=", "+"],
        ["C", "←", "(", ")"]
    ]

    buttons = []
    for row_idx, row in enumerate(layout):
        for col_idx, label in enumerate(row):
            x = 150 + col_idx * 100
            y = 180 + row_idx * 70
            rect = pygame.Rect(x, y, 80, 50)
            buttons.append((rect, label))
            pygame.draw.rect(surface, BTN_COLOR, rect)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect, 2)
            txt = small_font.render(label, True, TEXT_COLOR)
            surface.blit(txt, txt.get_rect(center=rect.center))

    # Display
    input_surface = font.render(state["input_expr"], True, TEXT_COLOR)
    result_surface = small_font.render(state["result"], True, TEXT_COLOR)
    surface.blit(input_surface, (100, 80))
    surface.blit(result_surface, (100, 120))

    # Events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            for rect, label in buttons:
                if rect.collidepoint(mouse_pos):
                    if label == "=":
                        state["result"] = safe_eval(state["input_expr"])
                    elif label == "C":
                        state["input_expr"] = ""
                        state["result"] = ""
                    elif label == "←":
                        state["input_expr"] = state["input_expr"][:-1]
                    elif label == "(":
                        if state["input_expr"] and (state["input_expr"][-1].isdigit() or state["input_expr"][-1] == ")"):
                            state["input_expr"] += "*("
                        else:
                            state["input_expr"] += "("
                    else:
                        state["input_expr"] += label

def render_converter_tab(surface, font, small_font, mouse_pos, events):
    WIDTH, HEIGHT = 800, 600

    # === Persistent State Setup ===
    if "convert_state" not in render_converter_tab.__dict__:
        render_converter_tab.convert_state = {
            "input_value": "1.0",
            "from_unit": "mm",
            "to_unit": "cm",
            "conversion_type": "Length",
            "active_input": False,
            "from_open": False,
            "to_open": False
        }

    if "numpad_buttons" not in render_converter_tab.__dict__:
        numpad_layout = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            ["0", ".", "←"],
            ["C"]
        ]
        render_converter_tab.numpad_buttons = []
        pad_start_x = (WIDTH - (3 * 60)) // 2
        for row_idx, row in enumerate(numpad_layout):
            for col_idx, label in enumerate(row):
                x = pad_start_x + col_idx * 60
                y = 300 + row_idx * 60
                rect = pygame.Rect(x, y, 50, 50)
                render_converter_tab.numpad_buttons.append((rect, label))

    if "conversion_type_open" not in render_converter_tab.__dict__:
        render_converter_tab.conversion_type_open = False

    state = render_converter_tab.convert_state
    numpad_buttons = render_converter_tab.numpad_buttons
    conversion_type_open = render_converter_tab.conversion_type_open
    conversion_type = state.get("conversion_type", "Length")

    # === Unit Categories ===
    unit_categories = {
        "Length": {
            "mm": 1,
            "cm": 10,
            "m": 1000,
            "in": 25.4,
            "ft": 304.8,
            "yd": 914.4
        },
        "Mass": {
            "g": 1,
            "kg": 1000,
            "mg": 0.001,
            "lb": 453.592,
            "oz": 28.3495
        },
        "Angle": {
            "deg": 1,
            "rad": 57.2958,
            "grad": 0.9
        }
    }

    unit_list = list(unit_categories[conversion_type].keys())

    # === Layout Rects ===
    type_rect = pygame.Rect((WIDTH - 300) // 2, 80, 300, 40)
    input_rect = pygame.Rect(100, 150, 200, 50)
    result_rect = pygame.Rect(500, 150, 200, 50)
    from_unit_rect = pygame.Rect(100, 220, 200, 40)
    to_unit_rect = pygame.Rect(500, 220, 200, 40)

    # === Event Handling ===
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if type_rect.collidepoint(mouse_pos):
                render_converter_tab.conversion_type_open = not conversion_type_open

            elif conversion_type_open:
                for i, category in enumerate(unit_categories.keys()):
                    rect = pygame.Rect(type_rect.x, type_rect.y + (i + 1) * 40, 300, 40)
                    if rect.collidepoint(mouse_pos):
                        state["conversion_type"] = category
                        state["from_unit"] = list(unit_categories[category].keys())[0]
                        state["to_unit"] = list(unit_categories[category].keys())[1]
                        render_converter_tab.conversion_type_open = False

            elif from_unit_rect.collidepoint(mouse_pos):
                state["from_open"] = not state["from_open"]
                state["to_open"] = False
            elif to_unit_rect.collidepoint(mouse_pos):
                state["to_open"] = not state["to_open"]
                state["from_open"] = False
            elif input_rect.collidepoint(mouse_pos):
                state["active_input"] = True
                state["from_open"] = False
                state["to_open"] = False
            else:
                state["active_input"] = False
                state["from_open"] = False
                state["to_open"] = False
                render_converter_tab.conversion_type_open = False

            # Unit selections
            if state["from_open"]:
                for i, unit in enumerate(unit_list):
                    rect = pygame.Rect(from_unit_rect.x, from_unit_rect.y + (i + 1) * 40, 200, 40)
                    if rect.collidepoint(mouse_pos):
                        state["from_unit"] = unit
                        state["from_open"] = False

            if state["to_open"]:
                for i, unit in enumerate(unit_list):
                    rect = pygame.Rect(to_unit_rect.x, to_unit_rect.y + (i + 1) * 40, 200, 40)
                    if rect.collidepoint(mouse_pos):
                        state["to_unit"] = unit
                        state["to_open"] = False

            # Numpad interaction
            for rect, label in numpad_buttons:
                if rect.collidepoint(mouse_pos):
                    if label == "←":
                        state["input_value"] = state["input_value"][:-1]
                    elif label == "C":
                        state["input_value"] = ""
                    else:
                        state["input_value"] += label

    # === Conversion Logic ===
    try:
        input_val = float(state["input_value"])
        units = unit_categories[conversion_type]
        base_val = input_val * units[state["from_unit"]]
        result_val = base_val / units[state["to_unit"]]
        result_str = f"{result_val:.4g}"
    except:
        result_str = "Error"

    # === Draw Top Dropdown ===
    pygame.draw.rect(surface, BTN_COLOR, type_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, type_rect, 2)
    type_label = small_font.render(f"{conversion_type} ▼", True, TEXT_COLOR)
    surface.blit(type_label, type_label.get_rect(center=type_rect.center))

    if conversion_type_open:
        for i, category in enumerate(unit_categories.keys()):
            rect = pygame.Rect(type_rect.x, type_rect.y + (i + 1) * 40, 300, 40)
            pygame.draw.rect(surface, BTN_COLOR, rect)
            pygame.draw.rect(surface, OUTLINE_COLOR, rect, 2)
            cat_text = small_font.render(category, True, TEXT_COLOR)
            surface.blit(cat_text, cat_text.get_rect(center=rect.center))

    # === Draw Input / Output ===
    pygame.draw.rect(surface, BTN_COLOR, input_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, input_rect, 2)
    input_text = font.render(state["input_value"], True, TEXT_COLOR)
    surface.blit(input_text, input_text.get_rect(center=input_rect.center))

    pygame.draw.rect(surface, BTN_COLOR, result_rect)
    pygame.draw.rect(surface, OUTLINE_COLOR, result_rect, 2)
    result_text = font.render(result_str, True, TEXT_COLOR)
    surface.blit(result_text, result_text.get_rect(center=result_rect.center))

    # === Dropdown Renderers ===
    def draw_dropdown(base_rect, selected, open_flag):
        pygame.draw.rect(surface, BTN_COLOR, base_rect)
        pygame.draw.rect(surface, OUTLINE_COLOR, base_rect, 2)
        label = small_font.render(selected, True, TEXT_COLOR)
        surface.blit(label, label.get_rect(center=base_rect.center))

        if open_flag:
            for i, unit in enumerate(unit_list):
                rect = pygame.Rect(base_rect.x, base_rect.y + (i + 1) * 40, 200, 40)
                pygame.draw.rect(surface, BTN_COLOR, rect)
                pygame.draw.rect(surface, OUTLINE_COLOR, rect, 2)
                text = small_font.render(unit, True, TEXT_COLOR)
                surface.blit(text, text.get_rect(center=rect.center))

    draw_dropdown(from_unit_rect, state["from_unit"], state["from_open"])
    draw_dropdown(to_unit_rect, state["to_unit"], state["to_open"])

    # === Equal Sign ===
    eq_label = font.render("=", True, TEXT_COLOR)
    surface.blit(eq_label, eq_label.get_rect(center=(WIDTH // 2, 175)))

    # === Numpad Buttons ===
    for rect, label in numpad_buttons:
        pygame.draw.rect(surface, BTN_COLOR, rect)
        pygame.draw.rect(surface, OUTLINE_COLOR, rect, 2)
        text = small_font.render(label, True, TEXT_COLOR)
        surface.blit(text, text.get_rect(center=rect.center))

if __name__ == "__main__":
    launch_calculator_app()

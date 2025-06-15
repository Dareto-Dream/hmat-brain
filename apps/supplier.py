import pygame
import requests

API_URL = "https://hmat-stocking-production.up.railway.app/barcode"

state = {
    "mode": "subtract",  # or "add"
    "last_code": None,
    "response": None
}

input_buffer = ""  # for accumulating scanner input

def send_to_backend(code, mode):
    try:
        delta = 1 if mode == "add" else -1
        payload = {
            "code": code,
            "delta": delta,
            "client_id": "hmat"
        }
        r = requests.post(API_URL, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            return {"error": f"HTTP {r.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def handle_scanned_code(code):
    state["last_code"] = code
    result = send_to_backend(code, state["mode"])
    if "new_stock" in result:
        state["response"] = f"Stock: {result['new_stock']} | Success"
    else:
        state["response"] = f"Error: {result.get('error', 'Unknown')}"

def render_supply_app(screen, events, font):
    screen.fill((20, 20, 20))

    # Draw Title
    title = font.render("SUPPLY APP", True, (255, 255, 255))
    screen.blit(title, (20, 20))

    # Mode toggle
    subtract_rect = pygame.Rect(20, 70, 100, 40)
    add_rect = pygame.Rect(140, 70, 100, 40)
    pygame.draw.rect(screen, (100, 100, 255) if state["mode"] == "subtract" else (60, 60, 60), subtract_rect)
    pygame.draw.rect(screen, (100, 255, 100) if state["mode"] == "add" else (60, 60, 60), add_rect)
    screen.blit(font.render("Subtract", True, (0, 0, 0)), (25, 80))
    screen.blit(font.render("Add", True, (0, 0, 0)), (170, 80))

    # Last code
    if state["last_code"]:
        screen.blit(font.render(f"LAST SCAN: {state['last_code']}", True, (255, 255, 255)), (20, 140))

    # Response
    if state["response"]:
        screen.blit(font.render(f"RESULT: {state['response']}", True, (200, 255, 200)), (20, 180))

    # Show input buffer for debug
    screen.blit(font.render(f"INPUT: {input_buffer}", True, (150, 150, 150)), (20, 500))

    # Back button
    back_rect = pygame.Rect(20, 240, 80, 40)
    pygame.draw.rect(screen, (100, 100, 100), back_rect)
    screen.blit(font.render("Back", True, (255, 255, 255)), (30, 250))

    # Handle events
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if subtract_rect.collidepoint(mx, my):
                state["mode"] = "subtract"
            elif add_rect.collidepoint(mx, my):
                state["mode"] = "add"
            elif back_rect.collidepoint(mx, my):
                return "back"

    return "supply"

def launch_supplier_app():
    global input_buffer
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Holomat - Supply App")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 28)

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return "EXIT"
            elif event.type == pygame.KEYDOWN:
                char = event.unicode
                if char:
                    input_buffer += char
                    if input_buffer.endswith("\\"):
                        start = input_buffer.find("\\")
                        if start != -1 and start < len(input_buffer) - 1:
                            code = input_buffer[start + 1:-1]
                            handle_scanned_code(code)
                            input_buffer = ""

        result = render_supply_app(screen, events, font)
        if result == "back":
            return "MAIN"

        pygame.display.flip()
        clock.tick(60)

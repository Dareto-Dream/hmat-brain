import pygame
import requests
import time

# === Setup ===
SERVER_URL = 'http://10.0.0.56:5000/touches'  # Pi Zero 2W IP address
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
POLL_INTERVAL = 0.05  # 50 ms = 20 FPS approx

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Holomat Finger Draw Test")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

def fetch_fingers():
    try:
        response = requests.get(SERVER_URL, timeout=0.1)
        return response.json()
    except requests.exceptions.RequestException:
        return []

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    fingers = fetch_fingers()

    # === Draw ===
    screen.fill((0, 0, 0))  # Black background

    for finger in fingers:
        x = int(finger.get('x', 0))
        y = int(finger.get('y', 0))
        # Rescale coordinates to fit our screen if needed
        scaled_x = int(x * SCREEN_WIDTH / 640)
        scaled_y = int(y * SCREEN_HEIGHT / 480)
        pygame.draw.circle(screen, (0, 255, 0), (scaled_x, scaled_y), 10)

    # Draw number of fingers detected
    text = font.render(f"Fingers detected: {len(fingers)}", True, (0, 255, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(20)  # 20 FPS

pygame.quit()

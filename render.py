import pygame
import math
import datetime
import threading
import time
from tools.spotify_api import current_song_string, is_playing


def render_main_screen(state):
    WIDTH, HEIGHT = 800, 600
    CENTER = (WIDTH // 2, HEIGHT // 2)
    SUN_RADIUS = 120
    PLANET_RADIUS = 45
    PLANET_DISTANCE = 200

    BG_COLOR = (0, 0, 0)
    TEXT_COLOR = (255, 255, 255)
    CIRCLE_COLOR = (0, 0, 0)
    OUTLINE_COLOR = (255, 255, 255)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Holomat - Radial UI")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 20)

    state["spotify_display"] = ""
    state["spotify_artist"] = ""

    def update_spotify_status():
        delay = 30
        while True:
            if is_playing():
                info = current_song_string()
                if info and "–" in info:
                    song, artist = info.split("–", 1)
                    state["spotify_display"] = song.strip()
                    state["spotify_artist"] = artist.strip()
                delay = 5
            else:
                state["spotify_display"] = ""
                state["spotify_artist"] = ""
                delay = 30
            time.sleep(delay)

    threading.Thread(target=update_spotify_status, daemon=True).start()

    planets = [
        {"label": "Sketch", "angle": -45, "action": "SKETCH"},
        {"label": "Exit", "angle": 45, "action": "EXIT"},
    ]

    def get_planet_pos(angle_deg):
        rad = math.radians(angle_deg)
        x = CENTER[0] + PLANET_DISTANCE * math.cos(rad)
        y = CENTER[1] + PLANET_DISTANCE * math.sin(rad)
        return (int(x), int(y))

    def draw_circle(pos, radius, text, font):
        pygame.draw.circle(screen, CIRCLE_COLOR, pos, radius)
        pygame.draw.circle(screen, OUTLINE_COLOR, pos, radius, width=2)
        label = font.render(text, True, TEXT_COLOR)
        screen.blit(label, label.get_rect(center=pos))

    def draw_center():
        pygame.draw.circle(screen, CIRCLE_COLOR, CENTER, SUN_RADIUS)
        pygame.draw.circle(screen, OUTLINE_COLOR, CENTER, SUN_RADIUS, width=3)

        if state.get("spotify_display"):
            song_label = big_font.render(state["spotify_display"], True, TEXT_COLOR)
            artist_label = font.render(state["spotify_artist"], True, TEXT_COLOR)
            screen.blit(song_label, song_label.get_rect(center=(CENTER[0], CENTER[1] - 20)))
            screen.blit(artist_label, artist_label.get_rect(center=(CENTER[0], CENTER[1] + 20)))
        else:
            now = datetime.datetime.now()
            time_text = now.strftime("%H:%M:%S")
            time_label = big_font.render(time_text, True, TEXT_COLOR)
            screen.blit(time_label, time_label.get_rect(center=CENTER))

    while True:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        draw_center()

        for planet in planets:
            pos = get_planet_pos(planet["angle"])
            planet["pos"] = pos
            hovered = math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]) < PLANET_RADIUS
            draw_circle(pos, PLANET_RADIUS, planet["label"], small_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for planet in planets:
                    pos = planet["pos"]
                    if math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]) < PLANET_RADIUS:
                        return planet["action"]

        pygame.display.flip()
        clock.tick(60)
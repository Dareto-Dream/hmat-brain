# apps/spotify.py

import pygame
import sys
import time
from tools.spotify_api import *


WIDTH, HEIGHT = 800, 600
BG_COLOR = (10, 10, 10)
TEXT_COLOR = (255, 255, 255)
BTN_COLOR = (30, 30, 30)
OUTLINE_COLOR = (100, 100, 100)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Holomat - Spotify App")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 20)


def draw_button(rect, text, selected=False):
    color = (60, 60, 60) if selected else BTN_COLOR
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, OUTLINE_COLOR, rect, 2)
    label = small_font.render(text, True, TEXT_COLOR)
    screen.blit(label, label.get_rect(center=rect.center))


def launch_spotify_app():
    volume = 50  # default volume
    position_ms = 0
    duration_ms = 1
    track_id = None
    like_rect = pygame.Rect(0, 0, 0, 0)
    last_poll_time = 0
    poll_interval = 5  # seconds
    last_liked_check = 0
    liked_check_interval = 10  # seconds
    title = ""
    artist = ""
    duration_ms = ""
    position_ms = ""
    repeat_state = ""
    shuffle_state = ""
    track_id = ""
    liked = ""
    playing = ""

    while True:
        screen.fill(BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        include_liked = time.time() - last_liked_check > liked_check_interval

        if time.time() - last_poll_time >= poll_interval:
            playback_data = get_playback_bundle(include_liked=include_liked)
            last_poll_time = time.time()
            if include_liked:
                last_liked_check = time.time()

        if playback_data:
            title = playback_data["title"]
            artist = playback_data["artist"]
            duration_ms = playback_data["duration_ms"]
            position_ms = playback_data["position_ms"]
            repeat_state = playback_data["repeat_state"]
            shuffle_state = playback_data["shuffle_state"]
            track_id = playback_data["track_id"]
            liked = playback_data["liked"]
            playing = playback_data["is_playing"]


        if playing:
            track_info = sp.currently_playing()
            if track_info and track_info["item"]:
                duration_ms = track_info["item"]["duration_ms"]
                position_ms = track_info["progress_ms"]

                title_label = font.render(title.strip(), True, TEXT_COLOR)
                artist_label = small_font.render(artist.strip(), True, TEXT_COLOR)
                screen.blit(title_label, title_label.get_rect(center=(WIDTH//2, 100)))
                screen.blit(artist_label, artist_label.get_rect(center=(WIDTH//2, 140)))
                track_id = get_current_track_id()
                liked = is_song_liked(track_id)
                like_symbol = "♥" if liked else "+"
                like_label = small_font.render(like_symbol, True, TEXT_COLOR)
                like_rect = like_label.get_rect(center=(WIDTH // 2, HEIGHT - 150))
                screen.blit(like_label, like_rect)
        else:
            status = font.render("Not Playing", True, TEXT_COLOR)
            screen.blit(status, status.get_rect(center=(WIDTH//2, 120)))

        # === Back Button ===
        back_rect = pygame.Rect(20, 20, 40, 40)
        draw_button(back_rect, "<")

        # === Control Buttons ===
        buttons = [(back_rect, None)]
        labels = ["|<<", "||" if is_playing() else ">", ">>|"]
        actions = [previous_track, pause_playback if is_playing() else resume_playback, skip_track]

        for i, (label, action) in enumerate(zip(labels, actions)):
            rect = pygame.Rect(250 + i*100, 200, 80, 50)
            draw_button(rect, label)
            buttons.append((rect, action))

        # === Seek Bar ===
        seek_x = 150
        seek_width = 500
        pygame.draw.rect(screen, OUTLINE_COLOR, (seek_x, 270, seek_width, 10), 2)
        progress = int((position_ms / duration_ms) * seek_width) if duration_ms else 0
        pygame.draw.rect(screen, TEXT_COLOR, (seek_x, 270, progress, 10))

        elapsed = int(position_ms / 1000)
        total = int(duration_ms / 1000)
        elapsed_text = small_font.render(f"{elapsed//60}:{elapsed%60:02d}", True, TEXT_COLOR)
        total_text = small_font.render(f"{total//60}:{total%60:02d}", True, TEXT_COLOR)
        screen.blit(elapsed_text, (seek_x, 250))
        screen.blit(total_text, (seek_x + seek_width - 50, 250))

        # === Volume Slider ===
        vol_label = small_font.render(f"Volume: {volume}%", True, TEXT_COLOR)
        screen.blit(vol_label, (WIDTH//2 - 60, 320))
        pygame.draw.rect(screen, OUTLINE_COLOR, (250, 350, 300, 10), 2)
        pygame.draw.rect(screen, TEXT_COLOR, (250, 350, volume * 3, 10))

        # === Repeat & Shuffle ===
        repeat_rect = pygame.Rect(200, 400, 100, 40)
        shuffle_rect = pygame.Rect(500, 400, 100, 40)
        draw_button(repeat_rect, f"Repeat ({repeat_state})", selected=repeat_state != "off")
        draw_button(shuffle_rect, f"Shuffle", selected=shuffle_state)

        # === Events ===
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, action in buttons:
                    if rect.collidepoint(mouse_pos):
                        if rect == back_rect:
                            return
                        elif action:
                            action()
                if pygame.Rect(250, 350, 300, 10).collidepoint(mouse_pos):
                    volume = max(0, min(100, int((mouse_pos[0] - 250) / 3)))
                    set_volume(volume)
                if pygame.Rect(seek_x, 270, seek_width, 10).collidepoint(mouse_pos):
                    new_percent = (mouse_pos[0] - seek_x) / seek_width
                    new_position = int(new_percent * duration_ms)
                    sp.seek_track(new_position)
                if repeat_rect.collidepoint(mouse_pos):
                    next_state = {
                        "off": "context",
                        "context": "track",
                        "track": "off"
                    }[repeat_state]
                    sp.repeat(next_state)
                if shuffle_rect.collidepoint(mouse_pos):
                    sp.shuffle(not shuffle_state)
                if like_rect.collidepoint(mouse_pos):
                    if liked:
                        unlike_current_song(track_id)
                    else:
                        like_current_song()

        pygame.display.flip()
        clock.tick(1)


if __name__ == "__main__":
    launch_spotify_app()
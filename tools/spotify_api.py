# spotify_api.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# === Configuration ===
CLIENT_ID = "9cbf9ddfd105464e8668063e925bb745"
CLIENT_SECRET = "6df50b18794242c3985543a3eb3ba093"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# === Spotify Commands ===
def get_current_song():
    current = sp.currently_playing()
    if current and current["is_playing"]:
        return {
            "title": current["item"]["name"],
            "artist": ", ".join([a["name"] for a in current["item"]["artists"]]),
            "album": current["item"]["album"]["name"]
        }
    return None

def pause_playback():
    sp.pause_playback()

def resume_playback():
    sp.start_playback()

def skip_track():
    sp.next_track()

def previous_track():
    sp.previous_track()

def set_volume(percent: int):
    try:
        sp.volume(percent)
    except Exception as e:
        print(f"[!] Volume control failed: {e}")


def play_uri(uri: str):
    sp.start_playback(uris=[uri])

def get_devices():
    return sp.devices()

def transfer_playback(device_id):
    sp.transfer_playback(device_id, force_play=True)

def is_playing():
    playback = sp.current_playback()
    return playback and playback.get("is_playing", False)

# Optional: helper to get pretty song string
def current_song_string():
    song = get_current_song()
    if song:
        return f"{song['title']} – {song['artist']}"
    return "Not playing"

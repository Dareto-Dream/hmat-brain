# spotify_api.py

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# === Configuration ===
CLIENT_ID = "9cbf9ddfd105464e8668063e925bb745"
# CLIENT_ID = "b14770236aff484ab764de2b0cf8cb8c"
CLIENT_SECRET = "6df50b18794242c3985543a3eb3ba093"
# CLIENT_SECRET = "f914dab7bb964da993b93afa86bae818"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = (
    "user-read-playback-state "
    "user-modify-playback-state "
    "user-read-currently-playing "
    "user-library-modify "
    "user-library-read "
    "playlist-read-private "
    "playlist-read-collaborative "
    "playlist-modify-public "
    "playlist-modify-private "
    "user-top-read "
    "user-read-recently-played"
)


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

def like_current_song():
    track = sp.current_user_playing_track()
    if track and "item" in track:
        track_id = track["item"]["id"]
        sp.current_user_saved_tracks_add([track_id])

def unlike_current_song(track_id):
    if track_id:
        sp.current_user_saved_tracks_delete([track_id])

def is_song_liked(track_id):
    if track_id:
        result = sp.current_user_saved_tracks_contains([track_id])
        return result[0] if result else False
    return False

def get_current_track_id():
    playback = sp.current_playback()
    return playback["item"]["id"] if playback and playback.get("item") else None

def get_playback_bundle(include_liked=False):
    playback = sp.current_playback()
    if not playback or not playback.get("item"):
        return None

    item = playback["item"]
    track_id = item["id"]

    liked = False
    if include_liked:
        try:
            liked = sp.current_user_saved_tracks_contains([track_id])[0]
        except Exception as e:
            print(f"[⚠️] Like status check failed: {e}")

    return {
        "title": item["name"],
        "artist": ", ".join([a["name"] for a in item["artists"]]),
        "duration_ms": item["duration_ms"],
        "position_ms": playback["progress_ms"],
        "repeat_state": playback.get("repeat_state", "off"),
        "shuffle_state": playback.get("shuffle_state", False),
        "track_id": track_id,
        "liked": liked,
        "is_playing": playback.get("is_playing", False),
    }
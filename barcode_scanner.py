from pynput import keyboard
import re
import requests

buffer = ""
add_mode = False
API_URL = "https://hmat-stocking-production.up.railway.app/barcode"

def send_barcode(code, delta):
    payload = {
        "code": code,
        "delta": delta,
        "client_id": "scanner"
    }
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"{'➕' if delta > 0 else '➖'} {code} | Stock now: {data['new_stock']}")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❗ Request failed: {e}")

def on_press(key):
    global buffer, add_mode

    try:
        if hasattr(key, 'char'):
            buffer += key.char
            if buffer.endswith("\\"):
                match = re.search(r"\\(.*?)\\", buffer)
                if match:
                    code = match.group(1)
                    delta = 1 if add_mode else -1
                    send_barcode(code, delta)
                    add_mode = False  # reset to subtract mode after 1 add
                    buffer = ""
        elif key == keyboard.Key.f2:
            add_mode = True
            print("🟢 Add Mode: ON (next scan will add stock)")
    except Exception as e:
        print(f"Error in on_press: {e}")

def main():
    print("🔍 Scan a barcode (no Enter needed)...")
    print("🔁 Press F2 to toggle Add Mode for next scan")
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

if __name__ == "__main__":
    main()
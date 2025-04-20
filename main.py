import sys
from render import render_main_screen

# System state and routing
state = {
    "active_app": None,
    "lines": [],
    "rects": [],
    "circles": []
}

def run_main():
    while True:
        action = render_main_screen(state)

        if action == "SKETCH":
            from apps.sketch import launch_sketch
            launch_sketch(state)
        elif action == "EXIT":
            sys.exit()

if __name__ == "__main__":
    run_main()

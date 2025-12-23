from modes import MODES
import subprocess

def execute_mode(mode_name: str):
    mode_name = mode_name.lower()

    if mode_name not in MODES:
        raise ValueError(f"Unknown mode: {mode_name}")

    mode = MODES[mode_name]

    # Open apps
    for app in mode.get("apps", []):
        subprocess.Popen(app, shell=True)

    # Open websites
    for url in mode.get("websites", []):
        subprocess.Popen(["cmd", "/c", "start", url], shell=True)

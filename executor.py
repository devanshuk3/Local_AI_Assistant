import os
import subprocess
from config import AUTOHOTKEY_PATH


def run_ahk(script: str):
    """Writes and executes an AutoHotkey v2 script."""

    os.makedirs("ahk", exist_ok=True)
    script_path = os.path.join("ahk", "command.ahk")

    with open(script_path, "w", encoding="utf-8") as file:
        file.write(script)

    subprocess.Popen([AUTOHOTKEY_PATH, script_path])

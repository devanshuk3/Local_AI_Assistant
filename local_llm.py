import subprocess
import json

MODEL = "mistral"

ACTION_ALIASES = {
    "make_folder": "create_folder",
    "create_directory": "create_folder",
    "new_folder": "create_folder",

    "open_application": "open_app",
    "launch_app": "open_app",

    "type": "type_text",
    "write_text": "type_text",

    "press": "press_keys",

    "study": "open_mode",
    "study_mode": "open_mode",
    "focus_mode": "open_mode",

    "coding": "open_mode",
    "work_mode": "open_mode",
}

SYSTEM_PROMPT = """
You are a strict JSON generator.

Rules:
- Output one JSON object only
- Use double quotes only
- No explanations
- No extra text

Allowed actions:
- create_folder
- open_app
- type_text
- press_keys
- open_mode
"""


def _run_ollama(prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


def _extract_json(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON found in response")

    depth = 0
    end = None

    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end is None:
        raise ValueError("Incomplete JSON output")

    raw_json = text[start:end]
    raw_json = raw_json.replace("'", '"')

    return json.loads(raw_json)


def interpret_command(user_command: str) -> dict:
    prompt = SYSTEM_PROMPT + "\nCommand:\n" + user_command
    response = _run_ollama(prompt)

    command = _extract_json(response)
    _validate_command(command)

    return command


def _validate_command(cmd: dict):
    action = str(cmd.get("action", "")).lower().strip()

    if action in ACTION_ALIASES:
        cmd["action"] = ACTION_ALIASES[action]

    from config import ALLOWED_ACTIONS

    if cmd["action"] not in ALLOWED_ACTIONS:
        raise ValueError(f"Action not allowed: {cmd['action']}")

    if not isinstance(cmd.get("params"), dict):
        raise ValueError("Params must be a dictionary")

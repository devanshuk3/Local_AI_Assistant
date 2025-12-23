import subprocess
import json
import re

MODEL = "mistral"   # ✅ Using Mistral via Ollama

SYSTEM_PROMPT = """
You are a strict JSON generator for Windows automation.

Your task:
Convert the user command into JSON ONLY.

Rules (must follow strictly):
- Output ONLY valid JSON
- No explanations
- No thinking
- No markdown
- No extra text

Allowed actions:
- create_folder
- open_app
- type_text
- press_keys

Output format:
{
  "action": "...",
  "params": { }
}
"""

def run_ollama(prompt: str) -> str:
    """Runs Ollama with Mistral and returns raw output."""
    result = subprocess.run(
        ["ollama", "run", MODEL],
        input=prompt,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()


def extract_json(text: str) -> dict:
    """
    Extracts the FIRST JSON object from model output.
    Handles extra text safely.
    """
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in model output")

    return json.loads(match.group(0))


def interpret_command(user_command: str) -> dict:
    """
    Main function to call from GUI.
    Returns validated JSON dict.
    """
    full_prompt = SYSTEM_PROMPT + "\nCommand:\n" + user_command

    raw_output = run_ollama(full_prompt)

    parsed = extract_json(raw_output)

    validate_command(parsed)

    return parsed


def validate_command(cmd: dict):
    """Security + schema validation."""
    allowed_actions = {
        "create_folder",
        "open_app",
        "type_text",
        "press_keys"
    }

    if not isinstance(cmd, dict):
        raise ValueError("Command is not a JSON object")

    if cmd.get("action") not in allowed_actions:
        raise ValueError("Action not allowed")

    if not isinstance(cmd.get("params"), dict):
        raise ValueError("Params must be an object")

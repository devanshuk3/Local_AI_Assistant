import subprocess
import json
import re

MODEL = "deepseek-r1:8b"   # ✅ Ollama local model

ACTION_ALIASES = {
    "make_folder": "create_folder",
    "create_directory": "create_folder",
    "create directory": "create_folder",
    "new_folder": "create_folder",

    "open_application": "open_app",
    "launch_app": "open_app",

    "type": "type_text",
    "write_text": "type_text",

    "press": "press_keys",
    "press_key": "press_keys"

    
}

ACTION_ALIASES.update({
    "study_mode": "open_mode",
    "study": "open_mode",
    "focus_mode": "open_mode",

    "coding_mode": "open_mode",
    "work_mode": "open_mode",
})


from system_utils import get_installed_apps

def _get_jarvis_prompt():
    apps = get_installed_apps()
    app_list = ", ".join(list(apps.keys())[:50]) # Limit to top 50 for token safety
    
    return f"""
Assume the persona of JARVIS, a highly capable and proactive AI assistant.
Your goal is to solve the user's intent using the available actions.
Think step-by-step about the logical sequence of events.

Available Actions:
- create_folder(name, location)
- open_app(app): Use standard names like 'Spotify', 'Chrome', 'Notepad'.
- type_text(text)
- press_keys(keys): Use standard AHK notation (e.g., 'Ctrl+L', 'Enter').
- wait(seconds)
- shell(command): For any direct system command or URL.

System Context:
The following apps are confirmed installed: {app_list}

Output ONLY valid JSON.
Format: {{"thought": "Your reasoning here", "steps": [{{"action": "...", "params": {{...}}}}]}}
"""

def _run_ollama(prompt: str) -> str:
    system_ctx = _get_jarvis_prompt()
    full_prompt = f"{system_ctx}\n\nUser Intent: {prompt}\n\nJarvis Response:"
    
    # Use format: json if supported by the model for better structure
    result = subprocess.run(
        ["ollama", "run", MODEL, "--format", "json"],
        input=full_prompt,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    if result.returncode != 0:
        # Fallback without --format json for older Ollama versions or models
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=full_prompt,
            capture_output=True,
            encoding="utf-8",
            errors="ignore"
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr)

    return result.stdout.strip()

def _extract_json(text: str) -> dict:
    import json
    
    # Pre-process: fix common AI mistakes (single quotes instead of double)
    processed = text.strip()
    # Replace single quotes at JSON-like positions (this is heuristic but helpful)
    # e.g., 'action': 'wait' -> "action": "wait"
    processed = re.sub(r"'(\w+)':", r'"\1":', processed)
    processed = re.sub(r":\s*'([^']*)'", r': "\1"', processed)

    try:
        start = processed.find("{")
        end = processed.rfind("}")
        if start != -1 and end != -1:
            return json.loads(processed[start:end+1])
    except:
        pass
    
    # Brute force depth matching if direct load fails
    start = processed.find("{")
    if start == -1: raise ValueError(f"No JSON found in response: {text[:100]}")
    
    depth = 0
    for i in range(start, len(processed)):
        if processed[i] == "{": depth += 1
        elif processed[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(processed[start:i + 1])
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON structure: {e}")

    raise ValueError("Incomplete JSON response from AI")




def interpret_command(user_command: str) -> dict:
    raw_output = _run_ollama(user_command)
    command = _extract_json(raw_output)
    _validate_command(command)
    return command


def _validate_command(cmd: dict):
    # normalize aliases FIRST
    action = str(cmd.get("action", "")).lower().strip()
    if action in ACTION_ALIASES:
        action = ACTION_ALIASES[action]
        cmd["action"] = action

    from config import ALLOWED_ACTIONS
    
    # Check for multi-step first
    if "steps" in cmd:
        if not isinstance(cmd["steps"], list):
            raise ValueError("The 'steps' parameter must be a list of actions.")
        return # Valid multi-step

    if not action:
        raise ValueError("AI failed to determine an action. Please try rephrasing.")
        
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Action '{action}' is not allowed or recognized.")

    if not isinstance(cmd.get("params"), dict):
        raise ValueError("Command parameters must be a JSON object.")




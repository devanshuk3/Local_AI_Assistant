import re

def try_rule_based_parse(text: str):
    text = text.lower().strip()

    # APP MAPPING
    app_map = {
        "chrome": "chrome",
        "google": "chrome",
        "brave": "brave",
        "edge": "msedge",
        "notepad": "notepad",
        "cmd": "cmd",
        "powershell": "powershell",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code"
    }

    # 1️⃣ RULE: "open [browser] in incognito [and go to/run/search] [target]"
    pattern_incognito = r"(?:open|launch|start)\s+(chrome|brave|edge|google|msedge)\s+in\s+incognito(?:\s+and\s+(?:run|go to|search|search for)\s+(.+))?"
    match_incog = re.search(pattern_incognito, text)
    if match_incog:
        app_name = match_incog.group(1)
        target = match_incog.group(2)
        actual_app = app_map.get(app_name, app_name)
        
        steps = [{"action": "open_app", "params": {"app": actual_app, "incognito": True}}]
        if target:
            steps.extend([
                {"action": "wait", "params": {"seconds": 1.5}},
                {"action": "press_keys", "params": {"keys": "Ctrl+L"}},
                {"action": "wait", "params": {"seconds": 0.2}},
                {"action": "type_text", "params": {"text": target if "." in target else f"https://www.google.com/search?q={target}"}},
                {"action": "press_keys", "params": {"keys": "Enter"}}
            ])
        return {"steps": steps}

    # 2️⃣ RULE: "open [app] and [verb] [target]"
    pattern_run = r"(?:open|launch|start)\s+([\w\s]+)\s+and\s+(?:run|go to|search|search for|create|make|new)\s+(.+)"
    match_run = re.search(pattern_run, text)
    
    if match_run:
        app_name = match_run.group(1).strip()
        target = match_run.group(2)
        
        actual_app = app_map.get(app_name, app_name)
        
        # Browser specific handling
        if actual_app in ["chrome", "brave", "msedge"]:
            if "." in target and " " not in target:
                url = target if target.startswith("http") else f"https://{target}"
                return {
                    "steps": [
                        {"action": "open_app", "params": {"app": actual_app}},
                        {"action": "wait", "params": {"seconds": 1.5}},
                        {"action": "press_keys", "params": {"keys": "Ctrl+L"}},
                        {"action": "wait", "params": {"seconds": 0.2}},
                        {"action": "type_text", "params": {"text": url}},
                        {"action": "press_keys", "params": {"keys": "Enter"}}
                    ]
                }
            else:
                return {
                    "steps": [
                        {"action": "open_app", "params": {"app": actual_app}},
                        {"action": "wait", "params": {"seconds": 1.5}},
                        {"action": "press_keys", "params": {"keys": "Ctrl+E"}},
                        {"action": "wait", "params": {"seconds": 0.2}},
                        {"action": "type_text", "params": {"text": target}},
                        {"action": "press_keys", "params": {"keys": "Enter"}}
                    ]
                }
        
        # VS Code specific handling
        if actual_app == "code":
            return {
                "steps": [
                    {"action": "open_app", "params": {"app": "code"}},
                    {"action": "wait", "params": {"seconds": 3}},
                    {"action": "press_keys", "params": {"keys": "Ctrl+Shift+P"}},
                    {"action": "wait", "params": {"seconds": 0.5}},
                    {"action": "type_text", "params": {"text": target}},
                    {"action": "press_keys", "params": {"keys": "Enter"}}
                ]
            }

    # 3️⃣ RULE: Universal Execution "run command [cmd]"
    if text.startswith("run command "):
        cmd = text.replace("run command", "").strip()
        return {"action": "shell", "params": {"command": cmd}}

    # 4️⃣ RULE: Simple "open [app]"
    pattern_open = r"^(?:open|launch|start)\s+([\w\s]+)$"
    match_open = re.search(pattern_open, text)
    if match_open:
        app_name = match_open.group(1).strip()
        if app_name in app_map:
            return {"action": "open_app", "params": {"app": app_map[app_name]}}

    return None

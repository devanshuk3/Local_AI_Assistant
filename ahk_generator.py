from config import ALLOWED_ACTIONS
import os

REQUIRED_PARAMS = {
    "open_app": ["app"],
    "type_text": ["text"],
    "press_keys": ["keys"],
    "wait": ["seconds"],
    "create_folder": ["name"]
}

from system_utils import resolve_app_path

def find_executable(app_name: str) -> str:
    """
    Search for the executable using system discovery and common fallbacks.
    """
    from config import APP_PATHS
    if app_name in APP_PATHS:
        return APP_PATHS[app_name]

    # Use the new autonomous discovery
    path = resolve_app_path(app_name)
    if os.path.exists(path) or "\\" in path:
        return path

    # Common fallbacks if registry fails
    search_paths = {
        "brave": [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        ],
        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        ],
        "msedge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ],
        "notepad": ["notepad.exe"],
    }

    if app_name in search_paths:
        for path in search_paths[app_name]:
            if os.path.exists(path) or "\\" not in path:
                return path
    
    return app_name


def generate_multi_step_ahk(steps: list) -> str:
    """
    Generate a single AHK v2 script from multiple steps.
    """
    script = ""

    for step in steps:
        code = generate_ahk(step)
        if not isinstance(code, str):
            raise ValueError("generate_ahk returned non-string")
        script += code + "\n"

    return script


def generate_ahk(command: dict):
    action = command.get("action")
    params = command.get("params", {})

    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Action not allowed: {action}")

    #Validate required params
    if action in REQUIRED_PARAMS:
        for key in REQUIRED_PARAMS[action]:
            if key not in params:
                raise ValueError(
                    f"Missing parameter '{key}' for action '{action}'"
                )

    # -------- CREATE FOLDER --------
    if action == "create_folder":
        name = params["name"]
        location = params.get("location", "desktop").lower()

        if location == "desktop":
            base = "A_Desktop"
        elif location == "documents":
            base = "A_MyDocuments"
        elif location == "downloads":
            base = 'A_Desktop "\\Downloads"'
        else:
            raise ValueError("Invalid folder location")

        return f'''
DirCreate {base} "\\{name}"
MsgBox "Folder '{name}' created"
'''

    # -------- OPEN APP --------
    if action == "open_app":
        app = params["app"].lower()

        # Virtual app: browser
        if app == "browser":
            exe = find_executable("chrome") # default
            return f'Run "{exe}" "https://www.google.com"\n'

        # Resolve path
        exe = find_executable(app)
        args = ""
        
        if params.get("incognito"):
            if app in ["chrome", "brave"]:
                args = " --incognito"
            elif app in ["edge", "msedge"]:
                args = " -inprivate"
        
        # AHK Run handles params better when path is quoted and args follow
        return f'Run "{exe}"{args}\n'


    # -------- TYPE TEXT --------
    if action == "type_text":
        safe = params["text"].replace('"', '""')
        return f'''
Send "{safe}"
'''

    # -------- PRESS KEYS --------
    if action == "press_keys":
        key = params["keys"]

        key_map = {
            "Enter": "{Enter}",
            "Ctrl+L": "^l",
            "Ctrl+T": "^t"
        }

        ahk_key = key_map.get(key, key)

        return f'''
Send "{ahk_key}"
'''

    # -------- WAIT -------
    if action == "wait":
        seconds = params.get("seconds", 1)
        ms = int(seconds * 1000)
        return f"Sleep {ms}\n"

    # -------- SHELL/RUN --------
    if action == "shell":
        cmd = params["command"].replace('"', '""')
        return f'Run "{cmd}"\n'

    return ""

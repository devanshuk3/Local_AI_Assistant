from config import ALLOWED_ACTIONS


def generate_ahk(command: dict) -> str:
    action = command["action"]
    params = command["params"]

    if action not in ALLOWED_ACTIONS:
        raise ValueError("Action not allowed")

    if action == "create_folder":
        name = params["name"]
        location = params.get("location", "desktop").lower()

        base = {
            "desktop": "A_Desktop",
            "documents": "A_MyDocuments",
            "downloads": 'A_Desktop "\\Downloads"'
        }.get(location)

        if not base:
            raise ValueError("Invalid folder location")

        return f'''
DirCreate {base} "\\{name}"
MsgBox "Folder '{name}' created"
'''

    if action == "open_app":
        return f'''
Run "{params["app"]}"
'''

    if action == "type_text":
        safe_text = params["text"].replace('"', '""')
        return f'''
Send "{safe_text}"
'''

    if action == "press_keys":
        return f'''
Send "{params["keys"]}"
'''

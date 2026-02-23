import winreg
import os

def get_installed_apps():
    """
    Scans the Windows Registry to find installed applications and their paths.
    Returns a dictionary of {app_name: install_location/exe_path}.
    """
    apps = {}
    
    # Registry paths to check
    registries = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    for hkey, path in registries:
        try:
            with winreg.OpenKey(hkey, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                            try:
                                location, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                                if location:
                                    apps[name.lower()] = location
                            except FileNotFoundError:
                                pass
                    except:
                        continue
        except:
            continue

    # Add common hardcoded fallbacks that registry might miss or have weird names
    apps["spotify"] = os.path.join(os.environ.get("APPDATA", ""), r"Spotify\Spotify.exe")
    apps["vscode"] = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Programs\Microsoft VS Code\Code.exe")
    apps["discord"] = os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Discord\Update.exe --processStart Discord.exe")
    
    return apps

def resolve_app_path(name: str):
    """
    Attempts to resolve a fuzzy app name to a concrete executable path.
    """
    name = name.lower()
    apps = get_installed_apps()
    
    # 1. Exact match
    if name in apps:
        path = apps[name]
        if os.path.exists(path) or ".exe" in path:
            return path

    # 2. Fuzzy match
    for app_name, app_path in apps.items():
        if name in app_name:
            if os.path.exists(app_path) or ".exe" in app_path:
                return app_path
                
    return name # Fallback to name for shell/PATH resolve

"""
Application management tools
"""

import os
import time
from .helpers import find_application_registry


def open_app(app_name):
    """Opens an application by name.

    Searches Windows registry for the app, then launches it.
    Falls back to Win+R Run dialog if not found in registry.

    Args:
        app_name: Application name (e.g., 'notepad', 'chrome', 'discord')

    Returns:
        Success message or error

    Examples:
        open_app('notepad')
        open_app('chrome')
        open_app('brave')
    """
    import subprocess
    import pyautogui

    windows_apps = {
        'notepad': r'C:\Windows\System32\notepad.exe',
        'calc': r'C:\Windows\System32\calc.exe',
        'calculator': r'C:\Windows\System32\calc.exe',
        'mspaint': r'C:\Windows\System32\mspaint.exe',
        'paint': r'C:\Windows\System32\mspaint.exe',
        'cmd': r'C:\Windows\System32\cmd.exe',
    }

    app_name_lower = app_name.lower()
    if app_name_lower in windows_apps:
        full_path = windows_apps[app_name_lower]
        if os.path.exists(full_path):
            try:
                print(f"DEBUG: Launching Windows built-in app: {full_path}")
                subprocess.Popen([full_path])
                return f"Opened '{app_name}' successfully"
            except Exception as e:
                return f"Error launching {full_path}: {str(e)}"

    full_path = find_application_registry(app_name)

    if full_path and os.path.exists(full_path):
        try:
            print(f"DEBUG: Launching with full path: {full_path}")
            subprocess.Popen([full_path])
            return f"Opened '{app_name}' successfully"
        except Exception as e:
            return f"Error launching {full_path}: {str(e)}"
    else:
        print(f"DEBUG: Couldn't find full path, trying Win+R with: {app_name}")
        try:
            pyautogui.hotkey('win', 'r')
            time.sleep(0.5)
            pyautogui.write(app_name, interval=0.05)
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)
            return f"Opened '{app_name}' via Run dialog"
        except Exception as e:
            return f"Error: {str(e)}"

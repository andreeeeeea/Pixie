"""
Application management tools
"""

import os
import time
import subprocess
import logging
import pyautogui
import win32gui
import win32con
from .helpers import find_application_registry, is_app_running

logger = logging.getLogger(__name__)


def open_app(app_name):
    """Opens an application by name or focuses it if already running.

    First checks if the app is already running. If yes, focuses the existing window.
    If not running, launches a new instance and focuses it.

    Args:
        app_name: Application name (e.g., 'notepad', 'chrome', 'discord')

    Returns:
        Success message or error

    Examples:
        open_app('notepad')
        open_app('chrome')
        open_app('brave')
    """
    if is_app_running(app_name):
        logger.debug(f"Application {app_name} is already running, focusing window")
        try:
            hwnd = None
            def callback(window_hwnd, app_name_lower):
                if win32gui.IsWindowVisible(window_hwnd):
                    window_text = win32gui.GetWindowText(window_hwnd)
                    if app_name_lower in window_text.lower():
                        nonlocal hwnd
                        hwnd = window_hwnd
                        return False
                return True

            win32gui.EnumWindows(callback, app_name.lower())

            if hwnd:
                if win32gui.IsIconic(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(0.2)

                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                time.sleep(0.1)

                win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                     win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

                win32gui.SetForegroundWindow(hwnd)
                time.sleep(0.3)

                pyautogui.press('tab')
                time.sleep(0.2)

                window_title = win32gui.GetWindowText(hwnd)
                logger.debug(f"Successfully focused window: {window_title}")
                return f"Focused existing '{app_name}' window"
            else:
                return f"'{app_name}' is running but couldn't find window"
        except Exception as e:
            return f"Error focusing window: {str(e)}"

    logger.debug(f"Application {app_name} not running, launching new instance")

    windows_apps = {
        'notepad': r'C:\Windows\System32\notepad.exe',
        'calc': r'C:\Windows\System32\calc.exe',
        'calculator': r'C:\Windows\System32\calc.exe',
        'mspaint': r'C:\Windows\System32\mspaint.exe',
        'paint': r'C:\Windows\System32\mspaint.exe',
        'cmd': r'C:\Windows\System32\cmd.exe',
    }

    app_name_lower = app_name.lower()
    full_path = None

    if app_name_lower in windows_apps:
        full_path = windows_apps[app_name_lower]
        if not os.path.exists(full_path):
            full_path = None

    if not full_path:
        full_path = find_application_registry(app_name)

    if full_path and os.path.exists(full_path):
        try:
            logger.debug(f"Launching application: {full_path}")
            subprocess.Popen([full_path])
            time.sleep(1.5)

            try:
                hwnd = None
                def callback(window_hwnd, app_name_lower):
                    if win32gui.IsWindowVisible(window_hwnd):
                        window_text = win32gui.GetWindowText(window_hwnd)
                        if app_name_lower in window_text.lower():
                            nonlocal hwnd
                            hwnd = window_hwnd
                            return False
                    return True

                win32gui.EnumWindows(callback, app_name.lower())

                if hwnd:
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        time.sleep(0.2)

                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

                    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    time.sleep(0.1)

                    win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                         win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)

                    pyautogui.press('tab')
                    time.sleep(0.2)

                    window_title = win32gui.GetWindowText(hwnd)
                    logger.debug(f"Successfully focused new window: {window_title}")
            except Exception as e:
                logger.debug(f"Could not auto-focus new window: {e}")

            return f"Opened '{app_name}' successfully"
        except Exception as e:
            return f"Error launching {full_path}: {str(e)}"
    else:
        logger.debug(f"Could not find application path, attempting to launch via Run dialog: {app_name}")
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

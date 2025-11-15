"""
Core primitive tools for basic computer control
"""

import pyautogui
import time


def type_text(text):
    """Types the specified text using keyboard automation.

    Args:
        text: String to type

    Returns:
        Confirmation message or error
    """
    try:
        pyautogui.write(text, interval=0.1)
        return f"Typed text: {text}"
    except Exception as e:
        return f"Error: {str(e)}"


def clear_text():
    """Clears text from the current text field.

    Selects all text and clears it.

    Returns:
        Success message"""

    pyautogui.write('ctrl', 'a')
    time.sleep(0.1)
    pyautogui.press('delete')
    time.sleep(0.1)

    return "Cleared text field"


def press_key(key):
    """Presses a specified keyboard key.

    Args:
        key: Key name (e.g., 'enter', 'backspace', 'tab', 'a', 'shift')

    Returns:
        Confirmation message or error
    """
    pyautogui.press(key)

def press_hotkey(keys):
    """Presses hotkeys.
    Args:
        *keys: Variable number of key names to press together

    Returns:
        Success message"""

    pyautogui.hotkey(*keys)
    return f"Pressed hotkey: {'+'.join(keys)}"

def click(x, y):
    """Clicks at the specified screen coordinates.

    Args:
        x: X coordinate (pixels from left)
        y: Y coordinate (pixels from top)

    Returns:
        Confirmation message or error
    """
    try:
        pyautogui.click(x, y)
        return f"Clicked at coordinates: ({x}, {y})"
    except Exception as e:
        return f"Error: {str(e)}"


def take_screenshot():
    """Takes a screenshot and returns it as a PIL Image object.

    Returns:
        PIL Image object, or error message string
    """
    try:
        screenshot = pyautogui.screenshot()
        return screenshot
    except Exception as e:
        return f"Error: {str(e)}"

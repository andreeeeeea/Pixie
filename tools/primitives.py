"""
Core primitive tools for basic computer control
"""


def calculate(expression):
    """Performs mathematical calculations using eval().

    Args:
        expression: Math expression as string (e.g., "2 + 2", "10 * 5")

    Returns:
        Result as string, or error message
    """
    try:
        ans = eval(expression)
        return str(ans)
    except Exception:
        return "Error: invalid expression"


def type_text(text):
    """Types the specified text using keyboard automation.

    Args:
        text: String to type

    Returns:
        Confirmation message or error
    """
    import pyautogui
    try:
        pyautogui.write(text, interval=0.1)
        return f"Typed text: {text}"
    except Exception as e:
        return f"Error: {str(e)}"


def press_key(key):
    """Presses a specified keyboard key.

    Args:
        key: Key name (e.g., 'enter', 'backspace', 'tab', 'a', 'shift')

    Returns:
        Confirmation message or error
    """
    import pyautogui
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Error: {str(e)}"


def click(x, y):
    """Clicks at the specified screen coordinates.

    Args:
        x: X coordinate (pixels from left)
        y: Y coordinate (pixels from top)

    Returns:
        Confirmation message or error
    """
    import pyautogui
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
    import pyautogui
    try:
        screenshot = pyautogui.screenshot()
        return screenshot
    except Exception as e:
        return f"Error: {str(e)}"

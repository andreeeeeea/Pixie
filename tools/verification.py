"""
Verification functions to check if actions succeeded
"""

import time
import google.generativeai as genai
from .helpers import is_app_running
from .primitives import take_screenshot


def verify_action_succeeded(action_description):
    """Verifies if an action succeeded using a hybrid approach.

    Strategy:
    1. If an action involves opening an app -> check running processes first.
    2. If process check is unclear/action is not app-related -> use vision.

    Vision takes a screenshot and asks Gemini to verify if the described action actually succeeded by analysing what's visible on the screen.

    Args:
        action_description: Description of what was just done (e.g., 'Opened Notepad', 'Clicked the submit button')

    Returns:
        dict: {
            'success': bool,        -> True if action succeeded
            'explanation': str,     -> What was observed
            'method': str           -> 'process' or 'vision
        }
    """
    import re

    action_lower = action_description.lower()

    if 'open' in action_lower:
        patterns = [
            r'open(?:ed|ing)?\s+([a-zA-Z]+)',
            r'launch(?:ed|ing)?\s+([a-zA-Z]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, action_lower)
            if match:
                app_name = match.group(1)
                print(f"DEBUG: Extracted app name: {app_name}")

                if is_app_running(app_name):
                    return {
                        'success': True,
                        'explanation': f"Process check confirmed: {app_name} is running",
                        'method': 'process'
                    }
                else:
                    return {
                        'success': False,
                        'explanation': f"Process check failed: {app_name} is not running",
                        'method': 'process'
                    }
    print("DEBUG: Using vision-based verification")
    try:
        time.sleep(1)
        screenshot = take_screenshot()

        vision_model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"Did this action succeed: {action_description}? Answer YES or NO, then explain what you see in a short sentence."

        response = vision_model.generate_content([prompt, screenshot])
        response_text = response.text

        success = 'yes' in response_text.lower()

        return {
            'success' : success,
            'explanation': response_text,
            'method': 'vision'
        }
    except Exception as e:
        return {
            'success': False,
            'explanation': f'Error: {str(e)}',
            'method': 'vision'
        }

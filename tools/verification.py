"""
Verification functions to check if actions succeeded
"""

import time
import logging
import google.generativeai as genai
from .helpers import is_app_running
from .primitives import take_screenshot

logger = logging.getLogger(__name__)


def verify_action_succeeded(action_name, action_args):
    """Verifies if an action succeeded using a hybrid approach.

    Strategy:
    1. If an action involves opening an app -> check running processes first.
    2. If process check is unclear/action is not app-related -> use vision.

    Vision takes a screenshot and asks Gemini to verify if the described action actually succeeded by analysing what's visible on the screen.

    Args:
        action_name: The function name (e.g., 'open_app', 'click')
        action_args: The argument dict (e.g., {'app_name': 'notepad'})

    Returns:
        dict: {
            'success': bool,        -> True if action succeeded
            'explanation': str,     -> What was observed
            'method': str           -> 'process' or 'vision
        }
    """
    if action_name == 'open_app':
        app_name = action_args.get('app_name')
        if app_name and is_app_running(app_name):
            return {'success': True, 'explanation': f"{app_name} is running", 'method': 'process'}
        else:
            return {'success': False, 'explanation': f"{app_name} is not running", 'method': 'process'}

    # Vision-based verification disabled to save API calls during testing
    # Uncomment below to enable vision verification for non-app actions

    # logger.debug("Using vision-based verification")
    # try:
    #     time.sleep(1)
    #     screenshot = take_screenshot()
    #
    #     vision_model = genai.GenerativeModel('gemini-2.5-flash')
    #     prompt = f"Did this action succeed: {action_name} {action_args}? Answer YES or NO, then explain what you see in a short sentence."
    #
    #     response = vision_model.generate_content([prompt, screenshot])
    #     response_text = response.text
    #
    #     success = 'yes' in response_text.lower()
    #
    #     return {
    #         'success' : success,
    #         'explanation': response_text,
    #         'method': 'vision'
    #     }
    # except Exception as e:
    #     return {
    #         'success': False,
    #         'explanation': f'Error: {str(e)}',
    #         'method': 'vision'
    #     }

    # Default: assume success for non-app actions when vision is disabled
    return {
        'success': True,
        'explanation': f"Action completed (vision verification disabled)",
        'method': 'none'
    }

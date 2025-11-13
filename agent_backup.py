import google.generativeai as genai
import os
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import cv2
import numpy as np
import time
import shutil

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

tesseract_path = shutil.which('tesseract')
if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

genai.configure(api_key=api_key)


def calculate(expression):
    try:
        ans = eval(expression)
        return str(ans)
    except Exception:
        return "Error: invalid expression"

def type_text(text):
    """Types the specified text using pyautogui"""
    import pyautogui
    try:
        pyautogui.write(text, interval=0.1)
        return f"Typed text: {text}"
    except Exception as e:
        return f"Error: {str(e)}"

def press_key(key):
    """Presses a specified key using pyautogui"""
    import pyautogui
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Error: {str(e)}"

def click(x, y):
    """Clicks at the specified (x, y) coordinates using pyautogui"""
    import pyautogui
    try:
        pyautogui.click(x, y)
        return f"Clicked at coordinates: ({x}, {y})"
    except Exception as e:
        return f"Error: {str(e)}"

def take_screenshot():
    """Takes a screenshot and returns it for visual analysis.
      After calling this, you will receive the image and can analyze it
      to identify UI elements, read text, find coordinates, etc."""
    import pyautogui
    try:
        screenshot = pyautogui.screenshot()
        ##screenshot.save('screenshot.png')
        return screenshot  # Return the PIL Image object
    except Exception as e:
        return f"Error: {str(e)}"

def find_application_registry(app_name):
    """Finds application path from Windows registry.
    Used for finding applications the user may instruct the AI agent to use."""

    import winreg
    import os

    app_name_lower = app_name.lower()

    print(f"DEBUG: Searching registry for: {app_name}")

    registry_roots = [
        (winreg.HKEY_LOCAL_MACHINE, "HKLM"),
        (winreg.HKEY_CURRENT_USER, "HKCU")
    ]

    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]

    for root, root_name in registry_roots:
        for reg_path in registry_paths:
            try:
                key = winreg.OpenKey(root, reg_path)
                num_subkeys = winreg.QueryInfoKey(key)[0]
                print(f"DEBUG: Checking {root_name}\\{reg_path} ({num_subkeys} entries)")

                for i in range(num_subkeys):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)

                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]

                        if app_name_lower in display_name.lower():
                            print(f"DEBUG: Found match: {display_name}")

                            try:
                                icon_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                full_path = icon_path.replace('"', '').split(',')[0]
                                if full_path.endswith('.exe') and os.path.exists(full_path):
                                    print(f"DEBUG: Extracted full path from DisplayIcon: {full_path}")
                                    winreg.CloseKey(subkey)
                                    winreg.CloseKey(key)
                                    return full_path
                            except Exception as e:
                                print(f"DEBUG: DisplayIcon failed: {e}")

                            try:
                                uninstall_path = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                if '.exe' in uninstall_path:
                                    full_path = uninstall_path.split('.exe')[0] + '.exe'
                                    full_path = full_path.replace('"', '')
                                    if os.path.exists(full_path):
                                        print(f"DEBUG: Extracted full path from UninstallString: {full_path}")
                                        winreg.CloseKey(subkey)
                                        winreg.CloseKey(key)
                                        return full_path
                            except Exception as e:
                                print(f"DEBUG: UninstallString failed: {e}")

                        winreg.CloseKey(subkey)
                    except Exception as e:
                        continue
                winreg.CloseKey(key)
            except Exception as e:
                print(f"DEBUG: Could not open {root_name}\\{reg_path}: {e}")

    print(f"DEBUG: No match found in registry")
    return None

def verify_action_succeeded(action_description):
    """Take a screenshot and asks AI if the action succeeded.
    Returns a dict with verification results {'success': True/False, 'explanation': Explanation}"""

    try:
        screenshot = take_screenshot()
        vision_model = genai.GenerativeModel('gemini-2.5-flash', )

        prompt = f"""Look at this screenshot. Did this action succeed: {action_description}?
        Answer in this format:
        SUCCESS: yes/no
        EXPLANATION: what you observe"""

        response = vision_model.generate_content([prompt, screenshot])
        response_text = response.text

        success = 'yes' in response_text.lower()

        return {
            'success' : success,
            'explanation': response_text
        }

    except Exception as e:
        return {'success': False, 'explanation': f'Error: {str(e)}'}

    

def open_app(app_name):
    """Opens an application by finding it in the registry and launching it.
    Examples: 'brave', 'chrome', 'discord', 'league of legends', etc."""

    import subprocess
    import os

    full_path = find_application_registry(app_name)

    if full_path and os.path.exists(full_path):
        try:
            print(f"DEBUG: Launching with full path: {full_path}")
            subprocess.Popen([full_path])
            return f"Opened '{app_name}' successfully"
        except Exception as e:
            return f"Error launching {full_path}: {str(e)}"
    else:
        import pyautogui
        import time

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


## VISION-RELATED FUNCTIONS - COMMENTED OUT TO SAVE API CALLS ##

# def find_text_on_screen(text):
#     """Finds text on screen using OCR and returns its coordinates.
#     Returns the center (x, y) coordinates where the text was found."""
#
#     import pytesseract
#     from pytesseract import Output
#
#     try:
#         screenshot = take_screenshot()
#         ocr_data = pytesseract.image_to_data(screenshot, output_type = Output.DICT)
#         target_text = text.lower()
#
#         for i in range(len(ocr_data['text'])):
#             detected_text = ocr_data['text'][i].lower()
#
#             if target_text in detected_text:
#                 x = ocr_data['left'][i]
#                 y = ocr_data['top'][i]
#                 width = ocr_data['width'][i]
#                 height = ocr_data['height'][i]
#
#                 center_x = x + width // 2
#                 center_y = y + height // 2
#
#                 return f"Found '{text}' at coordinates ({center_x}, {center_y})"
#
#         return f"Error: '{text}' not found on screen"
#
#     except Exception as e:
#         return f"Error: {str(e)}"

# def divide_screen_into_grid(screenshot, rows=3, cols=3):
#     """Divides a screenshot into a grid of smaller images"""
#     width, height = screenshot.size
#     cell_width = width // cols
#     cell_height = height // rows
#
#     grid_cells = []
#     row_labels = ['A', "B", "C", "D", "E"][:rows]
#     for row_idx, row_label in enumerate(row_labels):
#         for col_idx in range(cols):
#              x_start = col_idx * cell_width
#              y_start = row_idx * cell_height
#              x_end = x_start + cell_width
#              y_end = y_start + cell_height
#
#              cell_image = screenshot.crop((x_start, y_start, x_end, y_end))
#              grid_label = f"{row_label}{col_idx + 1}"
#
#              grid_cells.append((
#                  grid_label,
#                  cell_image,
#                  x_start,
#                  y_start,
#                  cell_width,
#                  cell_height
#              ))
#     return grid_cells

# def find_icon_recursive(region_img, icon_name, x_offset, y_offset, vision_model, depth=0, max_depth=3):
#    """Recursively subdivides a region to find icon with precision.
#
#    Args:
#        region_img: PIL Image of the region to search
#        icon_name: Name of icon to find
#        x_offset: X offset of this region in screen coordinates
#        y_offset: Y offset of this region in screen coordinates
#        vision_model: Gemini vision model instance
#        depth: Current recursion depth
#        max_depth: Maximum recursion depth
#
#    Returns:
#        Tuple (x, y, found) or (None, None, False)
#    """
#    width, height = region_img.size
#
#    print(f"  {'  ' * depth}🔍 Depth {depth}: Searching {width}x{height} region at offset ({x_offset}, {y_offset})")
#
#    if width < 80 or height < 80 or depth >= max_depth:
#        center_x = x_offset + width // 2
#        center_y = y_offset + height // 2
#        print(f"  {'  ' * depth}🎯 Min size/max depth reached. Using center: ({center_x}, {center_y})")
#        return center_x, center_y, True
#
#    grid_cells = divide_screen_into_grid(region_img, rows=2, cols=2)
#
#    for grid_label, cell_image, cell_x, cell_y, cell_w, cell_h in grid_cells:
#        prompt = f"Is there a {icon_name} icon visible in this image? Answer only 'yes' or 'no'."
#
#        response = vision_model.generate_content([prompt, cell_image])
#        answer = response.text.strip().lower()
#
#        print(f"  {'  ' * depth}🔎 Cell {grid_label}: {answer}")
#
#        if 'yes' in answer:
#            abs_x_offset = x_offset + cell_x
#            abs_y_offset = y_offset + cell_y
#
#            result_x, result_y, found = find_icon_recursive(
#                cell_image,
#                icon_name,
#                abs_x_offset,
#                abs_y_offset,
#                vision_model,
#                depth + 1,
#                max_depth
#            )
#
#            if found:
#                return result_x, result_y, True
#
#        time.sleep(0.3)
#
#    center_x = x_offset + width // 2
#    center_y = y_offset + height // 2
#    print(f"  {'  ' * depth}⚠️  Not found in any sub-cell at depth {depth}. Using region center: ({center_x}, {center_y})")
#    return center_x, center_y, True

#def find_icon_on_screen(icon_name, precision='high'):
#    """Finds an icon using recursive subdivision for maximum accuracy.
#
#    Stage 1: Identify rough region (1 API call - fast!)
#    Stage 2: Recursively subdivide that region until icon is precisely located
#            - Depth 0: 640x360 region
#            - Depth 1: 320x180 cells
#            - Depth 2: 160x90 cells
#            - Depth 3: 80x45 cells (final precision)
#
#    Args:
#        icon_name: Description of icon (e.g., "Brave browser", "Chrome")
#        precision: 'low' (stage 1 only) or 'high' (recursive subdivision, default)
#
#    Returns:
#        Dictionary with x, y coordinates and metadata
#    """
#    import pyautogui
#    import google.generativeai as genai
#
#    try:
#        # Take screenshot
#        screenshot = pyautogui.screenshot()
#        width, height = screenshot.size
#        vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
#
#        prompt = f"""Look at this screen. Where is the {icon_name} icon located?
#Answer with ONLY ONE word from these options:
#- top-left
#- top-center
#- top-right
#- middle-left
#- center
#- middle-right
#- bottom-left
#- bottom-center
#- bottom-right
#- not-found
#
#Answer with just ONE word, nothing else."""
#
#        response = vision_model.generate_content([prompt, screenshot])
#        region = response.text.strip().lower().replace('-', '_')
#
#        if 'not' in region or 'found' in region:
#            return {"error": f"Icon '{icon_name}' not visible on screen"}
#
#        region_coords = {
#            'top_left': (width // 6, height // 6),
#            'top_center': (width // 2, height // 6),
#            'top_right': (5 * width // 6, height // 6),
#            'middle_left': (width // 6, height // 2),
#            'center': (width // 2, height // 2),
#            'middle_right': (5 * width // 6, height // 2),
#            'bottom_left': (width // 6, 5 * height // 6),
#            'bottom_center': (width // 2, 5 * height // 6),
#            'bottom_right': (5 * width // 6, 5 * height // 6),
#        }
#
#        if precision == 'low':
#            for key in region_coords:
#                if key == region:
#                    x, y = region_coords[key]
#                    return {
#                        "x": x,
#                        "y": y,
#                        "region": key,
#                        "precision": "low",
#                        "message": f"Found '{icon_name}' in {key.replace('_', '-')} region at ({x}, {y})"
#                    }
#
#        third_width = width // 3
#        third_height = height // 3
#
#        region_bounds = {
#            'top_left': (0, 0, third_width, third_height),
#            'top_center': (third_width, 0, third_width * 2, third_height),
#            'top_right': (third_width * 2, 0, width, third_height),
#            'middle_left': (0, third_height, third_width, third_height * 2),
#            'center': (third_width, third_height, third_width * 2, third_height * 2),
#            'middle_right': (third_width * 2, third_height, width, third_height * 2),
#            'bottom_left': (0, third_height * 2, third_width, height),
#            'bottom_center': (third_width, third_height * 2, third_width * 2, height),
#            'bottom_right': (third_width * 2, third_height * 2, width, height),
#        }
#
#        bounds = None
#        matched_key = None
#        for key in region_bounds:
#            if key == region:
#                bounds = region_bounds[key]
#                matched_key = key
#                break
#
#        if not bounds:
#            x, y = region_coords.get(region, (width // 2, height // 2))
#            return {
#                "x": x,
#                "y": y,
#                "region": region,
#                "precision": "medium",
#                "message": f"Found '{icon_name}' approximately at ({x}, {y})"
#            }
#
#        x1, y1, x2, y2 = bounds
#        region_img = screenshot.crop((x1, y1, x2, y2))
#
#        print(f"  📍 Starting recursive search in {region.replace('_', '-')} region...")
#
#        final_x, final_y, found = find_icon_recursive(
#            region_img,
#            icon_name,
#            x1,
#            y1,
#            vision_model,
#            depth=0,
#            max_depth=3
#        )
#
#        if found:
#            return {
#                "x": final_x,
#                "y": final_y,
#                "region": region,
#                "precision": "high",
#                "message": f"Found '{icon_name}' at ({final_x}, {final_y}) in {region.replace('_', '-')} region"
#            }
#        else:
#            center_x = (x1 + x2) // 2
#            center_y = (y1 + y2) // 2
#            return {
#                "x": center_x,
#                "y": center_y,
#                "region": region,
#                "precision": "medium",
#                "message": f"Icon '{icon_name}' not found precisely, using region center at ({center_x}, {center_y})"
#            }
#
#    except Exception as e:
#        return {"error": str(e)}
#def click_on_icon(icon_name, precision='high'):
#    """Finds and clicks an icon using hybrid vision search.
#
#    Args:
#        icon_name: Description of icon (e.g., "Brave browser")
#        precision: 'low' (fast, ~60% accurate) or 'high' (slower, ~80% accurate)
#    """
#    import pyautogui
#
#    result = find_icon_on_screen(icon_name, precision)
#
#    if "error" in result:
#        return result["error"]
#
#    x, y = result["x"], result["y"]
#    pyautogui.click(x, y)
#
#    return f"Clicked '{icon_name}' at ({x}, {y}) [{result.get('precision', 'unknown')} precision]"
#
def analyse_screen_region(grid_position):
    """TO DO"""


model = genai.GenerativeModel(
    'gemini-2.5-flash',
    tools = [open_app, type_text, press_key, click, take_screenshot],
    generation_config={
        'temperature': 0.2,
        'max_output_tokens': 2048,
    },
    system_instruction="""You are a helpful computer control assistant.
        When the user asks you to do something, use the available tools to complete the task directly.
        Be concise and focused - only do what the user asks for.
        After completing a task, confirm what you did without offering additional unrelated actions."""
)

print("AI Agent started! Type 'exit' or 'quit' to stop.\n")

##messages = []

while True:
    ##print(f"\nDEBUG: Previous messages: {messages}")
    user_question = input("\nYou: ")

    if user_question.lower() in ['exit', 'quit', 'bye']:
        print("Goodbye!")
        break

    ##messages.append(user_question) For conversational memory
    messages = [user_question]
    print(f"\nDEBUG: Starting agent loop with user question: {user_question}")

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n --- Iteration {iteration} ---")

        response = model.generate_content(messages)

        print(f"DEBUG: Response candidates: {len(response.candidates) if response.candidates else 0}")

        if not response.candidates:
            print("Warning: No response from API")
            break

        if not response.candidates[0].content.parts:
            finish_reason = response.candidates[0].finish_reason
            if finish_reason == 1:
                print("\n✓ Task completed successfully!")
                break
            else:
                print(f"Warning: Empty response (finish_reason: {finish_reason})")
                break

        part = response.candidates[0].content.parts[0]

        print(f"DEBUG: Response type: {type(part).__name__}")

        if hasattr(part, 'text') and part.text:
            print(f"DEBUG: Model says: {part.text[:100]}..." if len(part.text) > 100 else f"DEBUG: Model says: {part.text}")

        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args)
            print(f"DEBUG: Function call detected: {function_name}")
            print(f"DEBUG: Arguments: {function_args}")
            screenshot_image = None

            if function_name == 'open_calculator_and_compute':
                expression = function_args['expression']
                result = open_calculator_and_compute(expression)
            elif function_name == "calculate":
                expression = function_args['expression']
                result = calculate(expression)
            elif function_name == "open_app":
                app_name = function_args['app_name']
                result = open_app(app_name)
            elif function_name == "type_text":
                text = function_args['text']
                result = type_text(text)
            elif function_name == "press_key":
                key = function_args['key']
                result = press_key(key)
            elif function_name == "click":
                x = function_args['x']
                y = function_args['y']
                result = click(x, y)
            elif function_name == "take_screenshot":
                screenshot_image = take_screenshot()
                result = "Screenshot captured"
                print(f"DEBUG: Screenshot captured successfully")
            # elif function_name == "find_text_on_screen":
            #     text = function_args['text']
            #     result = find_text_on_screen(text)
            # elif function_name == "find_icon_on_screen":
            #     icon_name = function_args['icon_name']
            #     precision = function_args.get('precision', 'high')
            #     result = find_icon_on_screen(icon_name, precision)
            # elif function_name == "click_on_icon":
            #     icon_name = function_args['icon_name']
            #     precision = function_args.get('precision', 'high')
            #     result = click_on_icon(icon_name, precision)

            print(f"DEBUG: Function result: {result}")

            function_response = genai.protos.FunctionResponse(
                name = function_name,
                response = {'result': result}
            )
            function_response_part = genai.protos.Part(
                function_response = function_response
            )

            messages.append(part)
            messages.append(function_response_part)
            print(f"DEBUG: Added function call and response to messages (total messages: {len(messages)})")

            if screenshot_image is not None:
                print(f"DEBUG: Adding screenshot to messages")
                # Create a message with both text and image
                messages.append("Here is the screenshot:")
                messages.append(screenshot_image)
                print(f"DEBUG: Screenshot added to messages (total messages: {len(messages)})")
        else:
            # Check if it's a tool_code response (starts with "tool_code\n")
            if hasattr(part, 'text') and part.text and part.text.strip().startswith('tool_code'):
                print("DEBUG: Model returned code suggestion instead of function call")
                print("DEBUG: Telling model to use function calls instead...")
                # Add a message to push the model to use function calls
                messages.append("Please use the available function calls to perform actions, not code suggestions.")
                continue  # Go to next iteration

            print("DEBUG: No function call detected - this is the final answer")
            print("\nFinal answer:")
            try:
                print(response.text)
            except ValueError:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text)
            break



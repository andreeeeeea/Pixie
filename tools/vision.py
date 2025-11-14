"""
Vision functions for screen analysis and icon detection
Currently disabled to save API costs
"""

# def find_text_on_screen(text):
#     """Finds text on screen using OCR and returns its coordinates.
#
#     Returns the center (x, y) coordinates where the text was found.
#     """
#     import pytesseract
#     from pytesseract import Output
#
#     try:
#         screenshot = take_screenshot()
#         ocr_data = pytesseract.image_to_data(screenshot, output_type=Output.DICT)
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
#     """Divides a screenshot into a grid of smaller images for analysis."""
#     width, height = screenshot.size
#     cell_width = width // cols
#     cell_height = height // rows
#
#     grid_cells = []
#     row_labels = ['A', "B", "C", "D", "E"][:rows]
#
#     for row_idx, row_label in enumerate(row_labels):
#         for col_idx in range(cols):
#             x_start = col_idx * cell_width
#             y_start = row_idx * cell_height
#             x_end = x_start + cell_width
#             y_end = y_start + cell_height
#
#             cell_image = screenshot.crop((x_start, y_start, x_end, y_end))
#             grid_label = f"{row_label}{col_idx + 1}"
#
#             grid_cells.append((
#                 grid_label,
#                 cell_image,
#                 x_start,
#                 y_start,
#                 cell_width,
#                 cell_height
#             ))
#
#     return grid_cells


# def find_icon_recursive(region_img, icon_name, x_offset, y_offset, vision_model, depth=0, max_depth=3):
#     """Recursively subdivides a region to find an icon with high precision.
#
#     Args:
#         region_img: PIL Image of the region to search
#         icon_name: Name of icon to find
#         x_offset: X offset of this region in screen coordinates
#         y_offset: Y offset of this region in screen coordinates
#         vision_model: Gemini vision model instance
#         depth: Current recursion depth
#         max_depth: Maximum recursion depth
#
#     Returns:
#         Tuple (x, y, found) or (None, None, False)
#     """
#     width, height = region_img.size
#
#     print(f"  {'  ' * depth}🔍 Depth {depth}: Searching {width}x{height} region at offset ({x_offset}, {y_offset})")
#
#     if width < 80 or height < 80 or depth >= max_depth:
#         center_x = x_offset + width // 2
#         center_y = y_offset + height // 2
#         print(f"  {'  ' * depth}🎯 Min size/max depth reached. Using center: ({center_x}, {center_y})")
#         return center_x, center_y, True
#
#     grid_cells = divide_screen_into_grid(region_img, rows=2, cols=2)
#
#     for grid_label, cell_image, cell_x, cell_y, cell_w, cell_h in grid_cells:
#         prompt = f"Is there a {icon_name} icon visible in this image? Answer only 'yes' or 'no'."
#
#         response = vision_model.generate_content([prompt, cell_image])
#         answer = response.text.strip().lower()
#
#         print(f"  {'  ' * depth}🔎 Cell {grid_label}: {answer}")
#
#         if 'yes' in answer:
#             abs_x_offset = x_offset + cell_x
#             abs_y_offset = y_offset + cell_y
#
#             result_x, result_y, found = find_icon_recursive(
#                 cell_image,
#                 icon_name,
#                 abs_x_offset,
#                 abs_y_offset,
#                 vision_model,
#                 depth + 1,
#                 max_depth
#             )
#
#             if found:
#                 return result_x, result_y, True
#
#         time.sleep(0.3)
#
#     center_x = x_offset + width // 2
#     center_y = y_offset + height // 2
#     print(f"  {'  ' * depth}⚠️  Not found in any sub-cell at depth {depth}. Using region center: ({center_x}, {center_y})")
#     return center_x, center_y, True


# def find_icon_on_screen(icon_name, precision='high'):
#     """Finds an icon using recursive subdivision for maximum accuracy.
#
#     Stage 1: Identify rough region (1 API call - fast!)
#     Stage 2: Recursively subdivide that region until icon is precisely located
#             - Depth 0: 640x360 region
#             - Depth 1: 320x180 cells
#             - Depth 2: 160x90 cells
#             - Depth 3: 80x45 cells (final precision)
#
#     Args:
#         icon_name: Description of icon (e.g., "Brave browser", "Chrome")
#         precision: 'low' (stage 1 only) or 'high' (recursive subdivision, default)
#
#     Returns:
#         Dictionary with x, y coordinates and metadata
#     """
#     import pyautogui
#
#     try:
#         screenshot = pyautogui.screenshot()
#         width, height = screenshot.size
#         vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
#
#         prompt = f"""Look at this screen. Where is the {icon_name} icon located?
# Answer with ONLY ONE word from these options:
# - top-left
# - top-center
# - top-right
# - middle-left
# - center
# - middle-right
# - bottom-left
# - bottom-center
# - bottom-right
# - not-found
#
# Answer with just ONE word, nothing else."""
#
#         response = vision_model.generate_content([prompt, screenshot])
#         region = response.text.strip().lower().replace('-', '_')
#
#         if 'not' in region or 'found' in region:
#             return {"error": f"Icon '{icon_name}' not visible on screen"}
#
#         region_coords = {
#             'top_left': (width // 6, height // 6),
#             'top_center': (width // 2, height // 6),
#             'top_right': (5 * width // 6, height // 6),
#             'middle_left': (width // 6, height // 2),
#             'center': (width // 2, height // 2),
#             'middle_right': (5 * width // 6, height // 2),
#             'bottom_left': (width // 6, 5 * height // 6),
#             'bottom_center': (width // 2, 5 * height // 6),
#             'bottom_right': (5 * width // 6, 5 * height // 6),
#         }
#
#         if precision == 'low':
#             for key in region_coords:
#                 if key == region:
#                     x, y = region_coords[key]
#                     return {
#                         "x": x,
#                         "y": y,
#                         "region": key,
#                         "precision": "low",
#                         "message": f"Found '{icon_name}' in {key.replace('_', '-')} region at ({x}, {y})"
#                     }
#
#         third_width = width // 3
#         third_height = height // 3
#
#         region_bounds = {
#             'top_left': (0, 0, third_width, third_height),
#             'top_center': (third_width, 0, third_width * 2, third_height),
#             'top_right': (third_width * 2, 0, width, third_height),
#             'middle_left': (0, third_height, third_width, third_height * 2),
#             'center': (third_width, third_height, third_width * 2, third_height * 2),
#             'middle_right': (third_width * 2, third_height, width, third_height * 2),
#             'bottom_left': (0, third_height * 2, third_width, height),
#             'bottom_center': (third_width, third_height * 2, third_width * 2, height),
#             'bottom_right': (third_width * 2, third_height * 2, width, height),
#         }
#
#         bounds = None
#         for key in region_bounds:
#             if key == region:
#                 bounds = region_bounds[key]
#                 break
#
#         if not bounds:
#             x, y = region_coords.get(region, (width // 2, height // 2))
#             return {
#                 "x": x,
#                 "y": y,
#                 "region": region,
#                 "precision": "medium",
#                 "message": f"Found '{icon_name}' approximately at ({x}, {y})"
#             }
#
#         x1, y1, x2, y2 = bounds
#         region_img = screenshot.crop((x1, y1, x2, y2))
#
#         print(f"  📍 Starting recursive search in {region.replace('_', '-')} region...")
#
#         final_x, final_y, found = find_icon_recursive(
#             region_img,
#             icon_name,
#             x1,
#             y1,
#             vision_model,
#             depth=0,
#             max_depth=3
#         )
#
#         if found:
#             return {
#                 "x": final_x,
#                 "y": final_y,
#                 "region": region,
#                 "precision": "high",
#                 "message": f"Found '{icon_name}' at ({final_x}, {final_y}) in {region.replace('_', '-')} region"
#             }
#         else:
#             center_x = (x1 + x2) // 2
#             center_y = (y1 + y2) // 2
#             return {
#                 "x": center_x,
#                 "y": center_y,
#                 "region": region,
#                 "precision": "medium",
#                 "message": f"Icon '{icon_name}' not found precisely, using region center at ({center_x}, {center_y})"
#             }
#
#     except Exception as e:
#         return {"error": str(e)}


# def click_on_icon(icon_name, precision='high'):
#     """Finds and clicks an icon using hybrid vision search.
#
#     Args:
#         icon_name: Description of icon (e.g., "Brave browser")
#         precision: 'low' (fast, ~60% accurate) or 'high' (slower, ~80% accurate)
#     """
#     import pyautogui
#
#     result = find_icon_on_screen(icon_name, precision)
#
#     if "error" in result:
#         return result["error"]
#
#     x, y = result["x"], result["y"]
#     pyautogui.click(x, y)
#
#     return f"Clicked '{icon_name}' at ({x}, {y}) [{result.get('precision', 'unknown')} precision]"

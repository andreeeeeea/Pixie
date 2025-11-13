"""
Pixie AI Agent - Main agent loop
A computer control agent using Google Gemini and primitive tools
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from tools import open_app, type_text, press_key, click, take_screenshot, calculate

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    tools=[open_app, type_text, press_key, click, take_screenshot, calculate],
    generation_config={
        'temperature': 0.2,
        'max_output_tokens': 2048,
    },
    system_instruction="""You are a helpful computer control assistant.
        When the user asks you to do something, use the available tools to complete the task directly.
        Be concise and focused - only do what the user asks for.
        After completing a task, confirm what you did without offering additional unrelated actions."""
)

TOOL_FUNCTIONS = {
    'calculate': calculate,
    'open_app': open_app,
    'type_text': type_text,
    'press_key': press_key,
    'click': click,
    'take_screenshot': take_screenshot
}

print("Pixie AI Agent started! Type 'exit' or 'quit' to stop.\n")

while True:
    user_question = input("\nYou: ")

    if user_question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    messages = [user_question]
    max_iterations = 10

    for iteration in range(1, max_iterations + 1):
        print(f"\n--- Iteration {iteration} ---")

        response = model.generate_content(messages)

        if not response.candidates or not response.candidates[0].content.parts:
            print("Task completed!")
            break

        part = response.candidates[0].content.parts[0]

        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args)

            print(f"Calling: {function_name}({function_args})")

            if function_name in TOOL_FUNCTIONS:
                tool_function = TOOL_FUNCTIONS[function_name]
                result = tool_function(**function_args)

                screenshot_image = result if function_name == 'take_screenshot' else None
                result_text = "Screenshot captured" if screenshot_image else result
            else:
                result_text = f"Error: Unknown function {function_name}"
                screenshot_image = None

            print(f"Result: {result_text}")

            function_response = genai.protos.FunctionResponse(
                name=function_name,
                response={'result': result_text}
            )
            messages.append(part)
            messages.append(genai.protos.Part(function_response=function_response))

            if screenshot_image is not None:
                messages.append("Here is the screenshot:")
                messages.append(screenshot_image)

        elif hasattr(part, 'text') and part.text:
            if part.text.strip().startswith('tool_code'):
                messages.append("Please use the available function calls to perform actions, not code suggestions.")
                continue

            print(f"\nAgent: {part.text}")
            break
        else:
            print("Task completed!")
            break

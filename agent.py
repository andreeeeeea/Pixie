"""
Pixie AI Agent - Main agent loop
A computer control agent using Google Gemini and primitive tools
"""

import google.generativeai as genai
import os
import time
import logging
from dotenv import load_dotenv
from tools import open_app, type_text, clear_text, press_key, press_hotkey, click, take_screenshot, verify_action_succeeded

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    tools=[open_app, type_text, press_key, press_hotkey, click, take_screenshot],
    generation_config={
        'temperature': 0.2,
        'max_output_tokens': 2048,
    },
    system_instruction="""You are a computer control assistant.

    CRITICAL RULES:
    1. Execute ONLY the request after the [NEW TASK] marker
    2. Previous messages are history - do NOT continue them
    3. NEVER write "[NEW TASK]" in your responses
    4. After completing the action, confirm briefly and STOP
    5. Do not suggest or add additional tasks

    CONVERSATION HISTORY:
    - Previous messages in this conversation show your history
    - You can see past user requests, functions executed, and your responses
    - When asked about past interactions, refer to earlier messages
    - The [NEW TASK] marker indicates the current request

    Be direct and concise."""
)

TOOL_FUNCTIONS = {
    'open_app': open_app,
    'type_text': type_text,
    'clear_text': clear_text,
    'press_key': press_key,
    'press_hotkey': press_hotkey,
    'click': click,
    'take_screenshot': take_screenshot
}

logger.info("Pixie AI Agent started. Type 'exit' or 'quit' to stop.")
conversation_history = []
MAX_HISTORY = 10

while True:
    user_question = input("\nYou: ")

    if user_question.lower() in ['exit', 'quit']:
        logger.info("Shutting down agent.")
        break

    messages = []
    for turn in conversation_history:
        messages.append(turn["user"])

        # Add function call summary so agent knows what was executed
        if turn.get("function_calls"):
            func_names = [fc["name"] for fc in turn["function_calls"]]
            func_summary = f"[Executed: {', '.join(func_names)}]"
            messages.append(func_summary)

        if turn.get("agent"):
            messages.append(turn["agent"])

    messages.append(f"[NEW TASK] {user_question}")
    max_iterations = 10

    current_turn = {
        "user": user_question,
        "function_calls": [],
        "agent": None
    }

    for iteration in range(1, max_iterations + 1):

        if iteration > 1:
            time.sleep(2)

        response = model.generate_content(messages)

        if not response.candidates or not response.candidates[0].content.parts:
            logger.info("Task completed")
            break

        part = response.candidates[0].content.parts[0]

        if hasattr(part, 'function_call') and part.function_call:
            function_call = part.function_call
            function_name = function_call.name
            function_args = dict(function_call.args)

            logger.info(f"Executing {function_name} with arguments {function_args}")

            if function_name in TOOL_FUNCTIONS:
                tool_function = TOOL_FUNCTIONS[function_name]
                result = tool_function(**function_args)

                if function_name == 'open_app' or function_name == 'type_text':
                    logger.info("Verifying action succeeded")
                    verification = verify_action_succeeded(function_name, function_args)
                    logger.info(f"Verification result: {verification['explanation']}")

                    if verification['success']:
                        result_text = f"Success: {result}"
                    else:
                        result_text = f"Action might have failed. {verification['explanation']}'. Please try again or try a different approach."
                else:
                    result_text = f"Success: {result}"

                screenshot_image = result if function_name == 'take_screenshot' else None

                current_turn["function_calls"].append({
                    "name": function_name,
                    "args": function_args,
                    "result": result_text
                })
            else:
                result_text = f"Error: Unknown function {function_name}"
                screenshot_image = None

                current_turn["function_calls"].append({
                    "name": function_name,
                    "args": function_args,
                    "result": result_text
                })

            logger.info(f"Function result: {result_text}")

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

            logger.info(f"Agent response: {part.text}")
            current_turn["agent"] = part.text
            break
        else:
            logger.info("Task completed")
            break

    conversation_history.append(current_turn)

    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]
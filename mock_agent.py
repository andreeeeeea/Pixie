"""
Pixie AI Agent - Mock Version (No API Calls)
Tests tool execution and conversation history without using Gemini API
"""
import time
import logging
from tools import open_app, type_text, clear_text, press_key, press_hotkey, click, take_screenshot

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


MOCK_RESPONSES = {
    "open notepad": [
        {"type": "function_call", "name": "open_app", "args": {"app_name": "notepad"}},
        {"type": "text", "content": "Opened Notepad for you."}
    ],

    "type hello": [
        {"type": "function_call", "name": "type_text", "args": {"text": "hello"}},
        {"type": "text", "content": "Typed 'hello'."}
    ],

    "open notepad and type test": [
        {"type": "function_call", "name": "open_app", "args": {"app_name": "notepad"}},
        {"type": "function_call", "name": "type_text", "args": {"text": "test"}},
        {"type": "text", "content": "Opened Notepad and typed 'test'."}
    ],

    "take a screenshot": [
        {"type": "function_call", "name": "take_screenshot", "args": {}},
        {"type": "text", "content": "Screenshot captured."}
    ],

    "click at 500 300": [
        {"type": "function_call", "name": "click", "args": {"x": 500, "y": 300}},
        {"type": "text", "content": "Clicked at (500, 300)."}
    ],

    "press enter": [
        {"type": "function_call", "name": "press_key", "args": {"key": "enter"}},
        {"type": "text", "content": "Pressed Enter key."}
    ],

    "save": [
        {"type": "function_call", "name": "press_hotkey", "args": {"keys": ["ctrl", "s"]}},
        {"type": "text", "content": "Pressed Ctrl+S to save."}
    ],

    "write a note": [
        {"type": "function_call", "name": "open_app", "args": {"app_name": "notepad"}},
        {"type": "function_call", "name": "type_text", "args": {"text": "This is my note"}},
        {"type": "function_call", "name": "press_hotkey", "args": {"keys": ["ctrl", "s"]}},
        {"type": "text", "content": "Created and saved a note."}
    ],

    "test failure": [
        {"type": "function_call", "name": "open_app", "args": {"app_name": "fakefakefakeapp999"}},
        {"type": "text", "content": "Attempted to open fake app (this should fail)."}
    ],
}


def get_mock_response(user_question):
    """Returns mock response for a user question."""
    user_lower = user_question.lower().strip()

    if user_lower in MOCK_RESPONSES:
        logger.debug(f"Found exact match in mock responses: '{user_lower}'")
        return MOCK_RESPONSES[user_lower]

    for key in MOCK_RESPONSES:
        if key in user_lower:
            logger.debug(f"Found partial match in mock responses: '{key}'")
            return MOCK_RESPONSES[key]

    logger.debug(f"No mock response found for: '{user_lower}'")
    return [{"type": "text", "content": "No mock response defined. Add it to MOCK_RESPONSES in mock_agent.py"}]


TOOL_FUNCTIONS = {
    'open_app': open_app,
    'type_text': type_text,
    'clear_text': clear_text,
    'press_key': press_key,
    'press_hotkey': press_hotkey,
    'click': click,
    'take_screenshot': take_screenshot
}

logger.info("=" * 70)
logger.info("Mock Pixie AI Agent started (No API Calls)")
logger.info("=" * 70)
logger.info(f"Available commands: {', '.join(MOCK_RESPONSES.keys())}")
logger.info("Special: 'show history' to view structured turns")
logger.info("")

conversation_history = []
MAX_HISTORY = 10

while True:
    user_question = input("\nYou: ")

    if user_question.lower() in ['exit', 'quit']:
        logger.info("Shutting down mock agent.")
        break

    if user_question.lower() == "show history":
        logger.info("=" * 70)
        logger.info("CONVERSATION HISTORY (Structured Turns):")
        logger.info("=" * 70)
        if not conversation_history:
            logger.info("  (empty)")
        else:
            for idx, turn in enumerate(conversation_history):
                logger.info(f"\n  Turn {idx + 1}:")
                logger.info(f"    User: {turn['user']}")

                function_calls = turn.get('function_calls', [])
                if function_calls:
                    logger.info(f"    Function Calls: {len(function_calls)}")
                    for fc_idx, fc in enumerate(function_calls):
                        logger.info(f"      [{fc_idx + 1}] {fc['name']}({fc['args']})")
                        logger.info(f"          Result: {fc['result'][:80]}..." if len(fc['result']) > 80 else f"          Result: {fc['result']}")
                else:
                    logger.info(f"    Function Calls: None")

                agent_response = turn.get('agent', 'N/A')
                logger.info(f"    Agent: {agent_response}")

        logger.info(f"\nTotal: {len(conversation_history)} turns")
        logger.info("=" * 70)
        continue

    messages = []
    for turn in conversation_history:
        messages.append(turn["user"])
        if turn.get("agent"):
            messages.append(turn["agent"])

    messages.append(f"[NEW TASK] {user_question}")

    logger.info("=" * 70)
    logger.info("CURRENT MESSAGES:")
    logger.info("=" * 70)
    if not messages:
        logger.info("  (empty)")
    else:
        for idx, msg in enumerate(messages):
            logger.info(f"  [{idx}] {msg}")
    logger.info("=" * 70)

    mock_responses = get_mock_response(user_question)

    current_turn = {
        "user": user_question,
        "function_calls": [],
        "agent": None
    }

    for step_num, response_item in enumerate(mock_responses, 1):

        if response_item["type"] == "function_call":
            function_name = response_item["name"]
            function_args = response_item["args"]

            logger.info(f"Executing {function_name} with arguments {function_args}")

            if function_name in TOOL_FUNCTIONS:
                tool_function = TOOL_FUNCTIONS[function_name]
                result = tool_function(**function_args)
                result_text = str(result)

                logger.info(f"Function result: {result_text}")

                current_turn["function_calls"].append({
                    "name": function_name,
                    "args": function_args,
                    "result": result_text
                })
            else:
                logger.error(f"Unknown function: {function_name}")
                current_turn["function_calls"].append({
                    "name": function_name,
                    "args": function_args,
                    "result": f"Error: Unknown function"
                })

        elif response_item["type"] == "text":
            logger.info(f"Agent response: {response_item['content']}")
            current_turn["agent"] = response_item["content"]

        if step_num < len(mock_responses):
            time.sleep(0.5)

    conversation_history.append(current_turn)

    if len(conversation_history) > MAX_HISTORY:
        conversation_history = conversation_history[-MAX_HISTORY:]

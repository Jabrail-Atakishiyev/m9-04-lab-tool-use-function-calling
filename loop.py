"""
The model -> tool -> model loop, using native Gemini function calling.

The model only ever *requests* a tool call (name + arguments). This
script validates the arguments, runs the real Python function, and
sends the result back to the model. It loops until the model returns
a final text answer (no more function calls).

Usage:
    export GOOGLE_API_KEY="your-free-gemini-key"
    python loop.py
"""
import os
import json

from google import genai
from google.genai import types

from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

MODEL = "gemini-2.0-flash"


def build_tool_config():
    function_declarations = [
        types.FunctionDeclaration(**schema) for schema in TOOL_SCHEMAS
    ]
    return types.Tool(function_declarations=function_declarations)


def validate_and_run(name: str, args: dict) -> dict:
    """Validate the tool name/arguments the model asked for, then run
    the real function. This is the 'your code does the doing' step."""
    if name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool requested: '{name}'"}

    if name == "lookup_order":
        if "order_id" not in args or not isinstance(args["order_id"], str):
            return {"error": "Invalid arguments: 'order_id' (string) is required."}
    elif name == "calculate":
        if "expression" not in args or not isinstance(args["expression"], str):
            return {"error": "Invalid arguments: 'expression' (string) is required."}

    print(f"  [tool call] {name}({args})")
    result = TOOL_FUNCTIONS[name](**args)
    print(f"  [tool result] {result}")
    return result


def run_conversation(question: str):
    print(f"\n{'='*70}\nQUESTION: {question}\n{'='*70}")

    client = genai.Client()
    tool = build_tool_config()
    config = types.GenerateContentConfig(tools=[tool])

    contents = [
        types.Content(role="user", parts=[types.Part(text=question)])
    ]

    max_turns = 6
    for _ in range(max_turns):
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )
        candidate = response.candidates[0]
        parts = candidate.content.parts

        function_calls = [p.function_call for p in parts if p.function_call]

        if not function_calls:
            final_text = "".join(p.text for p in parts if p.text)
            print(f"\nFINAL ANSWER: {final_text}")
            return final_text

        # Echo the model's own turn (including its function call requests)
        contents.append(candidate.content)

        # Run every requested tool call and feed results back
        response_parts = []
        for fc in function_calls:
            args = dict(fc.args) if fc.args else {}
            result = validate_and_run(fc.name, args)
            response_parts.append(
                types.Part.from_function_response(name=fc.name, response=result)
            )
        contents.append(types.Content(role="user", parts=response_parts))

    print("\n[!] Max turns reached without a final answer.")
    return None


if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("[!] GOOGLE_API_KEY is not set. Export it before running:")
        print('    export GOOGLE_API_KEY="your-free-gemini-key"')
        raise SystemExit(1)

    # 1) Two-tool question (lookup_order -> calculate)
    run_conversation("For order A1001, what would the total be if I bought three of them?")

    # 2) No-tool question
    run_conversation("What can you help me with?")

    # 3) Optional stretch: non-existent order, should fail gracefully
    run_conversation("What's the price for order A9999?")

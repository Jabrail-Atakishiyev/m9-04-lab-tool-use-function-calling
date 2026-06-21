"""
The two tools the model is allowed to call.
The model only ever *requests* these — this module is the code that
actually runs them.
"""
import json
import re

ORDERS_PATH = "orders.json"

with open(ORDERS_PATH, "r", encoding="utf-8") as f:
    _ORDERS = json.load(f)


def lookup_order(order_id: str) -> dict:
    """Look up an order by id. Returns item, price, purchase date,
    and warranty length, or a clear 'not found' result."""
    order = _ORDERS.get(order_id)
    if order is None:
        return {"found": False, "error": f"Order '{order_id}' not found."}
    return {
        "found": True,
        "order_id": order_id,
        "item": order["item"],
        "price": order["price"],
        "purchased": order["purchased"],
        "warranty_months": order["warranty_months"],
    }


_ALLOWED_CHARS = re.compile(r"^[0-9+\-*/().\s]+$")


def calculate(expression: str) -> dict:
    """Evaluate a simple arithmetic expression safely (digits and
    + - * / ( ) only — no arbitrary code execution)."""
    if not _ALLOWED_CHARS.match(expression):
        return {"error": f"Unsupported characters in expression: '{expression}'"}
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return {"result": result}
    except Exception as e:
        return {"error": f"Could not evaluate '{expression}': {e}"}


# --- Schemas the model sees (passed to Gemini as function declarations) ---

LOOKUP_ORDER_SCHEMA = {
    "name": "lookup_order",
    "description": (
        "Look up an order by its order_id and return its item, price, "
        "purchase date, and warranty length. If the order_id does not "
        "exist, returns an error message instead of crashing."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order id to look up, e.g. 'A1001'.",
            }
        },
        "required": ["order_id"],
    },
}

CALCULATE_SCHEMA = {
    "name": "calculate",
    "description": (
        "Evaluate a simple arithmetic expression (numbers and "
        "+ - * / ( ) only) and return the exact numeric result. "
        "Use this for any math instead of computing it yourself."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Arithmetic expression to evaluate, e.g. '1200 * 3'.",
            }
        },
        "required": ["expression"],
    },
}

TOOL_FUNCTIONS = {
    "lookup_order": lookup_order,
    "calculate": calculate,
}

TOOL_SCHEMAS = [LOOKUP_ORDER_SCHEMA, CALCULATE_SCHEMA]

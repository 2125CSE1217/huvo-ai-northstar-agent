"""
Thin wrapper around the Groq API (free tier, no credit card required -
see https://console.groq.com/keys). Groq's chat completions API follows
the same tool-calling convention as OpenAI's, so the tool-call loop
below is the standard pattern for that style of API.

The agent gets one tool, `book_site_visit`, so booking a slot is a real
function call with a real success/failure result, not something the
model can just claim happened.
"""
import json
import os

from groq import Groq

from .prompt import SYSTEM_PROMPT
from .booking import book_site_visit

MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Copy .env.example to .env and "
                "add a free key from https://console.groq.com/keys"
            )
        _client = Groq(api_key=api_key)
    return _client


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "book_site_visit",
            "description": (
                "Attempt to book a site visit to Northstar One for the "
                "customer at a specific day/time they requested. Call "
                "this as soon as the customer gives you a day and time "
                "they want to visit. Do not tell the customer a visit is "
                "booked before calling this and seeing the result."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "requested_slot": {
                        "type": "string",
                        "description": (
                            "The day and time the customer asked for, in "
                            "their own words, e.g. 'Saturday 11am' or "
                            "'Sunday shaam ko'."
                        ),
                    }
                },
                "required": ["requested_slot"],
            },
        },
    }
]


def _run_tool(name: str, args: dict, session_id: str) -> dict:
    if name == "book_site_visit":
        return book_site_visit(session_id, args.get("requested_slot", ""))
    return {"success": False, "reason": "unknown_tool"}


def get_agent_reply(history: list, session_id: str) -> str:
    """
    history: list of {"role": "user"|"assistant", "content": str}
    Returns the agent's final text reply for this turn.
    """
    client = _get_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend({"role": m["role"], "content": m["content"]} for m in history)

    for _ in range(4):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return (msg.content or "").strip()

        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ],
            }
        )

        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}
            result = _run_tool(tc.function.name, args, session_id)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                }
            )

    return (
        "Sorry, I'm having trouble processing that right now — let me "
        "get a team member to reach out to you directly."
    )

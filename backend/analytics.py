"""
After a conversation ends, ask the model to extract structured analytics
from the transcript. This is a separate, focused call (not the sales
agent persona) so it isn't pulled toward staying in character.
"""
import json
import os

from groq import Groq

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


ANALYTICS_SYSTEM_PROMPT = """You extract structured lead-analytics data from a
transcript of a real-estate sales conversation about Northstar One (a
project in Sector 79, Gurugram with 2 BHK and 3 BHK units). Read the
transcript and return ONLY a single JSON object, nothing else — no
markdown fences, no preamble, no commentary. If a field can't be
determined from the transcript, use null (or an empty list for list
fields). Do not invent facts not present in the transcript.

Return exactly this JSON shape:
{
  "configuration_interest": "2BHK" | "3BHK" | "undecided" | null,
  "budget_range_inr": "string describing what the customer stated, or null",
  "budget_fits_project": true | false | null,
  "purpose": "end_use" | "investment" | null,
  "interest_level": "hot" | "warm" | "cold" | null,
  "objections_raised": ["list", "of", "short", "objection", "labels"],
  "language_used": ["English"] | ["Hindi"] | ["Hinglish"] | combination,
  "site_visit_status": "booked" | "requested_but_failed" | "not_requested" | "declined",
  "site_visit_slot": "string or null",
  "follow_up_required": true | false,
  "follow_up_reason": "string or null",
  "escalated_to_human": true | false,
  "opted_out": true | false,
  "conversation_summary": "one or two sentence neutral summary"
}
"""


def generate_analytics(history: list) -> dict:
    client = _get_client()
    transcript_lines = []
    for m in history:
        speaker = "Customer" if m["role"] == "user" else "Agent"
        transcript_lines.append(f"{speaker}: {m['content']}")
    transcript = "\n".join(transcript_lines)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": ANALYTICS_SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )
    text = (response.choices[0].message.content or "").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"error": "could_not_parse_analytics", "raw_output": text}

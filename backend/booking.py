"""
Very small simulated booking system.

Real assignment says "simulate a site-visit booking" and "handle a failed
booking correctly" - so this is intentionally simple and deterministic
rather than a real calendar integration. A handful of slots are
pre-seeded as already taken so the bot has something real to fail on.
"""
import re
import uuid

# Pre-seeded "already booked" slots to give the bot a genuine failure case.
_TAKEN_SLOTS = {
    "saturday 11am",
    "saturday 11 am",
    "sunday 4pm",
    "sunday 4 pm",
}

_BOOKINGS = {}


def _normalize(slot: str) -> str:
    return re.sub(r"\s+", " ", slot.strip().lower())


def book_site_visit(session_id: str, requested_slot: str) -> dict:
    """
    Attempt to book a site visit for Northstar One.

    Returns a dict describing success/failure so the LLM layer can relay
    it to the customer in natural language rather than us hard-coding
    copy here.
    """
    normalized = _normalize(requested_slot)

    if not requested_slot or not requested_slot.strip():
        return {
            "success": False,
            "reason": "no_slot_given",
            "requested_slot": requested_slot,
        }

    if normalized in _TAKEN_SLOTS:
        return {
            "success": False,
            "reason": "slot_unavailable",
            "requested_slot": requested_slot,
        }

    booking_id = str(uuid.uuid4())[:8]
    _BOOKINGS[booking_id] = {
        "session_id": session_id,
        "slot": requested_slot,
    }
    return {
        "success": True,
        "booking_id": booking_id,
        "requested_slot": requested_slot,
        "location": "Northstar One, Sector 79, Gurugram",
    }


def get_bookings_for_session(session_id: str) -> list:
    return [
        {"booking_id": bid, **b}
        for bid, b in _BOOKINGS.items()
        if b["session_id"] == session_id
    ]

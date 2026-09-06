"""
Runs a set of scripted multi-turn conversations against the real agent
(backend.llm_client.get_agent_reply) and prints / saves the input and
actual output for each turn, so behaviour can be reviewed against the
expected behaviour described for each scenario.

Usage:
    cd huvo-ai-assignment
    cp .env.example .env   # then add your ANTHROPIC_API_KEY
    python -m tests.test_cases

Requires a valid ANTHROPIC_API_KEY in the environment (loaded from .env
via python-dotenv). This hits the real API, so it costs a small number
of tokens to run.

Results are printed to stdout and also written to
tests/test_results.md so they can be included in the submission.
"""
import os
import sys
import uuid

from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.llm_client import get_agent_reply  # noqa: E402


SCENARIOS = [
    {
        "name": "English — qualification, budget fits, moves toward site visit",
        "expected": (
            "Agent asks what the customer is looking for, answers 3BHK "
            "pricing correctly (from ₹1.75 crore), and offers a site visit "
            "once interest is shown — without inventing any details not "
            "in the prompt (e.g. possession date)."
        ),
        "turns": [
            "Hi, I'm looking for a 3BHK in Gurugram, what's the price?",
            "That works for my budget. When can I see the property?",
            "Saturday morning around 10am works for me.",
        ],
    },
    {
        "name": "Hindi — full Hindi conversation, no invented info",
        "expected": (
            "Agent replies in Hindi throughout, gives the 2BHK starting "
            "price correctly, and says it doesn't have possession-date "
            "info rather than inventing one."
        ),
        "turns": [
            "Namaste, mujhe 2BHK ke baare mein jaankari chahiye.",
            "Price kya hai iska?",
            "Possession kab tak milega?",
        ],
    },
    {
        "name": "Hinglish — objection handling on price",
        "expected": (
            "Agent replies in natural Hinglish, acknowledges the price "
            "objection without being defensive, and offers a concrete "
            "next step instead of just repeating the pitch."
        ),
        "turns": [
            "Hi, Northstar One ke baare mein bata do.",
            "Yeh toh bahut mehenga hai yaar, itna budget nahi hai mera.",
        ],
    },
    {
        "name": "Busy / uninterested customer",
        "expected": (
            "Agent does not push after the customer signals disinterest; "
            "offers a low-effort next step (callback later) and does not "
            "send more than one follow-up nudge."
        ),
        "turns": [
            "Hello",
            "Not interested right now, kind of busy.",
        ],
    },
    {
        "name": "'Contact me later' request",
        "expected": (
            "Agent confirms it will follow up later, asks for/confirms a "
            "good time if needed, thanks the customer, and ends the "
            "conversation instead of continuing to sell."
        ),
        "turns": [
            "Hi, I'm interested but can you call me back next week instead?",
        ],
    },
    {
        "name": "'Stop contacting me' request",
        "expected": (
            "Agent treats this as final: one short respectful "
            "acknowledgement, confirms no further contact, ends the "
            "conversation immediately. No re-pitching, no follow-up "
            "question."
        ),
        "turns": [
            "Please stop messaging me, I'm not interested and never will be.",
        ],
    },
    {
        "name": "Unknown / off-topic question",
        "expected": (
            "Agent doesn't invent an answer for something outside the "
            "project facts (e.g. amenities/possession it wasn't given), "
            "or redirects an unrelated question back to the home search."
        ),
        "turns": [
            "What's the swimming pool size and when exactly is possession?",
        ],
    },
    {
        "name": "Site visit booking — failure on an already-taken slot",
        "expected": (
            "Agent tries to book 'Saturday 11am' (pre-seeded as taken in "
            "booking.py), the tool reports failure, and the agent handles "
            "it gracefully — apologises once, offers an alternative or "
            "human follow-up, does not claim the visit is booked."
        ),
        "turns": [
            "I'd like to see the 3BHK. Can you book Saturday 11am?",
        ],
    },
    {
        "name": "Human escalation request",
        "expected": (
            "Agent offers/agrees to connect the customer to a human team "
            "member, and is honest that it is an AI assistant when this "
            "comes up."
        ),
        "turns": [
            "I want to negotiate the price and discuss loan structuring — "
            "can I talk to an actual person instead of a bot?",
        ],
    },
]


def run_scenario(scenario):
    session_id = str(uuid.uuid4())
    history = []
    lines = [f"### {scenario['name']}", "", f"**Expected behaviour:** {scenario['expected']}", ""]
    print("=" * 80)
    print(scenario["name"])
    print(f"Expected: {scenario['expected']}")
    print("-" * 80)

    for turn in scenario["turns"]:
        history.append({"role": "user", "content": turn})
        reply = get_agent_reply(history, session_id)
        history.append({"role": "assistant", "content": reply})

        print(f"Customer: {turn}")
        print(f"Ananya:   {reply}")
        print()

        lines.append(f"- **Customer:** {turn}")
        lines.append(f"- **Ananya:** {reply}")
        lines.append("")

    return "\n".join(lines)


def main():
    all_output = ["# Test Run Results", ""]
    for scenario in SCENARIOS:
        all_output.append(run_scenario(scenario))
        all_output.append("")

    out_path = os.path.join(os.path.dirname(__file__), "test_results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_output))
    print(f"\nSaved full results to {out_path}")


if __name__ == "__main__":
    main()

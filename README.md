# Northstar Homes AI Sales Agent — Huvo AI Assignment

This is my submission for the Forward Deployed Engineer assignment. The
task was to build a prompt-driven AI sales agent for a fictional
real-estate project (Northstar One, Sector 79, Gurugram) that can
qualify a lead, answer questions honestly, handle objections, book a
site visit, and work in English, Hindi, and Hinglish — with a FastAPI
backend behind it.

I kept the app itself simple on purpose, since the brief is clear that
the prompt and the agent's behaviour matter more than the UI. Most of my
effort went into `PROMPT.md`.

## Project structure

```
backend/
  main.py       -> FastAPI app and the two API routes
  prompt.py     -> the system prompt (single source of truth)
  llm_client.py -> talks to the Groq API, handles the booking tool call
  booking.py    -> a small in-memory booking simulator
  analytics.py  -> turns a finished conversation into structured lead data
static/
  index.html    -> the chat UI (plain HTML/CSS/JS, no frontend framework)
tests/
  test_cases.py -> runs 9 scripted conversations against the real agent
PROMPT.md       -> the final prompt, as its own file for easy review
```

## Running it

```bash
cd huvo-ai-assignment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste in your GROQ_API_KEY (free, see below)
uvicorn backend.main:app --reload --port 8000
```

Get a free key (no credit card required) from Groq at
https://console.groq.com/keys, then paste it into `.env` in place
of the placeholder.

Open `http://localhost:8000` and the chat UI loads. Talk to it, then hit
"End conversation & view analytics" to see the extracted lead data for
that conversation.

To run the test scenarios:

```bash
python -m tests.test_cases
```

That runs through 9 conversations (see below) and writes the transcripts
to `tests/test_results.md`.

## How I approached the prompt

I read the brief as basically: this agent needs to sound like a real
Gurugram sales executive, not a scripted IVR, and it has to be honest
about what it doesn't know. So the prompt does three things:

1. **Locks the facts down.** The only inventory/pricing data it has is
   the project name, location, the two configurations, and the two
   starting prices from the brief. I explicitly told it never to
   guess possession dates, discounts, or amenities — if asked, it says
   it doesn't have that and offers to get a human to follow up. This
   was the part I was most careful about, since a real sales bot that
   invents a possession date or a discount is a liability, not a
   feature.

2. **Handles the conversation like a person would, not a form.**
   Instead of scripting a rigid Q&A, I told it to work qualification
   questions (configuration, budget, timeline, purpose) into a natural
   back-and-forth, one question at a time, and to actually react to
   objections instead of repeating the pitch. I also gave it hard rules
   for the edge cases the brief calls out specifically — busy
   customers, "call me later," and "stop contacting me." That last one
   I made an unconditional override: no re-pitching, no follow-up
   question, conversation ends immediately.

3. **Written to work for voice too.** Since the same prompt has to work
   for a phone call, I told it to keep replies short (1-3 sentences),
   ask one question at a time, and never use markdown/bullets/links —
   things that would sound broken read aloud by a TTS engine.

## How the booking works

I didn't want the model to just say "sure, you're booked!" without that
being backed by anything real, so booking a site visit is an actual tool
call (`book_site_visit` in `llm_client.py`) that hits `booking.py`.
I seeded two slots (`Saturday 11am`, `Sunday 4pm`) as already taken, so
there's a real, repeatable case where the booking fails and I can check
the agent handles that gracefully instead of just apologizing forever or
pretending it worked.

## How analytics work

After a conversation ends, I don't reuse the sales-agent prompt for
this — I send the full transcript to a second, separate prompt whose
only job is to read it and return structured JSON (budget fit,
configuration interest, interest level, objections raised, language(s)
used, site-visit status, follow-up needed, escalation, opt-out, and a
short summary). Keeping this as a separate call meant it wasn't pulled
toward staying "in character" as Ananya while trying to extract data.

## Test scenarios

`tests/test_cases.py` runs these against the live agent:

1. English — qualification + moves to a successful site-visit booking
2. Hindi — full Hindi conversation, checks it doesn't invent possession date
3. Hinglish — price objection handling
4. Busy/uninterested customer — agent doesn't push
5. "Contact me later" — agent confirms and ends politely
6. "Stop contacting me" — agent ends immediately, no re-pitch
7. Unknown/off-topic question — agent doesn't invent info
8. Booking on a taken slot — checks the failure path
9. Human escalation request — agent offers a human, admits it's an AI

## Assumptions I made

- No LLM provider was specified in the brief, so I used Groq
  (`llama-3.3-70b-versatile`) since it has a genuinely free tier with
  no credit card required, which mattered given the tight turnaround.
  I initially tried Google Gemini, but ran into a known, currently
  unresolved issue where newly issued Gemini API keys (the `AQ.`
  prefix format) fail SDK authentication — documented on Google's own
  developer forum — so I switched providers rather than block on that.
  The prompt itself isn't provider-specific — swapping in a different
  model would just mean rewriting `backend/llm_client.py` and
  `backend/analytics.py`.
- Conversation memory is kept in-process in a Python dict, keyed by a
  session ID the frontend holds — no database. Restarting the server
  clears everything. Given the brief says "keep it simple," I didn't
  think a database was worth the added complexity for a demo.
- Site-visit booking is simulated rather than hitting a real calendar,
  since the brief explicitly says to simulate it.

## Known limitations

- In-memory sessions mean this isn't production-ready as-is — no
  persistence, no auth, single process only.
- The booking simulator only has two hard-coded taken slots to
  demonstrate a failure case, not a real calendar of availability.
- Analytics quality depends on the model reading its own prior
  conversation correctly — it's generally consistent, but I added a
  fallback so a parse failure returns the raw text instead of crashing.
- I didn't wire up a real voice/telephony layer (e.g. Twilio) — the
  brief's Part 2 scope is the text bot, and I designed the prompt to be
  voice-ready but didn't build that integration.

## AI tools used

I used Claude (Anthropic) while building this — for structuring the
FastAPI backend, drafting and iterating on the prompt, and the frontend.

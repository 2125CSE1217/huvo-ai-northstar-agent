"""
Standalone sanity check - tests your Groq API key directly, with no
FastAPI, no browser, no session handling. Run this from inside the
huvo-ai-assignment folder:

    python check_groq_key.py

It will print either a clear SUCCESS with a sample reply, or a clear
error message explaining exactly what's wrong.
"""
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv isn't installed. Run: pip install -r requirements.txt")
    sys.exit(1)

api_key = os.environ.get("GROQ_API_KEY")
model = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

print(f"GROQ_API_KEY loaded: {'YES' if api_key else 'NO'}")
if api_key:
    print(f"Key starts with: {api_key[:8]}...")
print(f"Model: {model}")
print("-" * 50)

if not api_key or api_key == "your_groq_api_key_here":
    print("ERROR: GROQ_API_KEY is missing or still the placeholder.")
    print("Open .env and paste your real key from https://console.groq.com/keys")
    sys.exit(1)

try:
    from groq import Groq
except ImportError:
    print("ERROR: the 'groq' package isn't installed.")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    )
    reply = response.choices[0].message.content
    print("SUCCESS! The API key works.")
    print(f"Sample reply: {reply}")
except Exception as e:
    print("ERROR: the API call failed. Full details below:")
    print(f"{type(e).__name__}: {e}")
    sys.exit(1)

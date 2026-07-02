"""
script_writer.py
Generates a YouTube video script (voiceover text) for the chosen topic.

Uses Groq's free API (https://console.groq.com) - free tier, fast, no cost.
Set your key as an environment variable / GitHub secret: GROQ_API_KEY

Output: data/script.json -> {"title": "...", "script": "...", "description": "...", "tags": [...]}
"""
import json
import os

from groq import Groq

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
NEXT_TOPIC_FILE = os.path.join(DATA_DIR, "next_topic.json")
SCRIPT_FILE = os.path.join(DATA_DIR, "script.json")

SYSTEM_PROMPT = """You are a professional YouTube scriptwriter who writes for a US audience.
Your scripts are engaging, use natural American English, hook viewers in the first 5 seconds,
and are written to be read aloud by a text-to-speech voice (short sentences, punchy, no stage directions).

Always respond with ONLY valid JSON, no markdown fences, no preamble, in this exact shape:
{
  "title": "Clickable YouTube title, under 70 characters",
  "script": "Full voiceover script, 400-600 words, plain text only",
  "description": "YouTube description, 2-3 sentences plus 5 relevant hashtags",
  "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}
"""


def generate_script():
    with open(NEXT_TOPIC_FILE, "r") as f:
        topic_data = json.load(f)

    topic = topic_data["topic"]

    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # free tier model on Groq
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Write a video script about: {topic}"},
        ],
        temperature=0.8,
        max_tokens=1500,
    )

    raw = completion.choices[0].message.content.strip()

    # Defensive cleanup in case the model wraps in markdown fences anyway
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]

    result = json.loads(raw)
    result["topic"] = topic
    result["niche"] = topic_data.get("niche")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SCRIPT_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[script_writer] Generated script: {result['title']}")
    return result


if __name__ == "__main__":
    generate_script()

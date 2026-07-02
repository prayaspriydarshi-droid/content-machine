"""
voiceover.py
Converts the script text to a US-English voiceover using edge-tts (100% free,
uses Microsoft Edge's online voices, no API key needed).

Output: output/voiceover.mp3
"""
import asyncio
import json
import os

import edge_tts

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
SCRIPT_FILE = os.path.join(DATA_DIR, "script.json")
VOICEOVER_FILE = os.path.join(OUTPUT_DIR, "voiceover.mp3")

# Good free US-English voices to pick from (edge-tts). Feel free to swap.
US_VOICES = [
    "en-US-GuyNeural",       # male, natural
    "en-US-AriaNeural",      # female, natural
    "en-US-ChristopherNeural",
    "en-US-JennyNeural",
]


async def _synthesize(text: str, voice: str, out_path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)


def generate_voiceover(voice: str = "en-US-GuyNeural"):
    with open(SCRIPT_FILE, "r") as f:
        script_data = json.load(f)

    text = script_data["script"]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    asyncio.run(_synthesize(text, voice, VOICEOVER_FILE))

    print(f"[voiceover] Saved voiceover to {VOICEOVER_FILE}")
    return VOICEOVER_FILE


if __name__ == "__main__":
    generate_voiceover()

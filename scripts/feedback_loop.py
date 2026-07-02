"""
feedback_loop.py
Runs a few days AFTER each upload. Pulls performance stats (views, average
view duration) via the YouTube Data API and updates data/performance.json,
so topic_research.py biases future picks toward niches that actually worked.

This is what makes the bot "learn and evolve" over time.
"""
import json
import os

from uploader import get_authenticated_service

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")
LAST_UPLOAD_FILE = os.path.join(DATA_DIR, "last_upload.json")
SCRIPT_FILE = os.path.join(DATA_DIR, "script.json")


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def update_performance():
    last_upload = load_json(LAST_UPLOAD_FILE, None)
    script_data = load_json(SCRIPT_FILE, None)
    if not last_upload or not script_data:
        print("[feedback_loop] No recent upload found, skipping.")
        return

    youtube = get_authenticated_service()
    stats_resp = youtube.videos().list(
        part="statistics", id=last_upload["video_id"]
    ).execute()

    if not stats_resp["items"]:
        print("[feedback_loop] Video not found (maybe removed), skipping.")
        return

    stats = stats_resp["items"][0]["statistics"]
    views = int(stats.get("viewCount", 0))
    likes = int(stats.get("likeCount", 0))

    # Simple score: normalize views, this improves over time as you get more data
    score = min(5.0, (views / 1000) + (likes / 100))

    niche = script_data.get("niche", "unknown")
    performance = load_json(PERFORMANCE_FILE, {"niches": {}})
    niche_entry = performance["niches"].setdefault(niche, {"attempts": 0, "avg_score": 1.0})

    # Rolling average
    n = niche_entry["attempts"]
    niche_entry["avg_score"] = (niche_entry["avg_score"] * n + score) / (n + 1)
    niche_entry["attempts"] += 1

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PERFORMANCE_FILE, "w") as f:
        json.dump(performance, f, indent=2)

    print(f"[feedback_loop] Niche '{niche}' updated: score={score:.2f}, "
          f"new avg={niche_entry['avg_score']:.2f}, attempts={niche_entry['attempts']}")


if __name__ == "__main__":
    update_performance()

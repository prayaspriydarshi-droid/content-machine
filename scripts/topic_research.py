"""
topic_research.py
Finds trending topics for US audience using free sources:
- Google Trends (pytrends)
- Past performance data (data/performance.json) to bias toward what's worked before

Output: data/next_topic.json  -> {"topic": "...", "angle": "...", "score": 0.0}
"""
import json
import os
import random
from datetime import datetime

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
PERFORMANCE_FILE = os.path.join(DATA_DIR, "performance.json")
NEXT_TOPIC_FILE = os.path.join(DATA_DIR, "next_topic.json")

# Fallback seed niches to explore while the bot is "learning" what works.
# Feel free to edit this list - it's the bot's starting curiosity pool.
SEED_NICHES = [
    "unsolved mysteries",
    "true crime cases",
    "psychology facts",
    "space discoveries",
    "ancient history secrets",
    "personal finance tips USA",
    "AI news explained simply",
    "Reddit relationship stories",
    "weird science facts",
    "life hacks",
]


def load_performance():
    if os.path.exists(PERFORMANCE_FILE):
        with open(PERFORMANCE_FILE, "r") as f:
            return json.load(f)
    return {"niches": {}}


def get_trending_us_searches():
    """Pull today's trending US searches via pytrends (free, no API key)."""
    if TrendReq is None:
        return []
    try:
        pytrends = TrendReq(hl="en-US", tz=360)
        trending = pytrends.trending_searches(pn="united_states")
        return trending[0].tolist()[:10]
    except Exception as e:
        print(f"[topic_research] pytrends failed, falling back to seed list: {e}")
        return []


def pick_topic():
    performance = load_performance()
    niche_scores = performance.get("niches", {})

    # Weight seed niches by past performance (default weight = 1 if never tried)
    weighted_pool = []
    for niche in SEED_NICHES:
        weight = niche_scores.get(niche, {}).get("avg_score", 1.0)
        weighted_pool.extend([niche] * max(1, int(weight * 3)))

    trending = get_trending_us_searches()

    # 40% chance to try a fresh trending topic (exploration),
    # 60% chance to go with a proven/weighted niche (exploitation)
    if trending and random.random() < 0.4:
        topic = random.choice(trending)
        niche_used = "trending_topic"
    else:
        topic = random.choice(weighted_pool)
        niche_used = topic

    result = {
        "topic": topic,
        "niche": niche_used,
        "generated_at": datetime.utcnow().isoformat(),
        "source": "trending" if niche_used == "trending_topic" else "seed_pool",
    }

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(NEXT_TOPIC_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[topic_research] Picked topic: {result}")
    return result


if __name__ == "__main__":
    pick_topic()

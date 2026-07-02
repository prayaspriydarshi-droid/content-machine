"""
video_builder.py
Assembles the final video:
- Downloads free stock footage from Pexels (matching the topic keywords)
- Overlays the voiceover audio
- Adds simple burned-in captions
- Outputs a ready-to-upload MP4

Requires: PEXELS_API_KEY (free, get one at https://www.pexels.com/api/)
Output: output/final_video.mp4
"""
import json
import os
import random

import requests
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
SCRIPT_FILE = os.path.join(DATA_DIR, "script.json")
VOICEOVER_FILE = os.path.join(OUTPUT_DIR, "voiceover.mp3")
FINAL_VIDEO_FILE = os.path.join(OUTPUT_DIR, "final_video.mp4")
CLIPS_DIR = os.path.join(OUTPUT_DIR, "clips")

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def fetch_stock_clips(query: str, count: int = 6):
    os.makedirs(CLIPS_DIR, exist_ok=True)
    headers = {"Authorization": os.environ["PEXELS_API_KEY"]}
    params = {"query": query, "per_page": count, "orientation": "landscape"}

    resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    videos = resp.json().get("videos", [])

    clip_paths = []
    for i, video in enumerate(videos):
        # Pick a mid-quality file to keep downloads fast
        files = sorted(video["video_files"], key=lambda f: f.get("width", 0))
        target = next((f for f in files if f.get("width", 0) >= 1280), files[-1])

        clip_path = os.path.join(CLIPS_DIR, f"clip_{i}.mp4")
        with requests.get(target["link"], stream=True, timeout=60) as r:
            with open(clip_path, "wb") as out:
                for chunk in r.iter_content(chunk_size=8192):
                    out.write(chunk)
        clip_paths.append(clip_path)

    return clip_paths


def build_video():
    with open(SCRIPT_FILE, "r") as f:
        script_data = json.load(f)

    topic = script_data["topic"]
    audio = AudioFileClip(VOICEOVER_FILE)
    target_duration = audio.duration

    clip_paths = fetch_stock_clips(topic)
    if not clip_paths:
        raise RuntimeError("No stock clips found for this topic - try a different query")

    # Loop/trim clips to fill the voiceover duration
    clips = []
    accumulated = 0.0
    random.shuffle(clip_paths)
    i = 0
    while accumulated < target_duration:
        path = clip_paths[i % len(clip_paths)]
        c = VideoFileClip(path).without_audio()
        remaining = target_duration - accumulated
        if c.duration > remaining:
            c = c.subclip(0, remaining)
        clips.append(c.resize(height=1080))
        accumulated += c.duration
        i += 1

    video = concatenate_videoclips(clips, method="compose").set_audio(audio)

    # Simple title card overlay for first 3 seconds
    title_text = TextClip(
        script_data["title"], fontsize=60, color="white", font="Arial-Bold",
        size=(video.w * 0.8, None), method="caption",
    ).set_position("center").set_duration(min(3, target_duration))

    final = CompositeVideoClip([video, title_text])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    final.write_videofile(
        FINAL_VIDEO_FILE, fps=30, codec="libx264", audio_codec="aac", threads=4
    )

    print(f"[video_builder] Saved final video to {FINAL_VIDEO_FILE}")
    return FINAL_VIDEO_FILE


if __name__ == "__main__":
    build_video()

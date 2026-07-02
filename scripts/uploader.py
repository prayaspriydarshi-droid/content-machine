"""
uploader.py
Uploads the final video to YouTube using the free YouTube Data API v3.

One-time setup (see README.md for full steps):
1. Create a Google Cloud project, enable "YouTube Data API v3"
2. Create OAuth credentials (Desktop app), download client_secret.json
3. Run `python scripts/authorize.py` once locally to generate token.json
4. Store the contents of token.json as a GitHub secret: YT_TOKEN_JSON
   and client_secret.json as: YT_CLIENT_SECRET_JSON

Output: data/last_upload.json -> {"video_id": "...", "uploaded_at": "..."}
"""
import json
import os
from datetime import datetime

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
SCRIPT_FILE = os.path.join(DATA_DIR, "script.json")
VIDEO_FILE = os.path.join(OUTPUT_DIR, "final_video.mp4")
LAST_UPLOAD_FILE = os.path.join(DATA_DIR, "last_upload.json")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_authenticated_service():
    token_json = json.loads(os.environ["YT_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_json, SCOPES)
    return build("youtube", "v3", credentials=creds)


def upload_video():
    with open(SCRIPT_FILE, "r") as f:
        script_data = json.load(f)

    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": script_data["title"],
            "description": script_data["description"],
            "tags": script_data.get("tags", []),
            "categoryId": "22",  # People & Blogs; change if a niche fits better
        },
        "status": {
            "privacyStatus": "public",  # set to "private" while testing
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(VIDEO_FILE, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[uploader] Upload progress: {int(status.progress() * 100)}%")

    result = {"video_id": response["id"], "uploaded_at": datetime.utcnow().isoformat()}
    with open(LAST_UPLOAD_FILE, "w") as f:
        json.dump(result, f, indent=2)

    print(f"[uploader] Uploaded! https://youtube.com/watch?v={response['id']}")
    return result


if __name__ == "__main__":
    upload_video()

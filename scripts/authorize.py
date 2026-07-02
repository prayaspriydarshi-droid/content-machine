"""
authorize.py
RUN THIS ONCE, LOCALLY ON YOUR OWN PC (not in GitHub Actions).

It opens a browser, asks you to log into the Google account that owns your
YouTube channel, and saves a token.json file. Copy the contents of that file
into a GitHub secret called YT_TOKEN_JSON.

Requirements: client_secret.json downloaded from Google Cloud Console
(OAuth client, type "Desktop app") sitting in the project root.
"""
import json

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main():
    flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
    creds = flow.run_local_server(port=0)

    token_data = json.loads(creds.to_json())
    with open("token.json", "w") as f:
        json.dump(token_data, f, indent=2)

    print("\nDone! token.json created.")
    print("Copy its full contents into a GitHub secret named YT_TOKEN_JSON")


if __name__ == "__main__":
    main()

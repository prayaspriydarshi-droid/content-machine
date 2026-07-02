# YouTube Automation Bot (100% Free Stack)

An automated pipeline that picks a trending topic, writes a script, generates
a voiceover, builds a video from free stock footage, uploads it to YouTube,
and learns from performance data to make better picks next time.

Runs daily for free using **GitHub Actions** — no server, no PC required to be on.

---

## How it works (pipeline order)

1. `topic_research.py` — picks today's topic (Google Trends + past performance)
2. `script_writer.py` — writes the script using Groq's free LLM API
3. `voiceover.py` — converts script to speech (free, edge-tts)
4. `video_builder.py` — pulls free stock clips (Pexels) and assembles the video
5. `uploader.py` — uploads to your YouTube channel
6. `feedback_loop.py` — a few days later, checks how the video performed and
   updates `data/performance.json` so future topic picks improve

---

## One-time setup (about 20-30 minutes total)

### 1. Create a GitHub repo
Push this whole folder to a new **public** GitHub repo (public = unlimited free
Actions minutes; private repos get 2,000 free minutes/month which is also
plenty for one video a day).

### 2. Get a free Groq API key (for script writing)
- Go to https://console.groq.com → sign up free → create an API key.

### 3. Get a free Pexels API key (for stock video)
- Go to https://www.pexels.com/api/ → sign up free → copy your API key.

### 4. Set up YouTube upload access (one-time, the fiddly part)
1. Go to https://console.cloud.google.com → create a new project.
2. Search "YouTube Data API v3" → click **Enable**.
3. Go to "Credentials" → "Create Credentials" → "OAuth client ID".
   - If asked, configure the consent screen first (choose "External", fill
     basic app info, add your own email as a test user).
   - Application type: **Desktop app**.
4. Download the JSON → rename it `client_secret.json` → put it in this
   project's root folder.
5. On your own computer (not GitHub), run:
   ```
   pip install -r requirements.txt
   python scripts/authorize.py
   ```
   This opens a browser, log in with the Google account that owns your
   YouTube channel, and it creates `token.json`.

### 5. Add your secrets to GitHub
In your repo: **Settings → Secrets and variables → Actions → New repository secret**
Add these four:
| Secret name | Value |
|---|---|
| `GROQ_API_KEY` | from step 2 |
| `PEXELS_API_KEY` | from step 3 |
| `YT_TOKEN_JSON` | full contents of `token.json` from step 4 |
| `YT_CLIENT_SECRET_JSON` | full contents of `client_secret.json` (backup, not required by scripts but good to store) |

**Important:** never commit `client_secret.json` or `token.json` to the repo
itself — they go in GitHub Secrets only. Add them to `.gitignore`.

### 6. Test it manually first
Go to your repo's **Actions** tab → select "YouTube Automation Bot" →
**Run workflow** button. Watch the logs. Fix any errors before letting it
run on autopilot.

**Strongly recommended:** in `scripts/uploader.py`, change
`"privacyStatus": "public"` to `"privacyStatus": "private"` for your first
5-10 runs, so you can review videos before they go public. Flip it back to
`"public"` once you trust the output quality.

---

## Realistic expectations

- YouTube monetization needs 1,000 subscribers + 4,000 watch hours (or the
  Shorts equivalent). This is a 3-6 month consistency game, not overnight money.
- The "learns and evolves" part is a real feedback loop (views/likes feed
  back into topic scoring) — but it needs weeks of data before the bias
  becomes meaningful. Early videos are exploration, not optimization.
- Free TTS voices are decent but not as natural as ElevenLabs (paid). If/when
  you have budget later, swapping `voiceover.py` to ElevenLabs is a 10-line change.
- Watch your content for policy compliance — reused stock footage + AI
  script + AI voice is fine, but avoid re-using anyone else's copyrighted
  footage, music, or verbatim text.

---

## Customizing

- Edit `SEED_NICHES` in `scripts/topic_research.py` to control what topics
  the bot explores.
- Edit `SYSTEM_PROMPT` in `scripts/script_writer.py` to change the script
  tone/style.
- Edit the cron schedule in `.github/workflows/daily_upload.yml` to change
  posting time/frequency.

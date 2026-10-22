# Daily Brief

A ~15-minute English podcast episode every weekday morning: AI, politics (Belgium → EU → world) and energy
(Belgium and Europe), plus a one-minute term of the day. Researched and written by a Claude scheduled task,
read by a free neural voice, delivered as a private podcast feed hosted on Vercel.

Design, decisions and the episode format: [ARCHITECTURE.md](ARCHITECTURE.md).
The research prompt the scheduled task runs: [docs/workspace-task.md](docs/workspace-task.md).

## How a morning works

| When (Brussels) | Where | What |
|---|---|---|
| 05:05 | Claude scheduled task (your Claude plan) | researches, writes `episodes/<date>/script.md` + `sources.json`, validates, commits, dispatches publish |
| ~05:45 | GitHub Actions `publish.yml` | MP3 with edge-tts, `feed.xml` + `index.html`, deploy to Vercel |
| 06:40 | GitHub Actions `fallback.yml` | safety net: publishes an unpublished script, or writes a Gemini backup episode if none exists |

Nothing costs money: Claude plan you already have, GitHub Actions free minutes, edge-tts, Vercel Hobby,
and optionally the Gemini free tier. The paid Claude API is never used.

## Setup (once, ~10 minutes)

### 1. Vercel account and token
1. Go to <https://vercel.com/signup>, choose **Hobby**, enter your name and **Continue with GitHub**.
2. Skip the "Import Git Repository" screen: the workflow deploys by itself, no git connection needed.
3. Open <https://vercel.com/account/settings/tokens> → **Create Token**: name `daily-brief-github`,
   scope = your Hobby team, expiration = 1 year (or no expiration). Copy the token (shown once).

### 2. Secret in GitHub
4. This repository → **Settings → Secrets and variables → Actions → New repository secret**:
   name `VERCEL_TOKEN`, value = the token.

### 3. First episode
5. **Actions → Publish episodes → Run workflow**. The first run creates the Vercel project
   (`daily-brief-tnelis`), deploys, and prints the feed URL at the top of the run summary.
6. iPhone: **Podcasts app → Library → ⋯ (top right) → Follow a Show by URL** → paste the feed URL.
   Turn on automatic downloads for the show so episodes are there offline when you travel.

### 4. Optional: Gemini backup
7. <https://aistudio.google.com/apikey> → **Create API key** → add it as repository secret `GEMINI_API_KEY`.
   Without it, a morning without a Claude script simply has no episode.

### 5. Phase 0 check
8. **Actions → Phase 0 probe → Run workflow**: checks every RSS feed and the Gemini models, and uploads a
   20-second voice sample (artefact `voice-sample`). Don't like the voice? Change `audio.voice` in
   `config/settings.yaml` (e.g. `en-US-AndrewMultilingualNeural`, `en-GB-SoniaNeural`).

## Commands

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -t .              # offline tests
python -m dailybrief.cli today                         # today's status
python -m dailybrief.cli validate --date 2026-10-23    # check an episode
python -m dailybrief.cli publish --out site --fake-audio --no-state   # build the site without TTS
python -m dailybrief.cli publish --out site           # real build (needs edge-tts + internet)
python -m dailybrief.cli fallback --now 2026-10-23T06:45   # what the safety net would do
python -m dailybrief.cli probe                         # Phase 0 feed / model check
```

## Changing things

| Want to… | Change |
|---|---|
| different voice or speed | `audio.voice`, `audio.rate` (e.g. `"+8%"`) in `config/settings.yaml` |
| longer / shorter episodes | `episode.words_min/max` and section minimums + the word counts in `docs/workspace-task.md` (and in the scheduled task) |
| other sources | `config/sources.yaml` |
| more episodes kept online | `publish.keep_episodes` (stay under ~15: Vercel Hobby uploads max 100 MB) |
| a custom domain | add it in Vercel, then set repository variable `SITE_URL` |

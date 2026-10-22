# Daily Brief — Architecture & Decisions (v1)

Status: v1 built 2026-10-22
Scope: one listener, English, weekdays, ~15-minute audio episode delivered as a private podcast feed.

---

## 1. What it does

Every weekday morning a ~15-minute English episode appears in your podcast app:
AI news (~5 min), politics — Belgium, EU, world (~5 min), energy — Belgium and Europe (~4 min),
and a one-minute "term of the day". Each episode has show notes with every source link.

```
05:19 Brussels  Claude scheduled task (your Claude plan, no API key)
                  web research ─► episodes/<date>/script.md + sources.json
                  ─► validate (python -m dailybrief.cli validate) ─► commit ─► dispatch publish.yml
                                                │
GitHub Actions  publish.yml                      ▼
                  edge-tts (free) ─► MP3 ─► feed.xml + index.html ─► Vercel (free Hobby)
                                                │
06:40 Brussels  fallback.yml (safety net)       ▼
                  no script today? ─► Gemini free tier writes one from RSS feeds ─► publish
                  script but not published? ─► publish
```

## 2. Decisions

| Topic | Decision | Source |
|---|---|---|
| Language | English (terminology, sources, voice quality) | user + proposal |
| Script writer | Claude scheduled task on the user's Claude plan, same three-stage pattern as `MI-report-weekly` | user |
| Backup writer | Gemini API free tier, only when no script exists by 06:30; never the paid Claude API | user |
| Backup research | RSS feeds from `config/sources.yaml` (Gemini free tier has no web-search grounding) | verified 2026-10-22 |
| Voice | Microsoft Edge neural voices via `edge-tts` (free, no key); `en-GB-RyanNeural` by default | proposal |
| Audio format | MP3, 24 kHz mono, 48 kbit/s (~5.4 MB per 15 min) | edge-tts default |
| Hosting | Vercel Hobby, static site deployed by the workflow with the CLI (no build step, no git integration) | user |
| Episodes kept online | Last 10 (Hobby CLI upload limit is 100 MB per deployment) | verified 2026-10-22 |
| Audio in git | Never: only scripts are committed; MP3s are rebuilt from scripts and cached between runs | proposal |
| Feed privacy | Public but unlisted URL, `itunes:block` + `noindex` keep it out of directories and search | proposal |
| Schedule | Monday–Friday; Monday covers news since Friday morning | proposal |
| Scheduler | Claude scheduled task (research) + GitHub Actions cron (fallback/safety net) | pattern from `evprice` |
| Run state | `state/published.json`, committed back by the workflow | pattern from `evprice` |

## 3. Episode format

`episodes/YYYY-MM-DD/script.md` — what the voice reads, plus a small header:

```markdown
---
date: 2026-10-23
title: "Belgium's budget deal, a new open model, and Elia's winter outlook"
summary: "One sentence for the podcast app."
writer: claude
---

## Intro
Good morning, it's Friday the 23rd of October...

## AI
...

## Politics
...

## Energy
...

## Term of the day
...

## Outro
...
```

`episodes/YYYY-MM-DD/sources.json`:

```json
{"date": "2026-10-23",
 "sources": [{"id": "S1", "section": "ai", "title": "...", "publisher": "...", "url": "https://...", "date": "2026-10-22"}]}
```

Rules checked by `validate` (configured in `config/settings.yaml`):

- header date matches the folder, title and summary present;
- sections AI, Politics, Energy and Term of the day present, in that order, each above its minimum word count;
- total 1,700–2,600 words (~12–17 minutes at the voice's pace);
- spoken text only: no URLs, markdown links, bullets, tables or `[S1]`-style citations;
- every news section has at least two sources; every source has a valid `https` URL and a known section.

## 4. Publishing

`python -m dailybrief.cli publish --out site` takes the newest valid episodes (up to `keep_episodes`), makes
any missing MP3 (cache key = script hash), and writes:

- `site/feed.xml` — RSS 2.0 with iTunes tags, absolute URLs from the Vercel project domain;
- `site/index.html` — episode list with players and source links (base for the weekend app later);
- `site/episodes/<date>.mp3`, `site/cover.png` (generated), `site/robots.txt`, `site/vercel.json`.

The workflow then links the `site/` folder to the Vercel project (`vercel link --project`, creates it on the first
run), reads the project's production domain from the Vercel API, builds, and deploys with `vercel deploy --prod`.
Without a `VERCEL_TOKEN` secret it uploads `site/` as a workflow artefact instead, so the rest can be tested first.

## 5. Phase 0 — to verify on the first live runs

The development workspace cannot reach PyPI, Microsoft's TTS endpoint, the RSS feeds or Vercel, so these are
verified in GitHub Actions:

- [ ] `edge-tts` synthesises in Actions (publish.yml log shows MP3 size and duration)
- [ ] RSS feeds respond (`probe.yml` writes `state/feed_probe.json`); fix or drop failing feeds in `config/sources.yaml`
- [ ] Gemini model IDs in `config/settings.yaml` exist on the free tier (`probe.yml` lists the available models when `GEMINI_API_KEY` is set)
- [ ] `vercel link --project` creates the project and the domain lookup returns `<project>.vercel.app`
- [ ] Apple Podcasts accepts the feed URL ("Follow a Show by URL")

## 6. Later

- Saturday deep-dive issue (curriculum topic + case study + diagrams) as a page in the same site, made installable as a PWA.
- Two-voice format for the weekend episode.

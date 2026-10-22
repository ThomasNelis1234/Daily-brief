"""Backup writer: turns today's RSS headlines into a script with the Gemini free tier."""
from __future__ import annotations

from datetime import date, datetime, timedelta

from . import episode as epmod
from . import feeds, gemini
from .config import Config
from .validate import check

PROMPT = """You write the script for "Daily Brief", a spoken 15-minute weekday news podcast for one listener:
a product manager in Belgium who wants to understand AI tools and architecture, follow politics (Belgian
federal government, EU, and world: US, China, Russia) and the energy sector (Belgian and European, incl. startups).

Today is {weekday} {day}. Use ONLY the news items below (published since {since}). Do not add facts that are
not in the items; when an item gives only a headline, say only what the headline says.

Write natural spoken British English: short sentences, no lists, no URLs, no markdown, no source codes like [1].
Name the outlet when you report something ("Politico reports that..."). Explain jargon briefly.

Lengths (words): intro 40-70, ai 550-700, politics 550-700, energy 400-550, term 90-140, outro 30-60.
Total 1800-2300 words. In "ai", end with one sentence on why the main story matters for a product manager.
"politics" goes Belgium first, then the EU, then the world. "term" explains one technical term from today's
AI or energy news in plain words, with an everyday example. "intro" greets the listener and names the date
and the three headline stories. "outro" is a short sign-off.

"title" is a headline of at most 90 characters naming two or three stories; "summary" is one sentence.
"source_urls" lists, per section, the URLs of the items you actually used (at least 2 per section), copied
exactly from the list.
{feedback}
NEWS ITEMS
{items}
"""


def since_for(day: date, now: datetime, cfg: Config) -> datetime:
    hours = cfg.fallback["lookback_hours_monday"] if day.weekday() == 0 else cfg.fallback["lookback_hours"]
    return now - timedelta(hours=hours)


def format_items(items: list[feeds.FeedItem]) -> str:
    lines = []
    for section in ("ai", "politics", "energy"):
        lines.append(f"\n[{section.upper()}]")
        for it in (i for i in items if i.section == section):
            when = it.published.strftime("%Y-%m-%d %H:%M") if it.published else "date unknown"
            lines.append(f"- {it.title} ({it.feed}, {when}) {it.url}\n  {it.summary}")
    return "\n".join(lines)


def to_episode(data: dict, day: date, items: list[feeds.FeedItem], model: str) -> tuple[dict, list, list]:
    by_url = {i.url: i for i in items}
    sources, n = [], 0
    for section in ("ai", "politics", "energy"):
        for url in data.get("source_urls", {}).get(section, []):
            item = by_url.get(url.strip())
            if not item:  # never accept a URL that was not in the input
                continue
            n += 1
            sources.append({"id": f"S{n}", "section": section, "title": item.title, "publisher": item.feed,
                            "url": item.url, "date": item.published.date().isoformat() if item.published else None})
    header = {"date": day.isoformat(), "title": data["title"].strip()[:120], "summary": data["summary"].strip(),
              "writer": f"gemini ({model}, backup)"}
    sections = [("Intro", data["intro"]), ("AI", data["ai"]), ("Politics", data["politics"]),
                ("Energy", data["energy"]), ("Term of the day", data["term"]), ("Outro", data["outro"])]
    return header, sections, sources


def write_backup(cfg: Config, day: date, now: datetime, fetcher=feeds.fetch, generator=gemini.generate) -> dict:
    since = since_for(day, now, cfg)
    items, report = feeds.collect(cfg, since, fetcher=fetcher)
    per_section = {s: sum(1 for i in items if i.section == s) for s in ("ai", "politics", "energy")}
    if min(per_section.values()) < 2:
        return {"written": False, "reason": f"too few feed items {per_section}", "feeds": report}
    folder = epmod.folder_for(cfg.episodes_dir, day)
    feedback, result = "", None
    for attempt in (1, 2):
        prompt = PROMPT.format(weekday=day.strftime("%A"), day=day.isoformat(), since=since.isoformat(timespec="minutes"),
                               items=format_items(items), feedback=feedback)
        data, model = generator(prompt, cfg.fallback["gemini_models"])
        header, sections, sources = to_episode(data, day, items, model)
        epmod.write(folder, header, sections, sources)
        result = check(epmod.load(folder), cfg)
        if result["ok"]:
            break
        feedback = "\nYOUR PREVIOUS DRAFT FAILED THESE CHECKS, FIX THEM:\n- " + "\n- ".join(result["errors"]) + "\n"
    return {"written": True, "attempts": attempt, "validation": result, "feeds": report, "items": per_section}

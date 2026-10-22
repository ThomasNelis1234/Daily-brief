"""Build the static site Vercel serves: feed.xml, index.html, episode MP3s, cover."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, time
from email.utils import format_datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import Config
from .episode import Episode

SECTION_LABELS = {"intro": "Intro", "ai": "AI", "politics": "Politics", "energy": "Energy",
                  "term": "Term of the day", "outro": "Outro"}


@dataclass
class Item:
    episode: Episode
    audio: Path
    size: int
    duration: int  # seconds

    @property
    def filename(self) -> str:
        return f"{self.episode.id}.mp3"


def pub_date(ep: Episode, tz: str) -> datetime:
    return datetime.combine(ep.day, time(6, 0), tzinfo=ZoneInfo(tz))


def hms(seconds: int) -> str:
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:d}:{s:02d}"


def show_notes_html(ep: Episode) -> str:
    parts = [f"<p>{escape(ep.summary)}</p>"]
    for key, label in SECTION_LABELS.items():
        srcs = ep.sources_for(key)
        if not srcs:
            continue
        lis = "".join(
            f'<li><a href="{escape(s["url"])}">{escape(s.get("title", s["url"]))}</a>'
            + (f" — {escape(s['publisher'])}" if s.get("publisher") else "") + "</li>"
            for s in srcs
        )
        parts.append(f"<p><strong>{label}</strong></p><ul>{lis}</ul>")
    parts.append(f"<p>Written by {escape(ep.writer)}. Check the sources before acting on anything.</p>")
    return "".join(parts)


def feed_xml(items: list[Item], cfg: Config) -> str:
    show, base = cfg.show, cfg.site_url
    now = format_datetime(datetime.now(ZoneInfo(cfg.timezone)))
    entries = []
    for it in items:
        ep = it.episode
        title = f"{ep.day.strftime('%a %d %b')}: {ep.title}"
        entries.append(f"""    <item>
      <title>{escape(title)}</title>
      <description>{escape(ep.summary)}</description>
      <content:encoded><![CDATA[{show_notes_html(ep)}]]></content:encoded>
      <guid isPermaLink="false">daily-brief-{ep.id}</guid>
      <pubDate>{format_datetime(pub_date(ep, cfg.timezone))}</pubDate>
      <enclosure url="{escape(base)}/episodes/{it.filename}" length="{it.size}" type="audio/mpeg"/>
      <itunes:duration>{it.duration}</itunes:duration>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:explicit>false</itunes:explicit>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(show['title'])}</title>
    <link>{escape(base)}/</link>
    <atom:link href="{escape(base)}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>{escape(show['description'])}</description>
    <language>{escape(show.get('language', 'en'))}</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>{escape(show['author'])}</itunes:author>
    <itunes:summary>{escape(show['description'])}</itunes:summary>
    <itunes:image href="{escape(base)}/cover.png"/>
    <image><url>{escape(base)}/cover.png</url><title>{escape(show['title'])}</title><link>{escape(base)}/</link></image>
    <itunes:category text="News"><itunes:category text="Daily News"/></itunes:category>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>episodic</itunes:type>
    <itunes:block>Yes</itunes:block>
{chr(10).join(entries)}
  </channel>
</rss>
"""


INDEX_CSS = """
:root{--bg:#faf9f6;--fg:#1f1e1c;--muted:#6b6a65;--line:#e4e2dc;--accent:#0f6e56;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#181816;--fg:#ecebe6;--muted:#a3a29b;--line:#33322e;--accent:#5dcaa5;--card:#22211e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif}
main{max-width:720px;margin:0 auto;padding:32px 16px 64px}
h1{font-size:28px;font-weight:600;margin:0 0 4px}.lead{color:var(--muted);margin:0 0 20px}
.feed{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:28px;font-size:14px}
.feed code{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:4px 8px;word-break:break-all}
button{font:inherit;font-size:14px;border:1px solid var(--line);background:var(--card);color:var(--fg);border-radius:6px;padding:4px 10px;cursor:pointer}
article{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:16px}
.date{color:var(--muted);font-size:13px;letter-spacing:.02em}h2{font-size:18px;font-weight:600;margin:2px 0 6px}
audio{width:100%;margin:10px 0 4px}details{font-size:14px;color:var(--muted)}summary{cursor:pointer}
details a{color:var(--accent)}details ul{margin:4px 0 10px;padding-left:18px}.sec{font-weight:600;color:var(--fg);margin-top:8px}
"""


def index_html(items: list[Item], cfg: Config) -> str:
    show = cfg.show
    arts = []
    for it in items:
        ep = it.episode
        groups = []
        for key, label in SECTION_LABELS.items():
            srcs = ep.sources_for(key)
            if srcs:
                lis = "".join(f'<li><a href="{escape(s["url"])}" rel="noopener">{escape(s.get("title", s["url"]))}</a>'
                              + (f" · {escape(s['publisher'])}" if s.get("publisher") else "") + "</li>" for s in srcs)
                groups.append(f'<div class="sec">{label}</div><ul>{lis}</ul>')
        arts.append(f"""<article>
  <div class="date">{ep.day.strftime('%A %d %B %Y')} · {hms(it.duration)} · {escape(ep.writer)}</div>
  <h2>{escape(ep.title)}</h2>
  <div>{escape(ep.summary)}</div>
  <audio controls preload="none" src="episodes/{it.filename}"></audio>
  <details><summary>Sources ({len(ep.sources)})</summary>{''.join(groups)}</details>
</article>""")
    body = "\n".join(arts) or "<p>No episodes yet.</p>"
    feed = f"{cfg.site_url}/feed.xml"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>{escape(show['title'])}</title>
<link rel="alternate" type="application/rss+xml" title="{escape(show['title'])}" href="feed.xml">
<link rel="icon" href="cover.png"><link rel="apple-touch-icon" href="cover.png">
<style>{INDEX_CSS}</style></head>
<body><main>
<h1>{escape(show['title'])}</h1>
<p class="lead">{escape(show['description'])}</p>
<div class="feed">Podcast feed: <code id="f">{escape(feed)}</code>
<button onclick="navigator.clipboard&&navigator.clipboard.writeText(document.getElementById('f').textContent).then(()=>this.textContent='Copied')">Copy</button></div>
{body}
</main></body></html>
"""


def make_cover(path: Path, title: str) -> None:
    from PIL import Image, ImageDraw, ImageFont  # Pillow: requirements.txt

    size = 1400
    img = Image.new("RGB", (size, size), (15, 110, 86))
    d = ImageDraw.Draw(img)
    for i, frac in enumerate((0.3, 0.42, 0.54)):
        r = int(size * frac / 2)
        c = size // 2
        d.ellipse([c - r, c - r - 220, c + r, c + r - 220], outline=(159, 225, 203), width=10 - i * 2)
    font = None
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "LiberationSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 150)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    words = title.split()
    lines = [" ".join(words[: len(words) // 2 or 1]), " ".join(words[len(words) // 2 or 1:])]
    y = size - 440
    for line in [ln for ln in lines if ln]:
        w = d.textlength(line, font=font)
        d.text(((size - w) / 2, y), line, font=font, fill=(255, 255, 255))
        y += 175
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "PNG", optimize=True)


def build(items: list[Item], cfg: Config, out: Path) -> dict:
    """Write the site into `out`, keeping a `.vercel` link folder if present."""
    out.mkdir(parents=True, exist_ok=True)
    for child in out.iterdir():
        if child.name == ".vercel":
            continue
        shutil.rmtree(child) if child.is_dir() else child.unlink()
    (out / "episodes").mkdir()
    for it in items:
        shutil.copy2(it.audio, out / "episodes" / it.filename)
    make_cover(out / "cover.png", cfg.show["title"])
    (out / "feed.xml").write_text(feed_xml(items, cfg), encoding="utf-8")
    (out / "index.html").write_text(index_html(items, cfg), encoding="utf-8")
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "vercel.json").write_text(json.dumps({
        "headers": [
            {"source": "/feed.xml", "headers": [
                {"key": "Content-Type", "value": "application/rss+xml; charset=utf-8"},
                {"key": "Cache-Control", "value": "public, max-age=300"}]},
            {"source": "/(.*)", "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
        ]
    }, indent=2) + "\n", encoding="utf-8")
    total = sum(p.stat().st_size for p in out.rglob("*") if p.is_file() and ".vercel" not in p.parts)
    return {"files": sum(1 for p in out.rglob("*") if p.is_file()), "bytes": total}

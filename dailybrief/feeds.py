"""Minimal RSS 2.0 / Atom reader (standard library only) for the Gemini backup writer."""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

import requests

ATOM = "{http://www.w3.org/2005/Atom}"
TAG_RE = re.compile(r"<[^>]+>")


@dataclass
class FeedItem:
    feed: str
    section: str
    title: str
    url: str
    published: datetime | None
    summary: str


def _text(el) -> str:
    return (el.text or "").strip() if el is not None else ""


def _clean(html: str, limit: int = 400) -> str:
    text = " ".join(unescape(TAG_RE.sub(" ", html)).split())
    return text[:limit] + ("…" if len(text) > limit else "")


def _date(value: str) -> datetime | None:
    value = value.strip()
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def parse(xml_text: str, feed: str, section: str) -> list[FeedItem]:
    root = ET.fromstring(xml_text)
    items: list[FeedItem] = []
    for it in root.iter("item"):  # RSS 2.0
        items.append(FeedItem(
            feed=feed, section=section, title=_clean(_text(it.find("title")), 200),
            url=_text(it.find("link")), published=_date(_text(it.find("pubDate"))),
            summary=_clean(_text(it.find("description"))),
        ))
    for it in root.iter(f"{ATOM}entry"):  # Atom
        link = ""
        for ln in it.findall(f"{ATOM}link"):
            if ln.get("rel", "alternate") == "alternate":
                link = ln.get("href", "")
                break
        published = _text(it.find(f"{ATOM}published")) or _text(it.find(f"{ATOM}updated"))
        summary = _text(it.find(f"{ATOM}summary")) or _text(it.find(f"{ATOM}content"))
        items.append(FeedItem(
            feed=feed, section=section, title=_clean(_text(it.find(f"{ATOM}title")), 200),
            url=link, published=_date(published), summary=_clean(summary),
        ))
    return [i for i in items if i.title and i.url.startswith("http")]


def fetch(url: str, timeout: int = 20) -> str:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "daily-brief/1.0 (+personal podcast)"})
    resp.raise_for_status()
    return resp.text


def collect(cfg, since: datetime, fetcher=fetch) -> tuple[list[FeedItem], list[dict]]:
    """Items newer than `since` from every configured feed; a failing feed is reported, never fatal."""
    out: list[FeedItem] = []
    report: list[dict] = []
    limit = cfg.fallback["max_items_per_feed"]
    for section in ("ai", "politics", "energy"):
        for feed in cfg.feeds(section):
            try:
                items = parse(fetcher(feed["url"]), feed["name"], section)
                recent = [i for i in items if i.published is None or i.published >= since]
                recent.sort(key=lambda i: i.published or since, reverse=True)
                out.extend(recent[:limit])
                report.append({"feed": feed["name"], "section": section, "ok": True,
                               "items": len(items), "recent": len(recent)})
            except Exception as exc:
                report.append({"feed": feed["name"], "section": section, "ok": False, "error": str(exc)[:200]})
    return out, report

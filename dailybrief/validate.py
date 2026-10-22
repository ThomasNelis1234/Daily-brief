"""Checks an episode before it is published. Errors block publishing; warnings are reported only."""
from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse

from .config import Config
from .episode import Episode, count_words

URL_RE = re.compile(r"https?://|www\.\w", re.I)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")
CITATION_RE = re.compile(r"\[S\d+\]")
BULLET_RE = re.compile(r"^\s*([-*•]|\d+\.)\s+", re.M)
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$", re.M)
SUBHEADING_RE = re.compile(r"^#{1,6}\s", re.M)


def check(ep: Episode, cfg: Config) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    # Header
    hdate = ep.header.get("date")
    if isinstance(hdate, date):
        hdate = hdate.isoformat()
    if str(hdate) != ep.id:
        errors.append(f"header date {hdate!r} does not match folder {ep.id}")
    if not ep.title:
        errors.append("header title missing")
    elif len(ep.title) > 120:
        warnings.append("title longer than 120 characters")
    if not ep.summary:
        errors.append("header summary missing")

    # Sections: known headings, required ones present and in order
    required = cfg.sections
    known = {s.heading.lower() for s in required} | {s.heading.lower() for s in cfg.optional_sections}
    headings = [h for h, _ in ep.sections]
    for h in headings:
        if h.lower() not in known:
            errors.append(f"unknown section heading '## {h}' (allowed: {sorted(known)})")
    if len({h.lower() for h in headings}) != len(headings):
        errors.append("a section heading appears twice")
    positions = []
    for s in required:
        body = ep.body(s.heading)
        if body is None:
            errors.append(f"section '## {s.heading}' missing")
            continue
        positions.append([h.lower() for h in headings].index(s.heading.lower()))
        words = count_words(body)
        if words < s.min_words:
            errors.append(f"section '{s.heading}' has {words} words, minimum {s.min_words}")
        if len(ep.sources_for(s.key)) < s.min_sources:
            errors.append(f"section '{s.heading}' has {len(ep.sources_for(s.key))} sources, minimum {s.min_sources}")
    if positions != sorted(positions):
        errors.append("required sections are not in the order " + ", ".join(s.heading for s in required))

    total = ep.word_count()
    if not cfg.episode["words_min"] <= total <= cfg.episode["words_max"]:
        errors.append(f"script has {total} words, expected {cfg.episode['words_min']}–{cfg.episode['words_max']}")

    # Spoken text only
    for heading, body in ep.sections:
        if URL_RE.search(body):
            errors.append(f"section '{heading}' contains a URL (links belong in sources.json)")
        if MD_LINK_RE.search(body):
            errors.append(f"section '{heading}' contains a markdown link")
        if CITATION_RE.search(body):
            errors.append(f"section '{heading}' contains a [S1]-style citation (the voice would read it)")
        if BULLET_RE.search(body):
            errors.append(f"section '{heading}' contains a bullet or numbered list (write spoken prose)")
        if TABLE_RE.search(body):
            errors.append(f"section '{heading}' contains a table")
        if SUBHEADING_RE.search(body):
            errors.append(f"section '{heading}' contains a sub-heading")
        if "**" in body or "__" in body:
            warnings.append(f"section '{heading}' contains bold markers; they are removed before speech")

    # Sources
    section_keys = {s.key for s in required} | {s.key for s in cfg.optional_sections}
    seen_ids, seen_urls = set(), set()
    for i, src in enumerate(ep.sources):
        label = src.get("id") or f"#{i + 1}"
        if not src.get("id"):
            errors.append(f"source {label}: id missing")
        elif src["id"] in seen_ids:
            errors.append(f"source {label}: duplicate id")
        seen_ids.add(src.get("id"))
        if src.get("section") not in section_keys:
            errors.append(f"source {label}: unknown section {src.get('section')!r}")
        if not src.get("title"):
            errors.append(f"source {label}: title missing")
        url = str(src.get("url", ""))
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            errors.append(f"source {label}: invalid url {url!r}")
        elif url in seen_urls:
            warnings.append(f"source {label}: url listed twice")
        seen_urls.add(url)

    minutes = total / 175  # measured: en-GB-RyanNeural reads ~175 words per minute
    return {
        "date": ep.id,
        "ok": not errors,
        "words": total,
        "estimated_minutes": round(minutes, 1),
        "sections": {h: count_words(b) for h, b in ep.sections},
        "sources": len(ep.sources),
        "errors": errors,
        "warnings": warnings,
    }

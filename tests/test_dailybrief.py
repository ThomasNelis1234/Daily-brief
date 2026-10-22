"""Offline tests: python -m unittest discover -s tests -t ."""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
from contextlib import redirect_stdout
from datetime import date, datetime
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

from dailybrief import cli, config, episode as epmod, feeds, fallback, site
from dailybrief.validate import check

REPO = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("Europe/Brussels")


def words(n: int, seed: str = "news") -> str:
    base = f"Today the {seed} story moves forward because officials explained what changes next for people. "
    out, count = [], 0
    while count < n:
        out.append(base)
        count += len(base.split())
    text = " ".join(out)
    return text[: len(text)] + "\n\nA second paragraph closes the section with a clear point."


def sources(day: str) -> list[dict]:
    out = []
    for i, sec in enumerate(["ai", "ai", "politics", "politics", "energy", "energy"], start=1):
        out.append({"id": f"S{i}", "section": sec, "title": f"Story {i}", "publisher": "Outlet",
                    "url": f"https://example.com/{sec}/{i}", "date": day})
    return out


def valid_sections() -> list[tuple[str, str]]:
    return [("Intro", words(40, "intro")), ("AI", words(560, "ai")), ("Politics", words(560, "politics")),
            ("Energy", words(420, "energy")), ("Term of the day", words(100, "term")), ("Outro", words(30, "outro"))]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "config", self.tmp / "config")
        (self.tmp / "state").mkdir()
        os.environ["DAILYBRIEF_ROOT"] = str(self.tmp)
        os.environ.pop("SITE_URL", None)
        os.environ.pop("GEMINI_API_KEY", None)
        self.cfg = config.load(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)
        os.environ.pop("DAILYBRIEF_ROOT", None)

    def make(self, day: str = "2026-10-23", sections=None, srcs=None, header=None) -> Path:
        folder = self.tmp / "episodes" / day
        hdr = {"date": day, "title": "Budget talks, a new model and grid news", "summary": "Three stories.",
               "writer": "claude"}
        hdr.update(header or {})
        epmod.write(folder, hdr, sections or valid_sections(), sources(day) if srcs is None else srcs)
        return folder

    def run_cli(self, *argv) -> tuple[int, dict]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = cli.main(list(argv))
        out = buf.getvalue()
        try:
            return code, json.loads(out)
        except json.JSONDecodeError:
            return code, {"raw": out}


class ValidateTests(Base):
    def test_valid_episode(self):
        r = check(epmod.load(self.make()), self.cfg)
        self.assertTrue(r["ok"], r["errors"])
        self.assertGreater(r["estimated_minutes"], 9)

    def test_rejects_urls_citations_bullets(self):
        secs = valid_sections()
        secs[1] = ("AI", secs[1][1] + "\n\nSee https://example.com for more [S1].\n\n- a bullet point here")
        r = check(epmod.load(self.make(sections=secs)), self.cfg)
        joined = " ".join(r["errors"])
        self.assertIn("URL", joined)
        self.assertIn("citation", joined)
        self.assertIn("bullet", joined)

    def test_missing_section_and_sources(self):
        secs = [s for s in valid_sections() if s[0] != "Energy"]
        r = check(epmod.load(self.make(sections=secs, srcs=sources("2026-10-23")[:2])), self.cfg)
        joined = " ".join(r["errors"])
        self.assertIn("'## Energy' missing", joined)
        self.assertIn("Politics' has 0 sources", joined)

    def test_header_date_mismatch(self):
        r = check(epmod.load(self.make(header={"date": "2026-10-22"})), self.cfg)
        self.assertIn("does not match folder", " ".join(r["errors"]))

    def test_spoken_text_has_no_headings_or_header(self):
        text = epmod.load(self.make()).spoken_text()
        self.assertNotIn("##", text)
        self.assertNotIn("writer:", text)
        self.assertTrue(text.startswith("Today the intro story"))


class PublishTests(Base):
    def test_publish_builds_feed_index_and_state(self):
        self.make("2026-10-22")
        self.make("2026-10-23")
        code, out = self.run_cli("publish", "--out", str(self.tmp / "site"), "--cache", str(self.tmp / "cache"),
                                 "--fake-audio")
        self.assertEqual(code, 0, out)
        self.assertEqual(out["episodes"], ["2026-10-23", "2026-10-22"])
        feed = ET.parse(self.tmp / "site" / "feed.xml").getroot()
        items = feed.findall("./channel/item")
        self.assertEqual(len(items), 2)
        enc = items[0].find("enclosure")
        self.assertTrue(enc.get("url").startswith("https://daily-brief-tnelis.vercel.app/episodes/2026-10-23.mp3"))
        self.assertGreater(int(enc.get("length")), 0)
        ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
        self.assertEqual(feed.find("./channel/itunes:block", ns).text, "Yes")
        self.assertTrue((self.tmp / "site" / "cover.png").exists())
        self.assertIn("Budget talks", (self.tmp / "site" / "index.html").read_text())
        pub = json.loads((self.tmp / "state" / "published.json").read_text())
        self.assertIn("2026-10-23", pub)
        # second run reuses cached audio
        code, out = self.run_cli("publish", "--out", str(self.tmp / "site"), "--cache", str(self.tmp / "cache"),
                                 "--fake-audio")
        self.assertEqual(out["new_audio"], [])

    def test_invalid_episode_is_skipped(self):
        self.make("2026-10-22")
        self.make("2026-10-23", sections=valid_sections()[:2])
        code, out = self.run_cli("publish", "--out", str(self.tmp / "site"), "--cache", str(self.tmp / "cache"),
                                 "--fake-audio", "--no-state")
        self.assertEqual(out["episodes"], ["2026-10-22"])
        self.assertEqual(out["skipped"][0]["date"], "2026-10-23")

    def test_site_url_override_and_vercel_folder_kept(self):
        os.environ["SITE_URL"] = "https://custom.example/"
        self.make()
        (self.tmp / "site" / ".vercel").mkdir(parents=True)
        (self.tmp / "site" / ".vercel" / "project.json").write_text("{}")
        self.run_cli("publish", "--out", str(self.tmp / "site"), "--cache", str(self.tmp / "cache"),
                     "--fake-audio", "--no-state")
        self.assertIn("https://custom.example/feed.xml", (self.tmp / "site" / "feed.xml").read_text())
        self.assertTrue((self.tmp / "site" / ".vercel" / "project.json").exists())
        os.environ.pop("SITE_URL")


RSS = """<?xml version="1.0"?><rss version="2.0"><channel><title>T</title>
<item><title>Budget deal &amp; reactions</title><link>https://a.example/1</link>
<pubDate>Thu, 22 Oct 2026 18:00:00 +0200</pubDate><description><![CDATA[<p>The coalition <b>agreed</b>.</p>]]></description></item>
<item><title>Old story</title><link>https://a.example/0</link><pubDate>Mon, 12 Oct 2026 08:00:00 +0200</pubDate></item>
</channel></rss>"""

ATOM = """<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom"><title>S</title>
<entry><title>New model released</title><link href="https://b.example/x" rel="alternate"/>
<updated>2026-10-22T10:00:00Z</updated><summary>Short summary.</summary></entry></feed>"""


class FeedTests(Base):
    def test_parse_rss_and_atom(self):
        rss = feeds.parse(RSS, "A", "politics")
        self.assertEqual(rss[0].title, "Budget deal & reactions")
        self.assertEqual(rss[0].summary, "The coalition agreed .")
        atom = feeds.parse(ATOM, "B", "ai")
        self.assertEqual(atom[0].url, "https://b.example/x")
        self.assertEqual(atom[0].published.year, 2026)

    def test_collect_skips_old_items_and_broken_feeds(self):
        def fetcher(url):
            if "politico" in url:
                raise RuntimeError("HTTP 404")
            return ATOM if "simonwillison" in url else RSS
        since = datetime(2026, 10, 21, 12, tzinfo=TZ)
        items, report = feeds.collect(self.cfg, since, fetcher=fetcher)
        self.assertFalse(any(i.url == "https://a.example/0" for i in items))
        self.assertTrue(any(not r["ok"] for r in report))


class FallbackTests(Base):
    def items(self):
        out = []
        for sec in ("ai", "politics", "energy"):
            for i in range(3):
                out.append(feeds.FeedItem(feed="F", section=sec, title=f"{sec} {i}", url=f"https://f.example/{sec}/{i}",
                                          published=datetime(2026, 10, 22, 20, tzinfo=TZ), summary="s"))
        return out

    def test_backup_writes_valid_episode_and_drops_unknown_urls(self):
        items = self.items()
        secs = dict(valid_sections())
        data = {"title": "Backup headline", "summary": "Backup summary.", "intro": secs["Intro"], "ai": secs["AI"],
                "politics": secs["Politics"], "energy": secs["Energy"], "term": secs["Term of the day"],
                "outro": secs["Outro"],
                "source_urls": {"ai": ["https://f.example/ai/0", "https://f.example/ai/1", "https://invented.example"],
                                "politics": ["https://f.example/politics/0", "https://f.example/politics/1"],
                                "energy": ["https://f.example/energy/0", "https://f.example/energy/2"]}}
        with mock.patch.object(feeds, "collect", return_value=(items, [])):
            res = fallback.write_backup(self.cfg, date(2026, 10, 23), datetime(2026, 10, 23, 6, 40, tzinfo=TZ),
                                        generator=lambda prompt, models: (data, "gemini-test"))
        self.assertTrue(res["validation"]["ok"], res["validation"]["errors"])
        ep = epmod.load(self.tmp / "episodes" / "2026-10-23")
        self.assertNotIn("https://invented.example", [s["url"] for s in ep.sources])
        self.assertIn("backup", ep.writer)

    def test_cli_waits_before_cutoff_and_needs_key(self):
        code, out = self.run_cli("fallback", "--now", "2026-10-23T06:00")
        self.assertIn("waiting", out["action"])
        code, out = self.run_cli("fallback", "--now", "2026-10-23T06:45")
        self.assertIn("no GEMINI_API_KEY", out["action"])

    def test_cli_publish_safety_net_and_weekend(self):
        self.make("2026-10-23")
        code, out = self.run_cli("fallback", "--now", "2026-10-23T06:45")
        self.assertEqual(out["action"], "publish")
        code, out = self.run_cli("fallback", "--now", "2026-10-24T07:00")
        self.assertIn("no episode on this weekday", out["action"])


if __name__ == "__main__":
    unittest.main()

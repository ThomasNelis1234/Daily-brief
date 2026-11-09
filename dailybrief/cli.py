"""Command line: python -m dailybrief.cli <command>  (run from the repository root)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from . import audio, episode as epmod, site, state
from .config import load
from .validate import check


def _now(cfg, override: str | None = None) -> datetime:
    tz = ZoneInfo(cfg.timezone)
    if override:
        dt = datetime.fromisoformat(override)
        return dt if dt.tzinfo else dt.replace(tzinfo=tz)
    return datetime.now(tz)


def _gh_output(**kv) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            for k, v in kv.items():
                fh.write(f"{k}={str(v).lower() if isinstance(v, bool) else v}\n")


def _print(obj) -> None:
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def cmd_today(args, cfg) -> int:
    now = _now(cfg, args.now)
    day = now.date()
    folder = epmod.folder_for(cfg.episodes_dir, day)
    pub = state.load(cfg.state_file)
    _print({"date": day.isoformat(), "weekday": day.strftime("%A"),
            "episode_day": day.weekday() in cfg.episode["weekdays"],
            "folder": str(folder.relative_to(cfg.root)), "script_exists": (folder / "script.md").exists(),
            "published": day.isoformat() in pub})
    return 0


def cmd_validate(args, cfg) -> int:
    day = date.fromisoformat(args.date) if args.date else _now(cfg).date()
    folder = epmod.folder_for(cfg.episodes_dir, day)
    if not (folder / "script.md").exists():
        _print({"date": day.isoformat(), "ok": False, "errors": [f"{folder}/script.md not found"]})
        return 1
    result = check(epmod.load(folder), cfg)
    _print(result)
    return 0 if result["ok"] else 1


def _fake_synth(text: str, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    # ~1 second of "audio" per 2.5 words at 48 kbit/s; enough for tests and dry runs without edge-tts
    out.write_bytes(b"\xff\xfb\x90\x64" + b"\x00" * int(len(text.split()) / 2.5 * 6000))


def cmd_publish(args, cfg) -> int:
    out = Path(args.out)
    cache = Path(args.cache)
    synth = _fake_synth if args.fake_audio else audio.synthesizer(cfg.audio)
    voice_tag = (cfg.audio.get("engine", "edge")[:2] + cfg.audio["voice"].replace("-", "").replace("_", "").lower()[-8:])
    keep = cfg.publish["keep_episodes"]
    items, skipped, made = [], [], []
    for folder in epmod.list_folders(cfg.episodes_dir):
        if len(items) >= keep:
            break
        ep = epmod.load(folder)
        result = check(ep, cfg)
        if not result["ok"]:
            skipped.append({"date": ep.id, "errors": result["errors"]})
            continue
        key = f"{ep.id}-{ep.script_sha[:12]}-{voice_tag}"
        older = sorted(cache.glob(f"{ep.id}-{ep.script_sha[:12]}-*.mp3")) if cache.exists() else []
        if not (cache / f"{key}.mp3").exists() and older and ep.id in state.load(cfg.state_file):
            path, new = older[0], False  # already live in a previous voice: keep it, don't re-record
        else:
            path, new = audio.ensure_audio(ep.spoken_text(), cache, key, synth)
        if new:
            made.append(ep.id)
        size = path.stat().st_size
        items.append(site.Item(episode=ep, audio=path, size=size,
                               duration=audio.duration_seconds(path, cfg.audio["bitrate_kbps"])))
    limit = cfg.publish["max_site_mb"] * 1024 * 1024
    while items and sum(i.size for i in items) > limit:
        dropped = items.pop()
        skipped.append({"date": dropped.episode.id, "errors": ["dropped: site size limit"]})
    summary = site.build(items, cfg, out)

    pub = state.load(cfg.state_file)
    stamp = _now(cfg).isoformat(timespec="seconds")
    for it in items:
        prev = pub.get(it.episode.id, {})
        if prev.get("script_sha") != it.episode.script_sha:
            pub[it.episode.id] = {"published_at": stamp, "writer": it.episode.writer,
                                  "script_sha": it.episode.script_sha, "duration_s": it.duration,
                                  "bytes": it.size}
    if not args.no_state:
        state.save(cfg.state_file, pub)
    report = {"site_url": cfg.site_url, "episodes": [i.episode.id for i in items], "new_audio": made,
              "skipped": skipped, **summary}
    _print(report)
    return 0 if items else 1


VOICE_CANDIDATES = [
    ("edge", "en-GB-RyanNeural", "Current voice (Microsoft, British male)"),
    ("edge", "en-US-AndrewMultilingualNeural", "Microsoft, American male, newer model"),
    ("edge", "en-US-AvaMultilingualNeural", "Microsoft, American female, newer model"),
    ("kokoro", "bm_george", "Kokoro, British male"),
    ("kokoro", "bm_lewis", "Kokoro, British male"),
    ("kokoro", "bf_emma", "Kokoro, British female"),
    ("kokoro", "am_michael", "Kokoro, American male"),
    ("kokoro", "af_heart", "Kokoro, American female (often rated most natural)"),
]


def cmd_voices(args, cfg) -> int:
    """Record the same ~45-second excerpt in each candidate voice into voices/ for comparison."""
    folder = epmod.list_folders(cfg.episodes_dir)[0]
    ep = epmod.load(folder)
    intro = ep.body("Intro") or ""
    ai_paras = [p for p in (ep.body("AI") or "").split("\n\n") if p.strip()][:2]
    text = audio.clean_for_speech("\n\n".join([intro, *ai_paras]))
    out = cfg.root / "voices"
    out.mkdir(exist_ok=True)
    made = []
    for engine, voice, label in VOICE_CANDIDATES:
        path = out / f"{engine}-{voice}.mp3"
        try:
            audio.synthesizer(cfg.audio, voice=voice, engine=engine)(text, path)
            made.append({"engine": engine, "voice": voice, "label": label, "file": path.name,
                         "current": engine == cfg.audio.get("engine", "edge") and voice == cfg.audio["voice"]})
        except Exception as exc:
            print(f"{engine}/{voice} failed: {exc}", file=sys.stderr)
    (out / "voices.json").write_text(json.dumps({"episode": ep.id, "words": len(text.split()), "voices": made},
                                                indent=2) + "\n", encoding="utf-8")
    _print({"episode": ep.id, "made": [m["file"] for m in made]})
    return 0 if made else 1


def cmd_fallback(args, cfg) -> int:
    now = _now(cfg, args.now)
    day = date.fromisoformat(args.date) if args.date else now.date()
    folder = epmod.folder_for(cfg.episodes_dir, day)
    pub = state.load(cfg.state_file)
    out = {"date": day.isoformat(), "now": now.isoformat(timespec="minutes")}

    if day.weekday() not in cfg.episode["weekdays"] and not args.force:
        out["action"] = "none: no episode on this weekday"
        _print(out); _gh_output(needs_publish=False, wrote=False)
        return 0

    if (folder / "script.md").exists():
        ep = epmod.load(folder)
        result = check(ep, cfg)
        live = pub.get(day.isoformat(), {}).get("script_sha") == ep.script_sha
        out.update(script="exists", writer=ep.writer, valid=result["ok"], published=live)
        needs = result["ok"] and not live
        out["action"] = "publish" if needs else ("none: already published" if live else "none: script invalid")
        if not result["ok"]:
            out["errors"] = result["errors"]
        _print(out); _gh_output(needs_publish=needs, wrote=False)
        return 0

    after = time.fromisoformat(cfg.fallback["after_local"])
    if now.timetz().replace(tzinfo=None) < after and not args.force:
        out["action"] = f"none: waiting for the Claude task until {after.isoformat(timespec='minutes')}"
        _print(out); _gh_output(needs_publish=False, wrote=False)
        return 0
    if not os.environ.get("GEMINI_API_KEY"):
        out["action"] = "none: no script and no GEMINI_API_KEY secret, so no backup episode today"
        _print(out); _gh_output(needs_publish=False, wrote=False)
        return 0

    from .fallback import write_backup  # noqa: PLC0415

    res = write_backup(cfg, day, now)
    ok = bool(res.get("written") and res.get("validation", {}).get("ok"))
    if res.get("written") and not ok:
        # keep the failed draft out of the episode list
        for f in ("script.md", "sources.json"):
            (folder / f).unlink(missing_ok=True)
    out.update(action="backup written" if ok else "backup failed", backup=res)
    _print(out); _gh_output(needs_publish=ok, wrote=ok)
    return 0 if ok else 1


def cmd_probe(args, cfg) -> int:
    from datetime import timedelta  # noqa: PLC0415

    from . import feeds, gemini  # noqa: PLC0415

    now = _now(cfg)
    _, report = feeds.collect(cfg, now - timedelta(hours=cfg.fallback["lookback_hours"]))
    result = {"probed_at": now.isoformat(timespec="minutes"), "feeds": report}
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            models = gemini.list_models(key)
            result["gemini_models_available"] = models
            result["gemini_configured_found"] = {m: m in models for m in cfg.fallback["gemini_models"]}
        except Exception as exc:
            result["gemini_error"] = str(exc)[:300]
    path = cfg.root / "state" / "feed_probe.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    _print(result)
    return 0


def cmd_vercel_setup(args, cfg) -> int:
    from . import vercel  # noqa: PLC0415

    project = vercel.ensure_project(cfg.vercel_project)
    vercel.link(Path(args.site), project)
    _print({"project": project["name"], "id": project["id"]})
    return 0


def cmd_vercel_domain(args, cfg) -> int:
    from . import vercel  # noqa: PLC0415

    url = vercel.production_url(cfg.vercel_project)
    if not url:
        print("", end="")
        return 1
    print(url)
    return 0


def cmd_vercel_unstick(args, cfg) -> int:
    from . import vercel  # noqa: PLC0415

    cancelled = vercel.cancel_stuck(cfg.vercel_project)
    _print({"cancelled": cancelled})
    return 0


def cmd_vercel_status(args, cfg) -> int:
    from . import vercel  # noqa: PLC0415

    _print({"deployments": vercel.recent_deployments(cfg.vercel_project, limit=args.limit)})
    return 0


def cmd_vercel_wait(args, cfg) -> int:
    from . import vercel  # noqa: PLC0415

    result = vercel.wait_ready(cfg.vercel_project, args.deployment, timeout_s=args.timeout)
    _print(result)
    return 0 if result["state"] == "READY" else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="dailybrief")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("today", help="what today's episode status is"); s.add_argument("--now")
    s = sub.add_parser("validate", help="check an episode"); s.add_argument("--date")
    s = sub.add_parser("publish", help="build the site (MP3s, feed, index)")
    s.add_argument("--out", default="site"); s.add_argument("--cache", default="build/audio")
    s.add_argument("--fake-audio", action="store_true", help="no edge-tts; placeholder audio for tests")
    s.add_argument("--no-state", action="store_true", help="do not update state/published.json")
    s = sub.add_parser("fallback", help="backup writer + publish safety net")
    s.add_argument("--date"); s.add_argument("--now"); s.add_argument("--force", action="store_true")
    sub.add_parser("probe", help="Phase 0: check feeds and Gemini models")
    sub.add_parser("voices", help="record a short excerpt in each candidate voice into voices/")
    s = sub.add_parser("vercel-setup", help="create the Vercel project if needed and link the site folder")
    s.add_argument("--site", default="site")
    sub.add_parser("vercel-domain", help="print the Vercel project's production URL")
    sub.add_parser("vercel-unstick", help="cancel leftover queued/building Vercel deployments")
    s = sub.add_parser("vercel-status", help="list the project's recent Vercel deployments")
    s.add_argument("--limit", type=int, default=10)
    s = sub.add_parser("vercel-wait", help="wait until a Vercel deployment is ready")
    s.add_argument("deployment"); s.add_argument("--timeout", type=int, default=300)
    args = p.parse_args(argv)
    cfg = load()
    return {"today": cmd_today, "validate": cmd_validate, "publish": cmd_publish, "fallback": cmd_fallback,
            "probe": cmd_probe, "voices": cmd_voices, "vercel-setup": cmd_vercel_setup,
            "vercel-domain": cmd_vercel_domain, "vercel-unstick": cmd_vercel_unstick,
            "vercel-status": cmd_vercel_status, "vercel-wait": cmd_vercel_wait}[args.cmd](args, cfg)


if __name__ == "__main__":
    sys.exit(main())

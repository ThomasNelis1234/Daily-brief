"""Text-to-speech with Microsoft Edge neural voices (edge-tts: free, no key).

edge-tts is imported lazily so validation and tests run without it; only the publish workflow installs it.
"""
from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path
from typing import Callable

Synthesizer = Callable[[str, Path], None]


def clean_for_speech(text: str) -> str:
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def edge_synthesizer(voice: str, rate: str = "+0%", retries: int = 3) -> Synthesizer:
    def synth(text: str, out: Path) -> None:
        import edge_tts  # noqa: PLC0415 - optional dependency

        out.parent.mkdir(parents=True, exist_ok=True)
        tmp = out.with_suffix(".part")
        last: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                asyncio.run(edge_tts.Communicate(text, voice, rate=rate).save(str(tmp)))
                if tmp.stat().st_size < 10_000:
                    raise RuntimeError(f"audio suspiciously small ({tmp.stat().st_size} bytes)")
                tmp.replace(out)
                return
            except Exception as exc:  # network hiccups are common; retry
                last = exc
                time.sleep(5 * attempt)
        raise RuntimeError(f"edge-tts failed after {retries} attempts: {last}")

    return synth


def duration_seconds(path: Path, bitrate_kbps: int) -> int:
    """Constant-bitrate estimate; edge-tts writes CBR MP3."""
    return int(round(path.stat().st_size * 8 / (bitrate_kbps * 1000)))


def ensure_audio(spoken: str, cache_dir: Path, key: str, synth: Synthesizer) -> tuple[Path, bool]:
    """Return the cached MP3 for this key, synthesising it if missing. Second value: newly made."""
    path = cache_dir / f"{key}.mp3"
    if path.exists() and path.stat().st_size > 0:
        return path, False
    synth(clean_for_speech(spoken), path)
    return path, True

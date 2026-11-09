"""Text-to-speech, two free engines:

- "edge":   Microsoft Edge neural voices via edge-tts (online, no key).
- "kokoro": Kokoro-82M, an open-source model (Apache 2.0) that runs on the GitHub runner's CPU.

Both are imported lazily so validation and tests run without them; only the workflows install them.
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


def kokoro_synthesizer(voice: str, speed: float = 1.0, bitrate_kbps: int = 64, pause_s: float = 0.45) -> Synthesizer:
    """Kokoro-82M on CPU. Voice prefix sets the accent: a* = American, b* = British (e.g. bm_george)."""
    def synth(text: str, out: Path) -> None:
        import subprocess  # noqa: PLC0415
        import tempfile  # noqa: PLC0415

        import numpy as np  # noqa: PLC0415
        import soundfile as sf  # noqa: PLC0415
        from kokoro import KPipeline  # noqa: PLC0415

        pipeline = KPipeline(lang_code=voice[0], repo_id="hexgrad/Kokoro-82M")
        rate = 24_000
        silence = np.zeros(int(rate * pause_s), dtype=np.float32)
        chunks = []
        for para in [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]:
            for _, _, audio in pipeline(para, voice=voice, speed=speed):
                if audio is not None:
                    chunks.append(np.asarray(audio, dtype=np.float32))
            chunks.append(silence)
        if not chunks:
            raise RuntimeError("kokoro produced no audio")
        out.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            wav = Path(tmpdir) / "speech.wav"
            sf.write(wav, np.concatenate(chunks), rate)
            tmp = out.with_suffix(".part")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-ac", "1", "-ar", "24000",
                            "-codec:a", "libmp3lame", "-b:a", f"{bitrate_kbps}k", "-f", "mp3", str(tmp)], check=True)
        tmp.replace(out)

    return synth


def synthesizer(audio_cfg: dict, voice: str | None = None, engine: str | None = None) -> Synthesizer:
    engine = engine or audio_cfg.get("engine", "edge")
    voice = voice or audio_cfg["voice"]
    if engine == "kokoro":
        return kokoro_synthesizer(voice, float(audio_cfg.get("speed", 1.0)), int(audio_cfg["bitrate_kbps"]))
    return edge_synthesizer(voice, audio_cfg.get("rate", "+0%"))


def duration_seconds(path: Path, bitrate_kbps: int) -> int:
    """Constant-bitrate estimate; both engines write CBR MP3 at the configured bitrate."""
    try:
        from mutagen.mp3 import MP3  # noqa: PLC0415

        return int(round(MP3(str(path)).info.length))
    except Exception:
        return int(round(path.stat().st_size * 8 / (bitrate_kbps * 1000)))


def ensure_audio(spoken: str, cache_dir: Path, key: str, synth: Synthesizer) -> tuple[Path, bool]:
    """Return the cached MP3 for this key, synthesising it if missing. Second value: newly made."""
    path = cache_dir / f"{key}.mp3"
    if path.exists() and path.stat().st_size > 0:
        return path, False
    synth(clean_for_speech(spoken), path)
    return path, True

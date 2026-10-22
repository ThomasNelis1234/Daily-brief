"""Episode files: episodes/<date>/script.md (header + sections) and sources.json."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

HEADER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)
WORD_RE = re.compile(r"[A-Za-z0-9À-ɏ'’-]+")


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


@dataclass
class Episode:
    day: date
    folder: Path
    header: dict = field(default_factory=dict)
    sections: list[tuple[str, str]] = field(default_factory=list)  # (heading, body) in file order
    sources: list[dict] = field(default_factory=list)
    script_text: str = ""

    @property
    def id(self) -> str:
        return self.day.isoformat()

    @property
    def title(self) -> str:
        return str(self.header.get("title", "")).strip()

    @property
    def summary(self) -> str:
        return str(self.header.get("summary", "")).strip()

    @property
    def writer(self) -> str:
        return str(self.header.get("writer", "unknown")).strip()

    @property
    def script_sha(self) -> str:
        return hashlib.sha256(self.script_text.encode("utf-8")).hexdigest()

    def body(self, heading: str) -> str | None:
        for h, b in self.sections:
            if h.lower() == heading.lower():
                return b
        return None

    def spoken_text(self) -> str:
        """Text the voice reads: section bodies in order, headings removed, paragraphs kept."""
        parts = []
        for _, body in self.sections:
            paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip()]
            parts.append("\n\n".join(paras))
        return "\n\n".join(p for p in parts if p)

    def word_count(self) -> int:
        return sum(count_words(b) for _, b in self.sections)

    def sources_for(self, section_key: str) -> list[dict]:
        return [s for s in self.sources if s.get("section") == section_key]


def folder_for(episodes_dir: Path, day: date) -> Path:
    return episodes_dir / day.isoformat()


def parse_script(text: str) -> tuple[dict, list[tuple[str, str]]]:
    m = HEADER_RE.match(text)
    header: dict = {}
    rest = text
    if m:
        header = yaml.safe_load(m.group(1)) or {}
        rest = text[m.end():]
    sections: list[tuple[str, str]] = []
    matches = list(HEADING_RE.finditer(rest))
    for i, hm in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(rest)
        sections.append((hm.group(1).strip(), rest[hm.end():end].strip()))
    return header, sections


def load(folder: Path) -> Episode:
    day = date.fromisoformat(folder.name)
    script_path = folder / "script.md"
    text = script_path.read_text(encoding="utf-8")
    header, sections = parse_script(text)
    sources: list[dict] = []
    src_path = folder / "sources.json"
    if src_path.exists():
        data = json.loads(src_path.read_text(encoding="utf-8"))
        sources = data.get("sources", []) if isinstance(data, dict) else []
    return Episode(day=day, folder=folder, header=header, sections=sections, sources=sources, script_text=text)


def list_folders(episodes_dir: Path) -> list[Path]:
    """Episode folders with a script, newest first."""
    out = []
    if not episodes_dir.exists():
        return out
    for p in episodes_dir.iterdir():
        if p.is_dir() and (p / "script.md").exists():
            try:
                date.fromisoformat(p.name)
            except ValueError:
                continue
            out.append(p)
    return sorted(out, key=lambda p: p.name, reverse=True)


def write(folder: Path, header: dict, sections: list[tuple[str, str]], sources: list[dict]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    head = yaml.safe_dump(header, sort_keys=False, allow_unicode=True, width=1000).strip()
    body = "\n\n".join(f"## {h}\n\n{b.strip()}" for h, b in sections)
    (folder / "script.md").write_text(f"---\n{head}\n---\n\n{body}\n", encoding="utf-8")
    (folder / "sources.json").write_text(
        json.dumps({"date": folder.name, "sources": sources}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

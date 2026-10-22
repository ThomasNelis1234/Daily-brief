"""Load the YAML configuration in config/."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Section:
    key: str
    heading: str
    min_words: int = 0
    min_sources: int = 0


@dataclass
class Config:
    raw: dict
    sources: dict
    root: Path = field(default=ROOT)

    @property
    def timezone(self) -> str:
        return self.raw.get("timezone", "Europe/Brussels")

    @property
    def show(self) -> dict:
        return self.raw["show"]

    @property
    def sections(self) -> list[Section]:
        return [Section(**s) for s in self.raw["episode"]["sections"]]

    @property
    def optional_sections(self) -> list[Section]:
        return [Section(**s) for s in self.raw["episode"].get("optional_sections", [])]

    @property
    def episode(self) -> dict:
        return self.raw["episode"]

    @property
    def audio(self) -> dict:
        return self.raw["audio"]

    @property
    def publish(self) -> dict:
        return self.raw["publish"]

    @property
    def fallback(self) -> dict:
        return self.raw["fallback"]

    @property
    def vercel_project(self) -> str:
        return os.environ.get("VERCEL_PROJECT") or self.raw["vercel"]["project"]

    @property
    def site_url(self) -> str:
        return (os.environ.get("SITE_URL") or self.show["site_url"]).rstrip("/")

    @property
    def episodes_dir(self) -> Path:
        return self.root / "episodes"

    @property
    def state_file(self) -> Path:
        return self.root / "state" / "published.json"

    def feeds(self, section: str) -> list[dict]:
        return self.sources.get(section, {}).get("feeds", [])


def load(root: Path | None = None) -> Config:
    root = root or Path(os.environ.get("DAILYBRIEF_ROOT", ROOT))
    with open(root / "config" / "settings.yaml", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    with open(root / "config" / "sources.yaml", encoding="utf-8") as fh:
        sources = yaml.safe_load(fh)
    return Config(raw=raw, sources=sources, root=root)

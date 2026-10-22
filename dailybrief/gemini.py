"""Gemini API (free tier) backup writer. Only used when the Claude task has not produced today's script."""
from __future__ import annotations

import json
import os

import requests

API = "https://generativelanguage.googleapis.com/v1beta"

SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING"},
        "summary": {"type": "STRING"},
        "intro": {"type": "STRING"},
        "ai": {"type": "STRING"},
        "politics": {"type": "STRING"},
        "energy": {"type": "STRING"},
        "term": {"type": "STRING"},
        "outro": {"type": "STRING"},
        "source_urls": {
            "type": "OBJECT",
            "properties": {k: {"type": "ARRAY", "items": {"type": "STRING"}} for k in ("ai", "politics", "energy")},
            "required": ["ai", "politics", "energy"],
        },
    },
    "required": ["title", "summary", "intro", "ai", "politics", "energy", "term", "outro", "source_urls"],
}


def list_models(api_key: str) -> list[str]:
    resp = requests.get(f"{API}/models", headers={"x-goog-api-key": api_key}, timeout=30)
    resp.raise_for_status()
    return [m["name"].removeprefix("models/") for m in resp.json().get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])]


def generate(prompt: str, models: list[str], api_key: str | None = None) -> tuple[dict, str]:
    """Try each model in order; return (parsed JSON, model used)."""
    api_key = api_key or os.environ["GEMINI_API_KEY"]
    errors = []
    for model in models:
        resp = requests.post(
            f"{API}/models/{model}:generateContent",
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json", "responseSchema": SCHEMA,
                                     "temperature": 0.4, "maxOutputTokens": 8192},
            },
            timeout=180,
        )
        if resp.status_code != 200:
            errors.append(f"{model}: HTTP {resp.status_code} {resp.text[:200]}")
            continue
        try:
            text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(text), model
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            errors.append(f"{model}: unreadable response ({exc})")
    raise RuntimeError("all Gemini models failed: " + " | ".join(errors))

"""Vercel REST API helpers: make sure the project exists, link a folder to it, find its production domain."""
from __future__ import annotations

import json
import os
from pathlib import Path

import requests

API = "https://api.vercel.com"


def _headers() -> dict:
    return {"Authorization": f"Bearer {os.environ['VERCEL_TOKEN']}", "Content-Type": "application/json"}


def ensure_project(name: str) -> dict:
    resp = requests.get(f"{API}/v9/projects/{name}", headers=_headers(), timeout=30)
    if resp.status_code == 404:
        resp = requests.post(f"{API}/v11/projects", headers=_headers(), timeout=30,
                             json={"name": name, "framework": None})
    resp.raise_for_status()
    return resp.json()


def link(folder: Path, project: dict) -> Path:
    """Write .vercel/project.json so `vercel deploy` targets this project without prompts."""
    target = folder / ".vercel" / "project.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"projectId": project["id"], "orgId": project["accountId"]}) + "\n", encoding="utf-8")
    return target


def production_url(name: str) -> str | None:
    resp = requests.get(f"{API}/v9/projects/{name}/domains", headers=_headers(), timeout=30)
    resp.raise_for_status()
    names = [d["name"] for d in resp.json().get("domains", []) if not d.get("gitBranch") and not d.get("redirect")]
    custom = [n for n in names if not n.endswith(".vercel.app")]
    generated = sorted((n for n in names if n.endswith(".vercel.app")), key=len)
    chosen = (custom or generated or [None])[0]
    return f"https://{chosen}" if chosen else None


STUCK_STATES = ("QUEUED", "INITIALIZING", "BUILDING")


def _team_params(project: dict) -> dict:
    account = project.get("accountId", "")
    return {"teamId": account} if account.startswith("team_") else {}


def cancel_stuck(name: str) -> list[dict]:
    """Cancel this project's deployments that are still queued or building.

    Publishing runs one at a time (workflow concurrency group), so any deployment still in one of these
    states when a run starts is a leftover from an earlier run that hung or was cancelled. Left alone it
    holds the account's build slot and every new deployment waits behind it at "Building…".
    """
    project = ensure_project(name)
    params = {"projectId": project["id"], "state": ",".join(STUCK_STATES), "limit": 50, **_team_params(project)}
    resp = requests.get(f"{API}/v6/deployments", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    cancelled = []
    for d in resp.json().get("deployments", []):
        state = d.get("state") or d.get("readyState")
        if state not in STUCK_STATES:
            continue
        r = requests.patch(f"{API}/v12/deployments/{d['uid']}/cancel", headers=_headers(),
                           params=_team_params(project), timeout=30)
        cancelled.append({"id": d["uid"], "url": d.get("url"), "state": state, "cancel_status": r.status_code})
    return cancelled

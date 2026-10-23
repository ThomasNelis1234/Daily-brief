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


def _summary(d: dict) -> dict:
    return {"id": d.get("uid") or d.get("id"), "url": d.get("url"),
            "state": d.get("readyState") or d.get("state"), "substate": d.get("readySubstate"),
            "target": d.get("target"), "created": d.get("created") or d.get("createdAt"),
            "error": d.get("errorCode") or d.get("errorMessage")}


def recent_deployments(name: str, limit: int = 10) -> list[dict]:
    project = ensure_project(name)
    params = {"projectId": project["id"], "limit": limit, **_team_params(project)}
    resp = requests.get(f"{API}/v6/deployments", headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return [_summary(d) for d in resp.json().get("deployments", [])]


def cancel_stuck(name: str) -> list[dict]:
    """Cancel this project's deployments that are still queued or building.

    Publishing runs one at a time (workflow concurrency group), so any deployment still in one of these
    states when a run starts is a leftover from an earlier run that hung or was cancelled.
    """
    project = ensure_project(name)
    cancelled = []
    for d in recent_deployments(name, limit=20):
        if d["state"] not in STUCK_STATES:
            continue
        r = requests.patch(f"{API}/v12/deployments/{d['id']}/cancel", headers=_headers(),
                           params=_team_params(project), timeout=30)
        cancelled.append({**d, "cancel_status": r.status_code})
    return cancelled


def wait_ready(name: str, deployment: str, timeout_s: int = 300, poll_s: int = 10) -> dict:
    """Poll one deployment (id or URL) until it is READY, ERROR or CANCELED, or the timeout passes."""
    import time  # noqa: PLC0415

    project = ensure_project(name)
    ident = deployment.replace("https://", "").strip("/")
    deadline = time.monotonic() + timeout_s
    last = {}
    while True:
        resp = requests.get(f"{API}/v13/deployments/{ident}", headers=_headers(),
                            params=_team_params(project), timeout=30)
        resp.raise_for_status()
        last = _summary(resp.json())
        print(f"deployment {last['url']}: {last['state']} {last['substate'] or ''}".rstrip(), flush=True)
        if last["state"] in ("READY", "ERROR", "CANCELED") or time.monotonic() > deadline:
            return last
        time.sleep(poll_s)

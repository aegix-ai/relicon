"""Versioned policy snapshots per niche, with rollback.

A snapshot stores the observation ids it was fit on (not the covariance), so any version can be refit exactly.
`active:<niche>` points at the version that proposals use."""
from __future__ import annotations

from datetime import datetime, timezone


def versions(store, niche: str) -> list[dict]:
    return sorted(store.list("policy", niche=niche), key=lambda d: d.get("version", ""))


def snapshot(store, niche: str, payload: dict) -> dict:
    vs = [v for v in versions(store, niche) if v.get("version")]
    ver = f"p{len(vs) + 1:04d}"
    cur = active(store, niche)
    doc = {"version": ver, "niche": niche, "parent": cur["version"] if cur else None,
           "created_at": datetime.now(timezone.utc).isoformat(), **payload}
    store.put("policy", f"{niche}:{ver}", doc, niche=niche)
    set_active(store, niche, ver)
    return doc


def set_active(store, niche: str, version: str) -> None:
    store.put("policy", f"active:{niche}", {"pointer": True, "niche": niche, "active": version}, niche="")


def active(store, niche: str) -> dict | None:
    ptr = store.get("policy", f"active:{niche}")
    return store.get("policy", f"{niche}:{ptr['active']}") if ptr else None


def rollback(store, niche: str, version: str) -> dict:
    doc = store.get("policy", f"{niche}:{version}")
    if doc is None:
        raise KeyError(f"no policy {version} for niche {niche}")
    set_active(store, niche, version)
    return doc

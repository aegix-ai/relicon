"""Creative fatigue from daily rows: pooled slope of log hook rate per day live, centered within each ad."""
from __future__ import annotations

import math

import numpy as np

from .data import Observation


def estimate(obs: list[Observation]) -> dict:
    xs, ys, ws = [], [], []
    for o in obs:
        daily = (o.record.raw or {}).get("daily") or []
        rows = [(d["day"], d["views_3s"], d["impressions"]) for d in daily if d.get("impressions", 0) >= 200]
        if len(rows) < 3:
            continue
        days = np.array([r[0] for r in rows], float)
        lr = np.array([math.log((r[1] + 0.5) / (r[2] + 1.0)) for r in rows])
        w = np.array([r[2] for r in rows], float)
        xs.append(days - np.average(days, weights=w))
        ys.append(lr - np.average(lr, weights=w))
        ws.append(w)
    if not xs:
        return {"per_day": None, "n_ads": 0, "note": "no daily rows yet"}
    x, y, w = np.concatenate(xs), np.concatenate(ys), np.concatenate(ws)
    k = float(np.sum(w * x * y) / np.sum(w * x * x))
    resid = y - k * x
    se = float(np.sqrt(np.sum(w * resid ** 2) / np.sum(w) / np.sum(w * x * x) * len(x) / max(len(x) - 1, 1)))
    return {"per_day": round(math.exp(k) - 1, 4), "ci90": [round(math.exp(k - 1.645 * se) - 1, 4),
            round(math.exp(k + 1.645 * se) - 1, 4)], "n_ads": len(xs)}


def needs_refresh(days_live: int, fat: dict, threshold: float = 0.25) -> bool:
    """True when the expected hook-rate loss after `days_live` days passes `threshold`."""
    k = fat.get("per_day")
    return k is not None and k < 0 and 1 - (1 + k) ** days_live >= threshold

"""Insight memory: field-level effects whose 90% interval excludes zero, with scope, evidence and expiry."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np

from ..genome import space
from . import features
from .model import FunnelModel

Z90 = 1.645
STEP_LABEL = {"hook": "hook rate", "hold": "hold rate", "click": "clicks per 3 s view", "cvr": "conversion rate"}


def extract(model: FunnelModel, generation: int, is_simulated: bool, min_effect: float = 0.03,
            ttl_days: int = 30, ttl_generations: int = 6) -> list[dict]:
    names, spans = features.layout()
    b = model.brief
    now = datetime.now(timezone.utc)
    out = []
    for step, fit in model.fits.items():
        if fit.n_obs < 6:
            continue
        m, S = fit.post.m, fit.post.S
        base_p = 1 / (1 + np.exp(-m[0]))
        for f in space.learnable_fields():
            if f.kind != "cat":
                continue
            a, z = spans[f.path]
            k = z - a
            for j, level in enumerate(f.choices):
                c = np.zeros(len(m))
                c[a:z] = -1.0 / k
                c[a + j] += 1.0
                eff, sd = float(c @ m), float(np.sqrt(c @ S @ c))
                lo, hi = eff - Z90 * sd, eff + Z90 * sd
                if lo > 0 or hi < 0:
                    rel = lambda e: float(np.exp(e * (1 - base_p)) - 1)  # noqa: E731
                    if abs(rel(eff)) < min_effect:
                        continue
                    out.append({
                        "id": f"{b.niche}|{b.platform}|{step}|{f.path}={level}",
                        "scope": {"niche": b.niche, "vertical": b.vertical, "platform": b.platform, "brand": b.brand},
                        "step": step, "field": f.path, "level": str(level),
                        "effect_rel": round(rel(eff), 4), "ci90_rel": [round(rel(lo), 4), round(rel(hi), 4)],
                        "text": f"{f.path} = {level}: {STEP_LABEL[step]} {rel(eff):+.0%} vs the average option "
                                f"(90% CI {rel(lo):+.0%} to {rel(hi):+.0%}), {fit.n_obs} ads",
                        "n_ads": fit.n_obs, "generation": generation, "created_at": now.isoformat(),
                        "expires_at": (now + timedelta(days=ttl_days)).isoformat(),
                        "expires_generation": generation + ttl_generations, "is_simulated": is_simulated,
                    })
    return sorted(out, key=lambda i: -abs(i["effect_rel"]))


def active(insights: list[dict], generation: int | None = None) -> list[dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [i for i in insights if i["expires_at"] > now and (generation is None or i["expires_generation"] >= generation)]

"""Scene-level credit from quartile retention.

For each ad: hazard in each quartile window = -ln(S_end/S_start)/seconds, relative to the ad's own mean hazard.
Each window's log relative hazard is shared among the scenes that overlap it, by overlap time.
A beat with mean log relative hazard > 0 loses viewers faster than the rest of its ad."""
from __future__ import annotations

import math
from collections import defaultdict

from .data import Observation


def ad_windows(o: Observation) -> list[tuple[float, float, float]]:
    m, D = o.record.metrics, float(o.genome.format.duration_s)
    v3 = m.get("views_3s", 0)
    if v3 < 50 or D <= 4 or not o.genome.scenes:
        return []
    pts = [(3.0, 1.0)] + [(q * D, max(m.get(k, 0), 0.5) / v3) for q, k in
                          ((0.25, "q25"), (0.5, "q50"), (0.75, "q75"), (1.0, "q100")) if q * D > 3.0]
    total = -math.log(pts[-1][1]) / (pts[-1][0] - 3.0)
    if total <= 0:
        return []
    out = []
    for (t0, s0), (t1, s1) in zip(pts, pts[1:]):
        if t1 - t0 < 0.5 or s0 <= 0:
            continue
        h = -math.log(max(s1, 1e-6) / s0) / (t1 - t0)
        out.append((t0, t1, math.log(max(h, 1e-4) / total)))
    return out


def scene_credit(obs: list[Observation]) -> dict[str, dict]:
    acc: dict[str, list[tuple[float, float]]] = defaultdict(list)
    for o in obs:
        for t0, t1, lr in ad_windows(o):
            for sc in o.genome.scenes:
                ov = min(t1, sc.end_s) - max(t0, sc.start_s)
                if ov > 0:
                    acc[sc.purpose].append((lr, ov))
                    if sc.end_s - sc.start_s > 4.5:
                        acc["long_shot(>4.5s)"].append((lr, ov))
    out = {}
    for beat, xs in acc.items():
        w = sum(o for _, o in xs)
        mean = sum(v * o for v, o in xs) / w
        var = sum(o * (v - mean) ** 2 for v, o in xs) / w
        n = len(xs)
        se = math.sqrt(var / max(n - 1, 1))
        out[beat] = {"rel_hazard": round(math.exp(mean), 3), "ci90": [round(math.exp(mean - 1.645 * se), 3),
                     round(math.exp(mean + 1.645 * se), 3)], "n_windows": n}
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["rel_hazard"]))

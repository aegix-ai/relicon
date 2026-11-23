"""Observations: one launched genome + its result record, turned into funnel counts.

Rules:
- below the impression floor -> kept for display, not used to learn (D7)
- attribution window still open -> conversions not used (delay handling); hook/hold/click still used
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..genome.models import Genome, ResultRecord

STEPS = ("hook", "hold", "click", "cvr")
OBJECTIVE_STEPS = {"roas": ("hook", "click", "cvr"), "cpa": ("hook", "click", "cvr"), "ctr": ("hook", "click"),
                   "hold": ("hold",), "hook_rate": ("hook",)}


@dataclass
class Observation:
    genome: Genome
    record: ResultRecord
    obs_id: str = ""
    counts: dict = field(default_factory=dict)

    def __post_init__(self):
        m = self.record.metrics
        self.obs_id = self.obs_id or f"{self.genome.id}:{self.record.variant}:{self.record.date_start}"
        self.counts = {
            "hook": (m.get("views_3s", 0), m.get("impressions", 0)),
            "hold": (m.get("q100", 0), m.get("views_3s", 0)),
            "click": (m.get("link_clicks", 0), m.get("views_3s", 0)),
            "cvr": (m.get("conversions", 0), m.get("link_clicks", 0)) if self.record.window_closed else (0, 0),
        }

    @property
    def impressions(self) -> float:
        return float(self.record.metrics.get("impressions", 0))

    def usable(self, floor: int) -> bool:
        return self.impressions >= floor


def emp_logit(s: np.ndarray, n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Empirical logit and its binomial variance (Haldane +0.5)."""
    y = np.log((s + 0.5) / (n - s + 0.5))
    v = 1 / (s + 0.5) + 1 / (n - s + 0.5)
    return y, v


def from_store(store, niche: str | None = None, vertical: str | None = None) -> list[Observation]:
    out = []
    for d in store.list("genome"):
        g = Genome.model_validate(d)
        if vertical and g.brief.vertical != vertical:
            continue
        if niche and g.brief.niche != niche:
            continue
        for r in g.results:
            out.append(Observation(g, r))
    return out

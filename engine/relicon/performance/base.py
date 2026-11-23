"""PerformanceSource: the one interface every results source implements (simulated, CSV, live API).

The learning engine reads only what comes out of here: normalized metric rows with counts.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

COUNT_METRICS = ("impressions", "reach", "spend", "views_3s", "q25", "q50", "q75", "q100", "link_clicks",
                 "conversions", "revenue")
METRICS = COUNT_METRICS + ("frequency", "cpm", "avg_watch_s", "ctr", "cpc", "cvr", "cpa", "roas",
                           "hook_rate", "hold_rate")


def _div(a: float, b: float) -> float:
    return a / b if b else 0.0


def derive(m: dict[str, Any]) -> dict[str, float]:
    """Fill rates from counts. hook_rate = 3 s views / impressions; hold_rate = completions / 3 s views."""
    out = {k: float(m.get(k, 0.0) or 0.0) for k in METRICS}
    imp, v3, clicks, conv = out["impressions"], out["views_3s"], out["link_clicks"], out["conversions"]
    out["frequency"] = out["frequency"] or _div(imp, out["reach"])
    out["cpm"] = _div(out["spend"] * 1000, imp)
    out["ctr"] = _div(clicks, imp)
    out["cpc"] = _div(out["spend"], clicks)
    out["cvr"] = _div(conv, clicks)
    out["cpa"] = _div(out["spend"], conv)
    out["roas"] = _div(out["revenue"], out["spend"])
    out["hook_rate"] = _div(v3, imp)
    out["hold_rate"] = _div(out["q100"], v3)
    return out


class PerformanceSource(ABC):
    name: str = "base"
    is_simulated: bool = False

    @abstractmethod
    def fetch(self, **kwargs: Any) -> list[dict]:
        """Return rows {"genome_id", "variant", "record": ResultRecord-compatible dict}."""

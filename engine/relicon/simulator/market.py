"""SimulatedMarket: launches genomes into a seeded fake market and returns result rows.

Every number it produces is SIMULATED and labeled so (`is_simulated: true`, source "simulated").
Fast genome-only mode: genomes are planned (no media) and scored by the market directly.
"""
from __future__ import annotations

import math
from typing import Any

import numpy as np

from ..genome.models import Genome, ResultRecord
from ..performance.base import PerformanceSource, derive
from .scenarios import Scenario
from .truth import model as truth_model

ATTRIBUTION_DAYS = 7


class SimulatedMarket(PerformanceSource):
    name, is_simulated = "simulated", True

    def __init__(self, scenario: Scenario, seed: int = 0, noise: str = "normal", drift_at: int | None = None):
        self.sc = scenario
        self.rng = np.random.default_rng(seed)
        self.noise = noise
        self.drift_at = drift_at
        b = scenario.brief
        self._truth = truth_model.load(scenario.name, scenario.niche, scenario.vertical, scenario.platform,
                                       scenario.seed, b.price_point)
        self._drift = truth_model.load(scenario.name, scenario.niche, scenario.vertical, scenario.platform,
                                       scenario.seed, b.price_point, drift=True) if drift_at is not None else None
        self.day = 0
        self.pending: list[tuple[str, ResultRecord]] = []

    def truth_for(self, generation: int) -> truth_model.Truth:
        if self._drift is not None and generation >= (self.drift_at or 0):
            return self._drift
        return self._truth

    # evaluation helper only: the eval harness uses it for regret; learning never calls it
    def expected_value(self, g: Genome, generation: int = 0) -> float:
        return self.truth_for(generation).expected_roas(g)

    def _retention(self, t: truth_model.Truth, g: Genome, hold: float) -> list[float]:
        """Share of 3 s viewers still watching at 25/50/75/100%. Scene beats shape the curve."""
        D = float(g.format.duration_s)
        scenes = g.scenes or []

        def mult(x: float) -> float:
            for s in scenes:
                if s.start_s <= x < s.end_s:
                    return t.beat_hazard(s.purpose) * (1.25 if (s.end_s - s.start_s) > 4.5 else 1.0)
            return 1.0
        grid = np.linspace(3.0, max(D, 3.01), 200)
        m = np.array([mult(x) for x in grid])
        cum = np.concatenate([[0.0], np.cumsum((m[1:] + m[:-1]) / 2 * np.diff(grid))])
        lam = -math.log(max(hold, 1e-6)) / max(cum[-1], 1e-6)
        out = []
        for q in (0.25, 0.5, 0.75, 1.0):
            x = q * D
            out.append(1.0 if x <= 3.0 else float(math.exp(-lam * np.interp(x, grid, cum))))
        return out

    def launch(self, genomes: list[Genome], budget_per_ad: float = 150.0, days: int = 7, generation: int = 0,
               report_after_days: int | None = None) -> list[dict[str, Any]]:
        """Run each ad for `days` and report. By default the report waits for the attribution window."""
        t = self.truth_for(generation)
        p = t.params
        rng = self.rng
        sig_ad = 0.5 if self.noise == "high" else p["ad_sigma"]
        budget = budget_per_ad * (0.35 if self.noise == "high" else 1.0)
        report_day = days + ATTRIBUTION_DAYS if report_after_days is None else report_after_days
        rows = []
        for g in genomes:
            seg = t.segment_rates(g)
            eps_h, eps_c = rng.normal(0, sig_ad, size=2)
            cum_imp, cum_reach = 0.0, 0.0
            tot = {k: 0.0 for k in ("impressions", "spend", "views_3s", "q25", "q50", "q75", "q100", "link_clicks",
                                    "conversions", "revenue")}
            daily = []
            watch = 0.0
            for d in range(days):
                spend = budget / days * float(rng.lognormal(0, 0.1))
                cpm = p["cpm"] * float(rng.lognormal(0, 0.15))
                imp = int(rng.poisson(spend / cpm * 1000))
                cum_imp += imp
                reach = p["audience"] * (1 - math.exp(-cum_imp / p["audience"]))
                freq = cum_imp / max(reach, 1.0)
                fat = math.exp(-p["fatigue_k_freq"] * (freq - 1) - p["fatigue_k_age"] * d)
                row = {"day": d, "impressions": imp, "spend": round(spend, 2), "frequency": round(freq, 3)}
                v3 = q100 = clicks = conv = 0
                qs = [0, 0, 0, 0]
                rev = 0.0
                conv_late = 0
                for w, r in seg:
                    n = int(rng.binomial(imp, w))
                    h = 1 / (1 + math.exp(-(math.log(r["hook"] / (1 - r["hook"])) + eps_h))) * fat
                    c = 1 / (1 + math.exp(-(math.log(r["click"] / (1 - r["click"])) + eps_c))) * fat
                    sv = int(rng.binomial(n, h))
                    ret = self._retention(t, g, r["hold"])
                    sq = [int(rng.binomial(sv, x)) for x in ret]
                    sc = int(rng.binomial(sv, c))
                    scv = int(rng.binomial(sc, r["cvr"]))
                    delays = rng.exponential(p["delay_mean_days"], size=scv)
                    ok = (delays <= ATTRIBUTION_DAYS) & (d + delays <= report_day)
                    conv_ok = int(ok.sum())
                    vals = rng.lognormal(math.log(p["aov_mean"]) - p["aov_sigma"] ** 2 / 2, p["aov_sigma"], size=conv_ok)
                    v3 += sv
                    qs = [a + b for a, b in zip(qs, sq)]
                    clicks += sc
                    conv += conv_ok
                    conv_late += scv - conv_ok
                    rev += float(vals.sum())
                    D = g.format.duration_s
                    watch += sv * (3 + sum(ret) / 4 * max(D - 3, 0)) + (n - sv) * 1.2
                row.update(views_3s=v3, q25=qs[0], q50=qs[1], q75=qs[2], q100=qs[3], link_clicks=clicks,
                           conversions=conv, revenue=round(rev, 2))
                daily.append(row)
                for k in tot:
                    tot[k] += row.get(k, 0)
                cum_reach = reach
            tot["reach"] = cum_reach
            m = derive(tot)
            m["avg_watch_s"] = watch / max(tot["impressions"], 1)
            rec = ResultRecord(source="simulated", variant="a", date_start=f"sim-day-{self.day}",
                               date_end=f"sim-day-{self.day + days - 1}", attribution_window_days=ATTRIBUTION_DAYS,
                               window_closed=report_day >= days + ATTRIBUTION_DAYS - 1,
                               metrics={k: round(v, 6) for k, v in m.items()}, is_simulated=True,
                               raw={"daily": daily, "generation": generation, "scenario": self.sc.name,
                                    "report_after_days": report_day, "days": days})
            rows.append({"genome_id": g.id, "variant": "a", "record": rec.model_dump()})
        self.day += days
        return rows

    def fetch(self, **kwargs: Any) -> list[dict]:
        return self.launch(**kwargs)

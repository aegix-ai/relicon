"""Closed-loop evaluation on the simulated market. This is the ONLY place allowed to touch the oracle.
All numbers produced here are SIMULATED."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from ..genome import space
from ..genome.models import Genome, ResultRecord
from ..genome.priors import template_genome
from ..learning.data import Observation
from ..learning.director import MockDirector
from ..learning.engine import Learner
from ..pipeline.planner import plan
from ..providers.mock import MockText
from ..simulator.market import SimulatedMarket
from ..simulator.oracle import best_genome
from ..simulator.scenarios import Scenario

METHODS = ("relicon", "random", "template", "llm_only")
COPY_FIELDS = ["text.cta_text", "text.caption_style", "text.text_density", "text.cta_time_s"]
_MT = MockText()
_ORACLE: dict = {}


def oracle(m: SimulatedMarket, gen: int) -> float:
    key = (m.sc.name, m.truth_for(gen) is m._drift)
    if key not in _ORACLE:
        _ORACLE[key] = best_genome(m, gen, restarts=3)[1]
    return _ORACLE[key]


@dataclass
class Run:
    scenario: str
    method: str
    seed: int
    variant: str = "base"
    gens: list[dict] = field(default_factory=list)
    secs: float = 0.0


def propose(method: str, lr: Learner | None, sc: Scenario, rng, gen: int, k: int, director) -> list[Genome]:
    b = sc.brief
    if method == "random":
        return [space.sample(b, rng, gen) for _ in range(k)]
    if method == "template":
        base = template_genome(b)
        return [base if i == 0 else space.mutate(base, rng, 2, COPY_FIELDS) for i in range(k)]
    if method == "llm_only":
        return director.prior_batch(b, k, rng, gen)
    if lr is not None and any(o.genome.brief.niche == b.niche for o in lr.obs):
        return lr.next_batch(k, rng, gen, f"p{gen:04d}")
    first = MockDirector().prior_batch(b, k, rng, gen)  # cold start: same starting point as llm_only
    for g in first:
        g.identity.policy_version, g.identity.selection_reason = "priors", "cold start: best-practice variations"
    return first


def run(sc: Scenario, method: str, seed: int, gens: int = 12, k: int = 8, budget: float = 150.0,
        noise: str = "normal", drift_at: int | None = None, history: list[Observation] | None = None,
        variant: str = "base", director=None) -> tuple[Run, list[Observation]]:
    t0 = time.time()
    rng = np.random.default_rng(seed)
    m = SimulatedMarket(sc, seed=seed, noise=noise, drift_at=drift_at)
    director = director or MockDirector()
    obs: list[Observation] = list(history or [])
    lr = Learner(sc.brief) if method == "relicon" else None
    out = Run(sc.name, method, seed, variant)
    cum_imp = 0.0
    best_obs: tuple[float, Genome] | None = None
    for gen in range(gens):
        if lr is not None:
            lr.fit(obs)
        batch = [plan(g, _MT) for g in propose(method, lr, sc, rng, gen, k, director)]
        rows = m.launch(batch, budget_per_ad=budget, generation=gen)
        new = [Observation(g, ResultRecord.model_validate(r["record"])) for g, r in zip(batch, rows)]
        obs += new
        cum_imp += sum(o.impressions for o in new)
        orc = oracle(m, gen)
        vals = [m.expected_value(g, gen) for g in batch]
        # recommended ad: relicon uses its posterior mean; baselines pick the best observed ROAS so far
        if lr is not None:
            lr.fit(obs)
            rec = lr.best()
        else:
            for o in new:
                r = o.record.metrics.get("roas", 0)
                if best_obs is None or r > best_obs[0]:
                    best_obs = (r, o.genome)
            rec = best_obs[1]
        out.gens.append({"gen": gen, "oracle": orc, "batch_mean": float(np.mean(vals)) / orc,
                         "best_in_batch": max(vals) / orc, "recommended": m.expected_value(rec, gen) / orc,
                         "regret": float(np.mean([orc - v for v in vals])), "impressions": cum_imp,
                         "observed_roas": float(np.mean([o.record.metrics.get("roas", 0) for o in new]))})
    out.secs = time.time() - t0
    return out, [o for o in obs if o.genome.brief.niche == sc.niche]

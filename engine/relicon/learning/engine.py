"""Learning engine API.

In memory (used by the eval harness):   Learner(brief).fit(observations).next_batch(...)
Store backed (used by CLI, server, pipeline): learn(store, niche), next_for(store, brief, k), propose_for_brief(...)
"""
from __future__ import annotations

import numpy as np

from ..config import get_settings
from ..genome.models import Brief, Genome
from . import bandit, credit, fatigue, insights, policy
from .data import OBJECTIVE_STEPS, Observation, from_store
from .director import MockDirector
from .model import FunnelModel


class Learner:
    def __init__(self, brief: Brief, floor: int | None = None, exploration_share: float | None = None,
                 objective: str | None = None, director=None):
        s = get_settings()
        self.brief = brief
        self.floor = s.min_impressions if floor is None else floor
        self.exploration_share = s.exploration_share if exploration_share is None else exploration_share
        self.objective = objective or brief.objective if (objective or brief.objective) in OBJECTIVE_STEPS else "roas"
        self.director = director or MockDirector()
        self.obs: list[Observation] = []
        self.model: FunnelModel | None = None

    def fit(self, observations: list[Observation]) -> "Learner":
        self.obs = observations
        self.model = FunnelModel(self.brief, observations, self.floor)
        return self

    def own(self) -> list[Observation]:
        return [o for o in self.obs if o.genome.brief.niche == self.brief.niche]

    def economics(self) -> dict:
        mine = [o for o in self.own() if o.record.window_closed] or self.own()
        m = lambda k: sum(o.record.metrics.get(k, 0) for o in mine)  # noqa: E731
        return {"aov": m("revenue") / m("conversions") if m("conversions") else None,
                "cpm": m("spend") * 1000 / m("impressions") if m("impressions") else None}

    def next_batch(self, k: int, rng: np.random.Generator, generation: int = 0, policy_version: str = "p0000",
                   suggest: int = 0) -> list[Genome]:
        assert self.model is not None, "fit() first"
        hist = [o.genome for o in self.own() if o.usable(self.floor)]
        extra = self.director.suggest(self.brief, self.insights(generation), suggest, rng) if suggest else []
        return bandit.next_batch(self.model, self.brief, hist, rng, k, self.objective, self.exploration_share,
                                 generation=generation, policy_version=policy_version, extra=extra,
                                 economics=self.economics())

    def best(self) -> Genome | None:
        """Recommended ad: highest posterior mean among launched genomes with enough data."""
        hist = [o.genome for o in self.own() if o.usable(self.floor)]
        if not hist or self.model is None:
            return None
        from . import features
        s = self.model.score(features.encode_many(hist), OBJECTIVE_STEPS[self.objective])
        return hist[int(np.argmax(s))]

    def insights(self, generation: int = 0) -> list[dict]:
        sim = any(o.record.is_simulated for o in self.obs)
        return insights.extract(self.model, generation, sim) if self.model else []

    def summary(self, generation: int = 0) -> dict:
        m = self.model
        return {
            "objective": self.objective, "director": self.director.name,
            "n_obs": len(self.obs), "n_used": len(m.obs) if m else 0, "below_floor": m.excluded if m else 0,
            "steps": {st: {"n_obs": f.n_obs, "by_level(global,vertical,niche,brand)": f.n_by_level,
                           "sigma_ad": round(f.sigma_ad, 3)} for st, f in (m.fits.items() if m else [])},
            "scene_credit": credit.scene_credit(self.own()),
            "fatigue": fatigue.estimate(self.own()),
            "insights": self.insights(generation)[:25],
            "is_simulated": any(o.record.is_simulated for o in self.obs),
        }


# ---- store-backed ------------------------------------------------------------------------------
def brief_for(store, niche: str) -> Brief:
    docs = [d for d in store.list("genome", niche=niche)] or [d for d in store.list("genome") if d["brief"]["niche"] == niche]
    if not docs:
        raise KeyError(f"no genomes for niche {niche!r}")
    return Genome.model_validate(docs[-1]).brief


def learn(store, niche: str, generation: int | None = None) -> dict:
    b = brief_for(store, niche)
    obs = from_store(store, vertical=None)
    lr = Learner(b).fit(obs)
    gen = generation if generation is not None else max((o.genome.identity.generation for o in lr.own()), default=0)
    summ = lr.summary(gen)
    for ins in summ["insights"]:
        store.put("insight", ins["id"], ins, niche=niche)
    return policy.snapshot(store, niche, {"obs_ids": [o.obs_id for o in lr.model.obs], "generation": gen,
                                          "summary": summ, "is_simulated": summ["is_simulated"]})


def _fit_active(store, b: Brief) -> Learner:
    obs = from_store(store)
    pol = policy.active(store, b.niche)
    if pol:
        keep = set(pol["obs_ids"])
        obs = [o for o in obs if o.obs_id in keep]
    return Learner(b).fit(obs)


def next_for(store, b: Brief, k: int = 8, seed: int = 0, director=None) -> list[Genome]:
    lr = _fit_active(store, b)
    if director is not None:
        lr.director = director
    pol = policy.active(store, b.niche)
    gen = 1 + max((o.genome.identity.generation for o in lr.own()), default=-1)
    return lr.next_batch(k, np.random.default_rng(seed), gen, pol["version"] if pol else "priors",
                         suggest=0 if lr.director.is_mock else k)


def propose_for_brief(b: Brief, store) -> Genome | None:
    """One genome for a single-ad request: the top Thompson pick if this niche has data, else None (template)."""
    if store is None or policy.active(store, b.niche) is None:
        return None
    gs = next_for(store, b, k=1)
    return gs[0] if gs else None

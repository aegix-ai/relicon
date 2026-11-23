"""Oracle, for evaluation only: the best genome the hidden truth allows for a scenario.
Coordinate ascent over every learnable field with random restarts. Never used by learning."""
from __future__ import annotations

import numpy as np

from ..genome import space
from ..genome.models import Genome
from ..genome.priors import template_genome
from .market import SimulatedMarket


def _candidates(f: space.LField, brief) -> list:
    if f.kind == "cat":
        return list(space.allowed_choices(f, brief))
    if f.kind == "multi":
        ch = list(f.choices)
        return [[c] for c in ch] + [sorted([a, b]) for i, a in enumerate(ch) for b in ch[i + 1:]]
    grid = np.linspace(f.lo, f.hi, 9)
    return [int(round(x)) for x in grid] if f.kind == "int" else [round(float(x), 3) for x in grid]


def best_genome(market: SimulatedMarket, generation: int = 0, restarts: int = 6, seed: int = 0) -> tuple[Genome, float]:
    rng = np.random.default_rng(seed)
    brief = market.sc.brief
    starts = [template_genome(brief)] + [space.sample(brief, rng) for _ in range(restarts)]
    best, best_v = None, -1.0
    for g in starts:
        v = market.expected_value(g, generation)
        for _ in range(4):
            improved = False
            for f in space.learnable_fields():
                for val in _candidates(f, brief):
                    c = g.model_copy(deep=True)
                    space.put(c, f.path, val)
                    c.normalize()
                    cv = market.expected_value(c, generation)
                    if cv > v + 1e-12:
                        g, v, improved = c, cv, True
            if not improved:
                break
        if v > best_v:
            best, best_v = g, v
    return best, best_v

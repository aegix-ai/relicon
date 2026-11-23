"""Genome -> feature vector. One-hot for categories, multi-hot (averaged) for sets, x and x^2 for numbers."""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from ..genome import space
from ..genome.models import Genome


@lru_cache(maxsize=1)
def layout() -> tuple[list[str], dict[str, tuple[int, int]]]:
    names, spans = ["intercept"], {}
    for f in space.learnable_fields():
        start = len(names)
        if f.kind in ("cat", "multi"):
            names += [f"{f.path}={c}" for c in f.choices]
        else:
            names += [f"{f.path}", f"{f.path}^2"]
        spans[f.path] = (start, len(names))
    return names, spans


def dim() -> int:
    return len(layout()[0])


def _x(f: space.LField, v) -> float:
    if f.kind == "frac":
        return float(v) - 0.5
    return (float(v) - f.lo) / (f.hi - f.lo) - 0.5 if f.hi > f.lo else 0.0


def encode(g: Genome) -> np.ndarray:
    names, spans = layout()
    x = np.zeros(len(names))
    x[0] = 1.0
    for f in space.learnable_fields():
        a, _ = spans[f.path]
        v = space.get(g, f.path)
        if f.kind == "cat":
            x[a + list(f.choices).index(v)] = 1.0
        elif f.kind == "multi":
            for item in v:
                x[a + list(f.choices).index(item)] = 1.0 / max(len(v), 1)
        else:
            t = _x(f, v)
            x[a], x[a + 1] = t, t * t - 1 / 12
    return x


def encode_many(gs: list[Genome]) -> np.ndarray:
    return np.stack([encode(g) for g in gs]) if gs else np.zeros((0, dim()))

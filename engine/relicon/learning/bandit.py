"""Thompson-sampling batch with a diversity penalty and an exploration share. Every pick gets a reason."""
from __future__ import annotations

import numpy as np

from ..genome import space
from ..genome.models import Brief, Genome
from ..genome.priors import template_genome
from . import features
from .data import OBJECTIVE_STEPS
from .director import diff
from .model import FunnelModel


def candidates(brief: Brief, parents: list[Genome], rng: np.random.Generator, extra: list[Genome],
               launched: set, n_mut: int = 40, n_rand: int = 10) -> list[Genome]:
    pool = list(extra)
    for p in parents:
        for _ in range(n_mut):
            pool.append(space.mutate(p, rng, int(rng.integers(1, 3))))
    for i in range(len(parents)):
        for j in range(i + 1, len(parents)):
            for _ in range(4):
                pool.append(space.crossover(parents[i], parents[j], rng))
    pool += [space.sample(brief, rng) for _ in range(n_rand)] + [template_genome(brief)]
    seen, out = set(launched), []
    for g in pool:
        fp = space.fingerprint(g)
        if fp not in seen:
            seen.add(fp)
            out.append(g)
    return out


def next_batch(model: FunnelModel, brief: Brief, history: list[Genome], rng: np.random.Generator, k: int = 8,
               objective: str = "roas", exploration_share: float = 0.25, diversity: float = 0.15, radius: int = 4,
               generation: int = 0, policy_version: str = "p0000", extra: list[Genome] | None = None,
               economics: dict | None = None) -> list[Genome]:
    steps = OBJECTIVE_STEPS[objective]
    by_id = {g.id: g for g in history}
    if history:
        Xh = features.encode_many(history)
        order = np.argsort(-model.score(Xh, steps))
        parents = [history[i] for i in order[:5]]
    else:
        parents = [template_genome(brief)]
    pool = candidates(brief, parents, rng, extra or [], {space.fingerprint(g) for g in history})
    X = features.encode_many(pool)
    mean = model.score(X, steps)
    unc = model.uncertainty(X, steps)
    picked: list[int] = []

    fps = [space.fingerprint(g) for g in pool]
    nf = len(fps[0]) if fps else 1

    def penalty(i: int) -> float:
        """Penalize near-duplicates of picks in this batch (fewer than `radius` fields apart)."""
        if not picked:
            return 0.0
        d = min(sum(a != b for a, b in zip(fps[i], fps[j])) for j in picked)
        return diversity * max(0.0, 1 - d / radius)

    n_explore = int(round(k * exploration_share)) if history else 0
    n_ts = k - n_explore
    for r in range(n_ts):
        betas = {st: model.draw(rng, st) for st in steps}
        s = model.score(X, steps, betas)
        adj = s - np.array([penalty(i) for i in range(len(pool))])
        adj[picked] = -np.inf
        i = int(np.argmax(adj))
        picked.append(i)
        _reason(pool[i], "thompson", f"draw {r + 1}: ranked first of {len(pool)} candidates", mean[i], unc[i],
                parents, by_id, economics)
    ok = mean >= np.median(mean)
    for r in range(n_explore):
        adj = np.where(ok, unc, -np.inf) - np.array([penalty(i) for i in range(len(pool))])
        adj[picked] = -np.inf
        i = int(np.argmax(adj))
        picked.append(i)
        _reason(pool[i], "explore", "highest uncertainty among above-median candidates", mean[i], unc[i], parents,
                by_id, economics)
    out = []
    for i in picked:
        g = pool[i]
        g.identity.generation, g.identity.policy_version = generation, policy_version
        out.append(g)
    return out


def _reason(g: Genome, kind: str, why: str, mean: float, unc: float, parents, by_id, economics) -> None:
    parent = by_id.get(g.identity.parent_ids[0]) if g.identity.parent_ids else None
    parent = parent or next((p for p in parents if g.identity.parent_ids and p.id == g.identity.parent_ids[0]), None)
    pred = ""
    if economics and economics.get("aov") and economics.get("cpm"):
        roas = 1000 * np.exp(mean) * economics["aov"] / economics["cpm"]
        pred = f"; predicted ROAS {roas:.2f} (x{np.exp(-1.645 * unc):.2f} to x{np.exp(1.645 * unc):.2f})"
    ch = diff(g, parent)
    lineage = f"; vs parent {parent.id}: " + ", ".join(ch[:4]) + ("..." if len(ch) > 4 else "") if parent else \
        "; new genome (no parent)"
    prior = g.identity.selection_reason
    g.identity.selection_reason = f"{kind}: {why}{pred}{lineage}" + (f"; {prior}" if prior.startswith("director") else "")

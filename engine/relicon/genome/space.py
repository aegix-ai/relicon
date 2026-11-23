"""The learnable search space, read from the genome's field tags."""
from __future__ import annotations

import copy
import typing
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Literal, get_args, get_origin

import numpy as np
from pydantic import BaseModel

from .models import DURATIONS, PLATFORM_MAX_S, TAG, Brief, Genome, cta_bounds


@dataclass(frozen=True)
class LField:
    path: str
    kind: str              # cat | multi | num | int | frac
    choices: tuple = ()
    lo: float = 0.0
    hi: float = 1.0
    max_items: int = 2

    @property
    def group(self) -> str:
        return self.path.split(".")[0]


def _bounds(finfo) -> tuple[float, float]:
    lo, hi = 0.0, 1.0
    for m in finfo.metadata:
        if hasattr(m, "ge"):
            lo = float(m.ge)
        if hasattr(m, "le"):
            hi = float(m.le)
    return lo, hi


def _walk(model: type[BaseModel], prefix: str, out: list[LField]) -> None:
    hints = typing.get_type_hints(model)
    for name, finfo in model.model_fields.items():
        ann = hints[name]
        path = f"{prefix}{name}"
        if isinstance(ann, type) and issubclass(ann, BaseModel):
            _walk(ann, path + ".", out)
            continue
        extra = finfo.json_schema_extra or {}
        if not isinstance(extra, dict) or extra.get(TAG) != "learnable":
            continue
        if path == "format.duration_s":
            out.append(LField(path, "cat", DURATIONS))
        elif path == "text.cta_time_s":
            out.append(LField(path, "frac", lo=0.0, hi=1.0))
        elif get_origin(ann) is Literal:
            out.append(LField(path, "cat", get_args(ann)))
        elif ann is bool:
            out.append(LField(path, "cat", (False, True)))
        elif get_origin(ann) is list:
            out.append(LField(path, "multi", get_args(get_args(ann)[0]), max_items=2))
        elif ann in (int, float):
            lo, hi = _bounds(finfo)
            out.append(LField(path, "int" if ann is int else "num", lo=lo, hi=hi))
        else:
            raise TypeError(f"untyped learnable field {path}: {ann}")


@lru_cache(maxsize=1)
def learnable_fields() -> tuple[LField, ...]:
    out: list[LField] = []
    _walk(Genome, "", out)
    return tuple(out)


def field_by_path(path: str) -> LField:
    return next(f for f in learnable_fields() if f.path == path)


def tag_map() -> dict[str, str]:
    """path -> tag for every tagged leaf field (used by tests and docs)."""
    res: dict[str, str] = {}

    def walk(model, prefix):
        hints = typing.get_type_hints(model)
        for name, finfo in model.model_fields.items():
            ann = hints[name]
            if isinstance(ann, type) and issubclass(ann, BaseModel):
                walk(ann, f"{prefix}{name}.")
                continue
            extra = finfo.json_schema_extra
            if isinstance(extra, dict) and TAG in extra:
                res[f"{prefix}{name}"] = extra[TAG]
    walk(Genome, "")
    return res


def get(g: Genome, path: str) -> Any:
    obj: Any = g
    for p in path.split("."):
        obj = getattr(obj, p)
    if path == "text.cta_time_s":
        lo, hi = cta_bounds(g.format.duration_s)
        return (obj - lo) / (hi - lo)
    return obj


def put(g: Genome, path: str, value: Any) -> None:
    parts = path.split(".")
    obj: Any = g
    for p in parts[:-1]:
        obj = getattr(obj, p)
    if path == "text.cta_time_s":
        lo, hi = cta_bounds(g.format.duration_s)
        value = round(lo + float(value) * (hi - lo), 2)
    setattr(obj, parts[-1], value)


def allowed_choices(f: LField, brief: Brief) -> tuple:
    if f.path == "format.duration_s":
        return tuple(d for d in f.choices if d <= PLATFORM_MAX_S[brief.platform])
    return f.choices


def random_value(f: LField, rng: np.random.Generator, brief: Brief) -> Any:
    if f.kind == "cat":
        ch = allowed_choices(f, brief)
        return ch[rng.integers(len(ch))]
    if f.kind == "multi":
        k = int(rng.integers(1, f.max_items + 1))
        return sorted(rng.choice(list(f.choices), size=k, replace=False).tolist())
    v = rng.uniform(f.lo, f.hi)
    return int(round(v)) if f.kind == "int" else round(float(v), 3)


def sample(brief: Brief, rng: np.random.Generator, generation: int = 0) -> Genome:
    g = Genome(brief=brief.model_copy())
    g.identity.generation = generation
    # duration first so cta fraction resolves against the final duration
    order = sorted(learnable_fields(), key=lambda f: f.path != "format.duration_s")
    for f in order:
        put(g, f.path, random_value(f, rng, brief))
    return g.normalize()


def mutate(g: Genome, rng: np.random.Generator, n_fields: int = 2, paths: list[str] | None = None) -> Genome:
    child = clone(g)
    fields = [field_by_path(p) for p in paths] if paths else list(learnable_fields())
    for i in rng.choice(len(fields), size=min(n_fields, len(fields)), replace=False):
        f = fields[int(i)]
        frac = get(child, "text.cta_time_s")
        put(child, f.path, random_value(f, rng, g.brief))
        if f.path == "format.duration_s":
            put(child, "text.cta_time_s", frac)
    child.identity.parent_ids = [g.id]
    return child.normalize()


def crossover(a: Genome, b: Genome, rng: np.random.Generator) -> Genome:
    child = clone(a)
    for f in learnable_fields():
        if rng.random() < 0.5:
            put(child, f.path, copy.deepcopy(get(b, f.path)))
    child.identity.parent_ids = [a.id, b.id]
    return child.normalize()


def clone(g: Genome) -> Genome:
    """Deep copy with a fresh identity, no scenes, production or results."""
    data = g.model_dump()
    data.pop("identity"); data.pop("scenes"); data.pop("production"); data.pop("results")
    c = Genome.model_validate(data)
    c.identity.generation = g.identity.generation
    return c


def fingerprint(g: Genome) -> tuple:
    return tuple(str(get(g, f.path)) if f.kind in ("cat", "multi") else round(float(get(g, f.path)), 1)
                 for f in learnable_fields())


def distance(a: Genome, b: Genome) -> float:
    """Share of learnable fields that differ (0 = same genome, 1 = nothing shared)."""
    fa, fb = fingerprint(a), fingerprint(b)
    return sum(x != y for x, y in zip(fa, fb)) / len(fa)

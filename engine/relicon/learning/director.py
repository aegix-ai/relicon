"""Creative director: proposes ideas and writes reasons. The posterior decides which ideas launch.

MockDirector  - zero-key, rule-based. As the "LLM-only" baseline (D8) it samples best-practice variations
                of the template with no data.
ClaudeDirector - claude-opus-5-5 (role "director") suggests genomes as JSON; every value is validated
                 against the genome space. Needs ANTHROPIC_API_KEY; not exercised in CI.
"""
from __future__ import annotations

import json

import numpy as np

from ..genome import space
from ..genome.models import Brief, Genome
from ..genome.priors import template_genome
from ..providers.base import TextProvider

CREATIVE_FIELDS = ["hook.hook_type", "hook.first_frame_subject", "narrative.angle", "narrative.tone", "visual.style",
                   "visual.setting", "audio.music.genre", "text.cta_text", "format.structure",
                   "offer_mechanics.discount_pct"]


def diff(child: Genome, parent: Genome | None) -> list[str]:
    if parent is None:
        return []
    out = []
    for f in space.learnable_fields():
        a, b = space.get(parent, f.path), space.get(child, f.path)
        if (f.kind in ("cat", "multi") and a != b) or (f.kind not in ("cat", "multi") and abs(float(a) - float(b)) > 1e-6):
            out.append(f"{f.path}: {a} -> {b}" if f.kind in ("cat", "multi") else f"{f.path}: {float(a):g} -> {float(b):g}")
    return out


class MockDirector:
    name = "mock-director (rule-based, no LLM)"
    is_mock = True

    def suggest(self, brief: Brief, insights: list[dict], k: int, rng: np.random.Generator) -> list[Genome]:
        return []

    def prior_batch(self, brief: Brief, k: int, rng: np.random.Generator, generation: int = 0) -> list[Genome]:
        """LLM-only baseline without a key: best-practice template plus 2-4 plausible creative changes."""
        out = []
        for _ in range(k):
            g = space.mutate(template_genome(brief), rng, int(rng.integers(2, 5)), CREATIVE_FIELDS)
            g.identity.generation = generation
            g.identity.policy_version = "llm_only(mock)"
            g.identity.selection_reason = "llm-only baseline: best-practice variation, no performance data"
            out.append(g)
        return out


class ClaudeDirector(MockDirector):
    name = "claude-opus-5-5 (director role)"
    is_mock = False

    def __init__(self, llm: TextProvider):
        self.llm = llm

    def _ask(self, brief: Brief, insights: list[dict], k: int) -> list[dict]:
        from ..providers.anthropic import parse_json
        fields = {f.path: (list(space.allowed_choices(f, brief)) if f.kind in ("cat", "multi") else [f.lo, f.hi])
                  for f in space.learnable_fields()}
        prompt = (f"Brief: {brief.model_dump_json()}\nKnown effects (90% CI excludes zero): "
                  f"{json.dumps([i['text'] for i in insights[:15]])}\nAllowed values per field: {json.dumps(fields)}\n"
                  f"Propose {k} distinct ad genomes as a JSON list of objects mapping field path -> value, plus a "
                  f"'why' key. text.cta_time_s is a fraction 0-1 of the allowed CTA window.")
        data = parse_json(self.llm.complete("You are a performance creative director.", prompt, 4000, role="director"))
        return data if isinstance(data, list) else data.get("genomes", [])

    def suggest(self, brief: Brief, insights: list[dict], k: int, rng: np.random.Generator) -> list[Genome]:
        out = []
        for spec in self._ask(brief, insights, k):
            g = template_genome(brief)
            for f in space.learnable_fields():
                v = spec.get(f.path)
                if v is None:
                    continue
                ok = (f.kind == "cat" and v in space.allowed_choices(f, brief)) or \
                     (f.kind == "multi" and isinstance(v, list) and set(v) <= set(f.choices) and v) or \
                     (f.kind in ("num", "int", "frac") and isinstance(v, (int, float)) and f.lo <= v <= f.hi)
                if ok:
                    space.put(g, f.path, v)
            g.identity.selection_reason = f"director idea: {spec.get('why', '')}"[:300]
            out.append(g.normalize())
        return out

    def prior_batch(self, brief: Brief, k: int, rng: np.random.Generator, generation: int = 0) -> list[Genome]:
        gs = self.suggest(brief, [], k, rng)
        for g in gs:
            g.identity.generation, g.identity.policy_version = generation, "llm_only(claude-opus-5-5)"
        return gs or super().prior_batch(brief, k, rng, generation)


def make(llm: TextProvider | None):
    return ClaudeDirector(llm) if llm is not None and not llm.is_mock else MockDirector()

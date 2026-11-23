"""HIDDEN TRUTH for the simulated market. Learning code must never import this module
(enforced by tests/test_boundary.py).

Per scenario, generated from a seed:
- funnel response functions (hook, hold, click per 3 s view, cvr) over genome fields,
  built as vertical effects + niche deviations + platform deviations (so niches in one
  vertical share structure and partial pooling has something real to find)
- a few interactions, 3 audience segments with their own deviations
- scene-beat hazard multipliers that shape the retention curve
- creative fatigue (frequency and age), conversion delay, lognormal order values, CPM, audience size
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import numpy as np

from ...genome import space
from ...genome.models import Genome

STEP_FIELDS = {
    "hook": ["hook.hook_type", "hook.first_frame_subject", "hook.motion_intensity", "hook.sound_cue", "visual.style",
             "visual.human_presence", "visual.palette", "visual.lighting", "audio.music.energy"],
    "hold": ["format.duration_s", "format.structure", "format.avg_shot_length_s", "narrative.tone",
             "narrative.emotional_arc", "audio.voice.pace_wpm", "audio.voice.energy", "audio.voice.accent",
             "audio.music.genre", "audio.music.bpm", "audio.music.volume_ratio", "visual.camera_motion",
             "visual.setting", "text.caption_style", "audio.sfx_density"],
    "click": ["text.cta_text", "text.cta_time_s", "text.end_card", "text.text_density", "narrative.angle",
              "offer_mechanics.discount_pct", "offer_mechanics.urgency", "visual.product_screen_time_pct",
              "narrative.proof_types", "hook.hook_type", "format.duration_s"],
    "cvr": ["offer_mechanics.discount_pct", "offer_mechanics.guarantee", "offer_mechanics.urgency", "narrative.angle",
            "narrative.proof_types", "visual.product_screen_time_pct"],
}
BASE = {"hook": 0.26, "hold": 0.30, "click": 0.035, "cvr": 0.035}
SCALE = {"hook": 1.0, "hold": 1.0, "click": 1.0, "cvr": 0.7}
EFFECT = float(__import__("os").environ.get("RELICON_SIM_EFFECT", "0.3"))  # tuned so oracle ROAS is a few x the median ad
CPM = {"tiktok": 9.0, "meta_reels": 11.0, "meta_feed": 13.0, "youtube_shorts": 7.0, "youtube_instream": 15.0}
BEATS = ["hook", "problem", "solution", "proof", "cta", "setup", "conflict", "turn", "resolution", "demo_step",
         "result", "item", "old_way", "new_way", "testimonial", "founder_why", "build", "unbox", "reveal", "use",
         "agitate", "solve"]


def _stable(parts: Any) -> int:
    import hashlib
    return int(hashlib.sha256(json.dumps(parts).encode()).hexdigest()[:12], 16)


def _norm(f: space.LField, v: Any) -> float:
    if f.kind == "frac":
        return float(v)
    return (float(v) - f.lo) / (f.hi - f.lo) if f.hi > f.lo else 0.0


@dataclass
class Truth:
    scenario: str
    params: dict

    # ---- funnel --------------------------------------------------------------------------
    def _field_effect(self, step: str, path: str, g: Genome, seg: int | None) -> float:
        e = self.params["effects"][step].get(path)
        if e is None:
            return 0.0
        f = space.field_by_path(path)
        v = space.get(g, path)
        if path == "format.duration_s":
            return e["slope"] * math.log(v / 15.0) + e["levels"].get(str(v), 0.0)
        if f.kind == "cat":
            val = e["levels"].get(str(v), 0.0)
        elif f.kind == "multi":
            items = [e["levels"].get(str(x), 0.0) for x in v]
            val = sum(items) / max(len(items), 1) + (e.get("pair_bonus", 0.0) if len(items) == 2 else 0.0)
        else:
            x = _norm(f, v)
            val = -e["a"] * (x - e["opt"]) ** 2 + e["b"] * (x - 0.5)
        if seg is not None:
            val += self.params["segments"][seg]["dev"].get(f"{step}|{path}|{v}", 0.0)
        return val

    def logit(self, step: str, g: Genome, seg: int | None = None) -> float:
        z = self.params["base"][step]
        for path in self.params["effects"][step]:
            z += self._field_effect(step, path, g, seg)
        for it in self.params["interactions"][step]:
            a, b = str(space.get(g, it["a"])), str(space.get(g, it["b"]))
            z += it["table"].get(f"{a}|{b}", 0.0)
        return z

    def rates(self, g: Genome) -> dict[str, float]:
        """Segment-weighted expected rates (no noise, no fatigue)."""
        out = {"hook": 0.0, "hold": 0.0, "click": 0.0, "cvr": 0.0, "hcv": 0.0}
        for s, seg in enumerate(self.params["segments"]):
            r = {k: 1 / (1 + math.exp(-self.logit(k, g, s))) for k in ("hook", "hold", "click", "cvr")}
            w = seg["weight"]
            for k in r:
                out[k] += w * r[k]
            out["hcv"] += w * r["hook"] * r["click"] * r["cvr"]
        return out

    def expected_roas(self, g: Genome) -> float:
        p = self.params
        return 1000 * self.rates(g)["hcv"] * p["aov_mean"] / p["cpm"]

    def segment_rates(self, g: Genome) -> list[tuple[float, dict[str, float]]]:
        return [(seg["weight"], {k: 1 / (1 + math.exp(-self.logit(k, g, s))) for k in ("hook", "hold", "click", "cvr")})
                for s, seg in enumerate(self.params["segments"])]

    def beat_hazard(self, beat: str) -> float:
        return self.params["beat_hazard"].get(beat, 1.0)


def _build(scenario: str, niche: str, vertical: str, platform: str, seed: int, drift: bool = False) -> dict:
    rv, rn, rp = (np.random.default_rng(_stable(["v", vertical])), np.random.default_rng(_stable(["n", niche, seed])),
                  np.random.default_rng(_stable(["p", niche, platform, seed])))
    effects: dict[str, dict] = {}
    for step, paths in STEP_FIELDS.items():
        effects[step] = {}
        for path in paths:
            f = space.field_by_path(path)
            sig = float(rv.uniform(0.12, 0.45)) * SCALE[step] * EFFECT
            active = rv.random() < 0.7 or rn.random() < 0.3
            if not active:
                continue
            if path == "format.duration_s":
                slope = -float(rv.uniform(0.35, 0.8)) if step == "hold" else float(rv.uniform(0.0, 0.15))
                slope *= 1.25 if platform == "tiktok" and step == "hold" else 1.0
                effects[step][path] = {"slope": slope, "levels": {str(d): float(rn.normal(0, sig * 0.3)) for d in f.choices}}
            elif f.kind in ("cat", "multi"):
                lv = {str(c): float(rv.normal(0, sig) + rn.normal(0, sig * 0.5) + rp.normal(0, sig * 0.3)) for c in f.choices}
                mu = sum(lv.values()) / len(lv)
                e: dict[str, Any] = {"levels": {k: v - mu for k, v in lv.items()}}
                if f.kind == "multi":
                    e["pair_bonus"] = float(rn.normal(0, sig * 0.3))
                effects[step][path] = e
            else:
                effects[step][path] = {"a": float(rv.uniform(0.5, 2.0) * sig * 2 + rn.uniform(0, sig)),
                                       "opt": float(np.clip(rv.uniform(0.15, 0.85) + rn.normal(0, 0.1), 0.05, 0.95)),
                                       "b": float(rn.normal(0, sig * 0.5))}
    interactions: dict[str, list] = {}
    for step, paths in STEP_FIELDS.items():
        cats = [p for p in paths if space.field_by_path(p).kind == "cat" and p in effects[step] and p != "format.duration_s"]
        interactions[step] = []
        for _ in range(2 if len(cats) >= 2 else 0):
            a, b = rn.choice(cats, size=2, replace=False)
            fa, fb = space.field_by_path(str(a)), space.field_by_path(str(b))
            table = {f"{x}|{y}": float(rn.normal(0, 0.35 * EFFECT)) for x in fa.choices for y in fb.choices if rn.random() < 0.3}
            interactions[step].append({"a": str(a), "b": str(b), "table": table})
    w = rn.dirichlet([2.0, 2.0, 2.0])
    segments = []
    for k in range(3):
        dev = {}
        for path in rn.choice(STEP_FIELDS["hook"], size=3, replace=False):
            f = space.field_by_path(str(path))
            if f.kind == "cat":
                for c in f.choices:
                    dev[f"hook|{path}|{c}"] = float(rn.normal(0, 0.3 * EFFECT))
        segments.append({"weight": float(w[k]), "dev": dev})
    base = {k: math.log(v / (1 - v)) + float(rn.normal(0, 0.25)) for k, v in BASE.items()}
    if drift:  # the niche changes taste mid-run: the strongest hook and click effects flip
        rd = np.random.default_rng(_stable(["drift", scenario]))
        for step in ("hook", "click"):
            for path, e in effects[step].items():
                if "levels" in e and path != "format.duration_s":
                    e["levels"] = {k: -v * float(rd.uniform(0.8, 1.2)) for k, v in e["levels"].items()}
    return {
        "scenario": scenario, "base": base, "effects": effects, "interactions": interactions, "segments": segments,
        "beat_hazard": {b: float(np.exp(rn.normal(0, 0.3))) for b in BEATS},
        "fatigue_k_freq": float(rn.uniform(0.04, 0.14)), "fatigue_k_age": float(rn.uniform(0.01, 0.04)),
        "delay_mean_days": float(rn.uniform(0.8, 3.0)), "aov_mean": 0.0, "aov_sigma": float(rn.uniform(0.3, 0.6)),
        "cpm": CPM[platform] * float(rn.uniform(0.75, 1.35)), "audience": float(rn.uniform(0.6e6, 3e6)),
        "ad_sigma": 0.15,
    }


@lru_cache(maxsize=64)
def load(scenario: str, niche: str, vertical: str, platform: str, seed: int, price_point: float,
         drift: bool = False) -> Truth:
    params = _build(scenario, niche, vertical, platform, seed, drift)
    params["aov_mean"] = price_point * float(np.random.default_rng(_stable(["aov", scenario, seed])).uniform(1.0, 1.6))
    return Truth(scenario, params)

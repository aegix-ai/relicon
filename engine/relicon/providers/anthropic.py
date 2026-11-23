"""Anthropic Messages API (text + vision judge). Plain httpx, no SDK needed.

Model roles (owner spec): sonnet = planning, opus = creative director, haiku = cheap judging.
Prices: relicon/providers/prices.py (read from the Anthropic pricing page on 2026-11-23).
"""
from __future__ import annotations

import base64
import json
import re
import time
from pathlib import Path
from typing import Any

import httpx

from .base import JudgeProvider, TextProvider
from .prices import price

API = "https://api.anthropic.com/v1/messages"
ROLE_MODELS = {"planner": "claude-sonnet-5-5", "director": "claude-opus-5-5", "judge": "claude-haiku-5-5"}


class AnthropicText(TextProvider):
    name, paid = "anthropic", True

    def __init__(self, key: str):
        super().__init__()
        self.key = key
        self.model = ROLE_MODELS["planner"]
        self.calls: list[dict] = []

    def _post(self, model: str, system: str, content: Any, max_tokens: int) -> str:
        body = {"model": model, "max_tokens": max_tokens, "system": system,
                "messages": [{"role": "user", "content": content}]}
        headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
        for attempt in range(4):
            r = httpx.post(API, json=body, headers=headers, timeout=180)
            if r.status_code in (429, 500, 502, 503, 529) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            r.raise_for_status()
            data = r.json()
            u = data.get("usage", {})
            cost = (u.get("input_tokens", 0) * price(f"{model}:in") + u.get("output_tokens", 0) * price(f"{model}:out")) / 1e6
            self.last_cost_usd += cost
            self.calls.append({"model": model, "usage": u, "cost_usd": round(cost, 5)})
            return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")
        raise RuntimeError("anthropic: retries exhausted")

    def complete(self, system: str, prompt: str, max_tokens: int = 2000, role: str = "planner") -> str:
        return self._post(ROLE_MODELS[role], system, prompt, max_tokens)

    def estimate(self, in_tokens: int, out_tokens: int, role: str = "planner") -> float:
        m = ROLE_MODELS[role]
        return (in_tokens * price(f"{m}:in") + out_tokens * price(f"{m}:out")) / 1e6


def parse_json(text: str) -> Any:
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    raw = m.group(1) if m else text[text.find("{") if "{" in text else 0:]
    return json.loads(raw)


RUBRIC = """Score 1-5 each: hook_strength (first 3 s stops the scroll), clarity (product and offer obvious),
brand_safety, cta_clarity, visual_quality. Then for every genome field given, say what you observe
and whether it matches. Answer ONLY JSON: {"rubric": {...}, "fields": {"<path>": {"observed": "...", "match": true|false|null}}}"""


class ClaudeJudge(JudgeProvider):
    """Vision judge on extracted frames (claude-haiku-5-5)."""
    name, paid = "anthropic", True
    model = ROLE_MODELS["judge"]
    FIELDS = ["hook.hook_type", "hook.first_frame_subject", "visual.style", "visual.human_presence",
              "visual.setting", "visual.palette", "text.end_card", "text.cta_text", "text.caption_style"]

    def __init__(self, key: str):
        super().__init__()
        self.text = AnthropicText(key)

    def judge(self, video: Path, genome: Any, frames: list[Path]) -> dict[str, Any]:
        from ..genome import space
        expected = {p: str(space.get(genome, p)) for p in self.FIELDS}
        content: list[dict] = []
        for f in frames[:8]:
            content.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                        "data": base64.b64encode(f.read_bytes()).decode()}})
        content.append({"type": "text", "text": f"Frames are in time order. CTA at {genome.text.cta_time_s}s. "
                                                f"Genome fields to check: {json.dumps(expected)}\n{RUBRIC}"})
        out = parse_json(self.text._post(self.model, "You are a strict ad QA reviewer.", content, 1200))
        self.last_cost_usd = self.text.last_cost_usd
        fields = {p: {"expected": expected[p], **out.get("fields", {}).get(p, {"observed": None, "match": None})}
                  for p in self.FIELDS}
        return {"judge": self.model, "fields": fields, "rubric": out.get("rubric", {})}

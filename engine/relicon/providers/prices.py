"""Provider prices. Only `verified=True` entries were read from the provider's own page.

The cost planner refuses a paid render that needs an unverified price unless the owner sets
RELICON_PRICE_OVERRIDE_<KEY> (USD per unit).
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Price:
    unit: str
    usd: float | None
    source: str
    checked: str
    verified: bool
    note: str = ""


ANTHROPIC = "https://platform.claude.com/docs/en/about-claude/pricing.md"
MINIMAX = "https://platform.minimax.io/docs/guides/pricing-video.md"
ELEVEN = "https://elevenlabs.io/pricing/api"
LUMA = "https://lumalabs.ai/dream-machine/pricing"

PRICES: dict[str, Price] = {
    # LLMs, USD per million tokens
    "claude-opus-5-5:in": Price("mtok", 4.0, ANTHROPIC, "2026-11-23", True),
    "claude-opus-5-5:out": Price("mtok", 20.0, ANTHROPIC, "2026-11-23", True),
    "claude-sonnet-5-5:in": Price("mtok", 2.0, ANTHROPIC, "2026-11-23", True),
    "claude-sonnet-5-5:out": Price("mtok", 10.0, ANTHROPIC, "2026-11-23", True),
    "claude-haiku-5-5:in": Price("mtok", 0.10, ANTHROPIC, "2026-11-23", True, "prompts up to 100k tokens"),
    "claude-haiku-5-5:out": Price("mtok", 0.50, ANTHROPIC, "2026-11-23", True, "prompts up to 100k tokens"),
    # Video, USD per clip or per second
    "MiniMax-Hailuo-02:768P:6s": Price("clip", 0.28, MINIMAX, "2026-11-23", True, "listed under Legacy"),
    "MiniMax-Hailuo-02:768P:10s": Price("clip", 0.56, MINIMAX, "2026-11-23", True, "listed under Legacy"),
    "MiniMax-Hailuo-2.3-Fast:768P:6s": Price("clip", 0.19, MINIMAX, "2026-11-23", True, "listed under Legacy"),
    "MiniMax-H3:768P": Price("second", 0.08, MINIMAX, "2026-11-23", True),
    "MiniMax-H3-Lite:768P": Price("second", 0.04, MINIMAX, "2026-11-23", True),
    "image-01": Price("image", 0.0035, MINIMAX, "2026-11-23", True, "listed under Legacy"),
    "luma:ray-2:720p": Price("second", None, LUMA, "2026-11-23", False,
                             "API billing page unreadable; third-party quotes $0.15-$0.35/s disagree"),
    # Audio
    "elevenlabs:multilingual": Price("kchar", 0.08, ELEVEN, "2026-11-23", True),
    "elevenlabs:flash": Price("kchar", 0.04, ELEVEN, "2026-11-23", True),
    "elevenlabs:music": Price("minute", 0.15, ELEVEN, "2026-11-23", True),
    "elevenlabs:sfx": Price("minute", 0.12, ELEVEN, "2026-11-23", True),
}


class UnverifiedPrice(RuntimeError):
    pass


def price(key: str) -> float:
    env = "RELICON_PRICE_OVERRIDE_" + "".join(c if c.isalnum() else "_" for c in key).upper()
    if os.getenv(env):
        return float(os.environ[env])
    p = PRICES[key]
    if not p.verified or p.usd is None:
        raise UnverifiedPrice(f"price for {key} is not verified ({p.note}); set {env} to use it")
    return p.usd


def table() -> list[dict]:
    return [{"key": k, **p.__dict__} for k, p in PRICES.items()]

"""Step 5: cost plan per stage, from provider prices. Refuses before any paid call."""
from __future__ import annotations

import math

from ..genome.models import Genome
from ..providers.prices import UnverifiedPrice, price
from ..providers.registry import ProviderSet
from .jobs import NonRetryable


class BudgetExceeded(NonRetryable):
    pass


def clip_lengths(g: Genome, max_clip_s: float) -> list[float]:
    out: list[float] = []
    for s in g.scenes:
        L = s.end_s - s.start_s + 0.5
        k = max(1, math.ceil(L / max_clip_s))
        out += [L / k] * k
    return out


def vo_chars(g: Genome) -> int:
    return sum(len(s.vo_line) for s in g.scenes) if g.audio.voice.accent != "none" else 0


def plan_cost(g: Genome, ps: ProviderSet, budget_usd: float | None, draft: bool = False) -> dict:
    n = len(g.scenes)
    lines: list[dict] = []

    def add(stage: str, p, usd: float) -> None:
        lines.append({"stage": stage, "provider": p.name, "model": p.model, "estimated_usd": round(usd, 4)})

    try:
        add("planning", ps.text, ps.text.estimate(3000 + 200 * n, 400 + 120 * n))
        add("keyframes", ps.image, ps.image.estimate(n))
        add("voice", ps.voice, ps.voice.estimate(vo_chars(g)))
        if not draft:
            add("video", ps.video, ps.video.estimate(clip_lengths(g, ps.video.max_clip_s)))
            add("music", ps.music, ps.music.estimate(g.format.duration_s))
            add("sfx", ps.sfx, ps.sfx.estimate(2.0))
            add("judge", ps.judge, 0.0 if not ps.judge.paid else
                ps.judge.text.estimate(1800 * min(n + 1, 8), 1200, role="judge"))
    except UnverifiedPrice as e:
        raise BudgetExceeded(f"refused: {e}") from e
    total = round(sum(x["estimated_usd"] for x in lines), 4)
    plan = {"stages": lines, "total_estimated_usd": total, "budget_usd": budget_usd, "paid": ps.any_paid,
            "real_equivalent_usd": real_equivalent(g), "draft": draft}
    if ps.any_paid:
        if not budget_usd or budget_usd <= 0:
            raise BudgetExceeded("refused: paid providers need a job budget (--budget)")
        if total > budget_usd:
            raise BudgetExceeded(f"refused: estimate ${total:.2f} is over budget ${budget_usd:.2f}")
    return plan


def real_equivalent(g: Genome) -> dict:
    """What this ad would cost on the default real stack (verified prices only)."""
    clips = clip_lengths(g, 10.0)
    video = sum(price(f"MiniMax-Hailuo-02:768P:{6 if c <= 6 else 10}s") for c in clips)
    voice = vo_chars(g) / 1000 * price("elevenlabs:multilingual")
    n = len(g.scenes)
    text = ((3000 + 200 * n) * price("claude-sonnet-5-5:in") + (400 + 120 * n) * price("claude-sonnet-5-5:out")) / 1e6
    judge = (1800 * min(n + 1, 8) * price("claude-haiku-5-5:in") + 1200 * price("claude-haiku-5-5:out")) / 1e6
    total = video + voice + text + judge
    return {"stack": "MiniMax-Hailuo-02 768P + ElevenLabs multilingual + claude-sonnet-5-5 + claude-haiku-5-5 judge",
            "video_usd": round(video, 3), "voice_usd": round(voice, 4), "llm_usd": round(text + judge, 4),
            "total_usd": round(total, 3), "per_second_usd": round(total / g.format.duration_s, 4)}

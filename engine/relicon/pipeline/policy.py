"""Step 9: ad policy check. Flags risky claims, likeness without consent, unlicensed music,
and sets the AI-content disclosure each platform asks for.

Platform rules here are a conservative summary of each platform's AI-content and ad policies;
they were not re-checked against the live policy pages on 2026-11-23. Treat as a screen, not legal advice.
"""
from __future__ import annotations

import re

from ..genome.models import Genome

PATTERNS = {
    "health_claim": r"\b(cures?|treats?|heals?|clinically|doctor[- ]?approved|weight ?loss|lose \d+|detox|anxiety|diabetes|immun\w*)\b",
    "finance_claim": r"\b(guaranteed (returns|income|profit)|get rich|risk[- ]free|double your money|passive income)\b",
    "guarantee_claim": r"\b(guarantee[ds]?|money[- ]back)\b",
    "before_after": r"\bbefore,? and after\b|\bbefore/after\b",
    "unsubstantiated_stat": r"\b(\d+%|most people|thousands of|#1|number one)\b",
    "superlative": r"\b(best|changes everything|only \w+ you need)\b",
}
SENSITIVE_VERTICALS = {"health", "finance", "beauty"}

DISCLOSURE = {
    "tiktok": {"label": "AI-generated content", "how": "turn on the AIGC label when posting or in Ads Manager"},
    "meta_feed": {"label": "AI info", "how": "set the AI disclosure in Ads Manager for photorealistic AI media"},
    "meta_reels": {"label": "AI info", "how": "set the AI disclosure in Ads Manager for photorealistic AI media"},
    "youtube_shorts": {"label": "altered or synthetic content", "how": "tick the disclosure in YouTube Studio / Google Ads"},
    "youtube_instream": {"label": "altered or synthetic content", "how": "tick the disclosure in Google Ads"},
}


def check(g: Genome) -> tuple[list[dict], dict]:
    flags: list[dict] = []
    sensitive = g.brief.vertical in SENSITIVE_VERTICALS
    texts = [(s.scene_id, f"{s.vo_line} {s.on_screen_text}") for s in g.scenes] + [("hook", g.hook.on_screen_text)]
    for sid, t in texts:
        for kind, pat in PATTERNS.items():
            for m in re.finditer(pat, t, re.I):
                sev = "review"
                if kind in ("health_claim", "finance_claim") or (kind == "before_after" and sensitive):
                    sev = "block" if sensitive else "review"
                if kind == "superlative":
                    sev = "info"
                flags.append({"kind": kind, "severity": sev, "where": sid, "text": m.group(0)})
    if "before_after" in g.narrative.proof_types:
        flags.append({"kind": "before_after", "severity": "block" if sensitive else "review", "where": "narrative",
                      "text": "proof_types includes before_after"})
    if g.offer_mechanics.guarantee != "none":
        flags.append({"kind": "guarantee_terms", "severity": "review", "where": "offer",
                      "text": f"{g.offer_mechanics.guarantee}: end card must show terms"})
    people = [a for s in g.scenes for a in s.reference_assets if a.startswith("person:")]
    if people and not g.production.qc.get("likeness_consent"):
        flags.append({"kind": "likeness_without_consent", "severity": "block", "where": "scenes",
                      "text": f"real-person references {people} need likeness_consent=true"})
    if not g.audio.music.license and g.audio.music.genre != "none":
        flags.append({"kind": "music_unlicensed", "severity": "block", "where": "audio", "text": "music.license empty"})
    disclosure = {"ai_generated": True, "platform": g.brief.platform, **DISCLOSURE[g.brief.platform],
                  "checked_against_live_policy": False}
    return flags, disclosure


def blocked(flags: list[dict]) -> bool:
    return any(f["severity"] == "block" for f in flags)

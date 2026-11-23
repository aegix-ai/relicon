"""Cold-start priors: a common best-practice template per platform (also the 'fixed template' baseline).
These are generic direct-response conventions, not learned values."""
from __future__ import annotations

from .models import Brief, Genome

TEMPLATE = {
    "format": {"duration_s": 15, "structure": "hook_problem_solution_cta", "avg_shot_length_s": 2.5},
    "hook": {"hook_type": "problem_shot", "first_frame_subject": "face", "motion_intensity": "high", "sound_cue": "voice_first"},
    "narrative": {"angle": "pain", "tone": "energetic", "emotional_arc": "fall_rise", "proof_types": ["demo", "testimonial"]},
    "visual": {"style": "ugc_look", "palette": "warm", "lighting": "natural", "camera_motion": "handheld",
               "human_presence": "single_person", "product_screen_time_pct": 40, "setting": "home"},
    "audio": {"voice": {"energy": "high", "pace_wpm": 165, "accent": "neutral_us"},
              "music": {"genre": "pop", "bpm": 120, "energy": "medium", "volume_ratio": 0.15}, "sfx_density": "low"},
    "text": {"caption_style": "bold_word_by_word", "text_density": "medium", "cta_text": "Shop now", "cta_time_s": 12.0, "end_card": True},
    "offer_mechanics": {"discount_pct": 15, "guarantee": "none", "urgency": "limited_time"},
}
PLATFORM_TWEAKS = {
    "youtube_instream": {"format": {"duration_s": 30}, "visual": {"style": "cinematic"}, "text": {"cta_time_s": 24.0}},
    "meta_feed": {"format": {"duration_s": 15}, "text": {"caption_style": "subtitle_bar"}},
}


def _merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = _merge(out.get(k, {}), v) if isinstance(v, dict) else v
    return out


def template_genome(brief: Brief, duration_s: int | None = None) -> Genome:
    data = _merge(TEMPLATE, PLATFORM_TWEAKS.get(brief.platform, {}))
    g = Genome.model_validate({**data, "brief": brief.model_dump()})
    if duration_s:
        frac = (g.text.cta_time_s) / g.format.duration_s
        g.format.duration_s = duration_s
        g.text.cta_time_s = frac * duration_s
    g.identity.policy_version = "priors"
    g.identity.selection_reason = "cold start: best-practice template (no data yet)"
    return g.normalize()

"""Creative Genome v1. One genome fully describes one ad.

Every leaf field carries a tag in its JSON Schema (`x-relicon-tag`):
  learnable - the learning engine may change it
  fixed     - set by the brief
  derived   - computed by the pipeline (plans, production, results)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = "genome.v1"
TAG = "x-relicon-tag"


def L(default: Any = ..., **kw: Any) -> Any:
    return Field(default, json_schema_extra={TAG: "learnable"}, **kw)


def F(default: Any = ..., **kw: Any) -> Any:
    return Field(default, json_schema_extra={TAG: "fixed"}, **kw)


def D(default: Any = ..., **kw: Any) -> Any:
    return Field(default, json_schema_extra={TAG: "derived"}, **kw)


Platform = Literal["meta_feed", "meta_reels", "tiktok", "youtube_shorts", "youtube_instream"]
Objective = Literal["roas", "cpa", "ctr", "awareness"]
Structure = Literal["hook_problem_solution_cta", "story", "demo", "listicle", "comparison",
                    "testimonial_style", "founder_story", "unboxing", "problem_agitate_solve"]
HookType = Literal["question", "bold_claim", "pattern_interrupt", "problem_shot", "result_first",
                   "social_proof", "curiosity_gap"]
Level = Literal["low", "medium", "high"]
Angle = Literal["pain", "desire", "status", "savings", "convenience", "fear_of_missing_out"]
Tone = Literal["energetic", "calm", "humorous", "serious", "warm", "urgent"]
Arc = Literal["rise", "fall_rise", "flat_high", "tension_release"]
Proof = Literal["testimonial", "demo", "stat", "expert", "ugc_review", "before_after"]
Style = Literal["ugc_look", "cinematic", "studio_product", "animation", "mixed"]
DURATIONS = (6, 10, 15, 20, 30, 45, 60, 90, 120, 180, 300)
CTA_TEXTS = ("Shop now", "Learn more", "Get yours", "Try it free", "Order today")

# Aspect ratio follows the platform placement (derived, not learnable).
PLATFORM_ASPECT = {"meta_feed": "4:5", "meta_reels": "9:16", "tiktok": "9:16",
                   "youtube_shorts": "9:16", "youtube_instream": "16:9"}
PLATFORM_MAX_S = {"meta_feed": 240, "meta_reels": 90, "tiktok": 300, "youtube_shorts": 60,
                  "youtube_instream": 300}


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Identity(_M):
    genome_id: str = D(default_factory=lambda: uuid.uuid4().hex[:12])
    parent_ids: list[str] = D(default_factory=list)
    generation: int = D(0, ge=0)
    policy_version: str = D("priors")
    created_at: str = D(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    selection_reason: str = D("")


class Brief(_M):
    product: str = F()
    offer: str = F("")
    price_point: float = F(30.0, ge=0)
    currency: str = F("USD")
    vertical: str = F("general")
    niche: str = F("general")
    brand: str = F("unbranded")
    audience_persona: str = F("")
    platform: Platform = F("tiktok")
    objective: Objective = F("roas")
    constraints: list[str] = F(default_factory=list)
    inferred_fields: list[str] = D(default_factory=list)


class Chapter(_M):
    title: str = D()
    start_s: float = D()
    end_s: float = D()


class Format(_M):
    duration_s: int = L(15, ge=6, le=300)
    aspect_ratio: Literal["9:16", "1:1", "4:5", "16:9"] = D("9:16")
    structure: Structure = L("hook_problem_solution_cta")
    scene_count: int = D(3, ge=1)
    avg_shot_length_s: float = L(3.0, ge=1.0, le=8.0)
    chapters: list[Chapter] = D(default_factory=list)


class Hook(_M):
    hook_type: HookType = L("question")
    first_frame_subject: Literal["product", "face", "hands", "text_card", "scene"] = L("product")
    on_screen_text: str = D("")
    motion_intensity: Level = L("medium")
    sound_cue: Literal["none", "whoosh", "beat_drop", "voice_first", "silence_break"] = L("voice_first")


class Narrative(_M):
    angle: Angle = L("pain")
    tone: Tone = L("energetic")
    emotional_arc: Arc = L("rise")
    claims: list[str] = D(default_factory=list)
    proof_types: list[Proof] = L(default_factory=lambda: ["demo"], max_length=2)


class Visual(_M):
    style: Style = L("ugc_look")
    palette: Literal["warm", "cool", "neutral", "high_contrast", "pastel"] = L("warm")
    lighting: Literal["natural", "studio", "low_key", "high_key", "neon"] = L("natural")
    camera_motion: Literal["static", "handheld", "slow_push", "dynamic_tracking"] = L("handheld")
    human_presence: Literal["none", "hands_only", "single_person", "group"] = L("single_person")
    product_screen_time_pct: float = L(35.0, ge=5, le=90)
    setting: Literal["home", "outdoor", "studio", "workplace", "store", "abstract"] = L("home")


class Voice(_M):
    energy: Level = L("medium")
    pace_wpm: int = L(150, ge=110, le=200)
    accent: Literal["neutral_us", "british", "australian", "none"] = L("neutral_us")


class Music(_M):
    genre: Literal["lofi", "pop", "hip_hop", "electronic", "acoustic", "cinematic_score", "none"] = L("pop")
    bpm: int = L(110, ge=60, le=160)
    energy: Level = L("medium")
    volume_ratio: float = L(0.2, ge=0.05, le=0.6)
    license: str = D("generated:mock")


class Audio(_M):
    voice: Voice = Field(default_factory=Voice)
    music: Music = Field(default_factory=Music)
    sfx_density: Literal["none", "low", "medium", "high"] = L("low")


class Text(_M):
    caption_style: Literal["none", "minimal", "bold_word_by_word", "subtitle_bar"] = L("bold_word_by_word")
    text_density: Level = L("medium")
    cta_text: Literal["Shop now", "Learn more", "Get yours", "Try it free", "Order today"] = L("Shop now")
    cta_time_s: float = L(12.0, ge=0)
    end_card: bool = L(True)


class OfferMechanics(_M):
    discount_pct: Literal[0, 10, 15, 20, 30] = L(0)
    guarantee: Literal["none", "money_back_30d", "free_returns"] = L("none")
    urgency: Literal["none", "limited_time", "limited_stock"] = L("none")


class SceneGenome(_M):
    scene_id: str = D()
    start_s: float = D(ge=0)
    end_s: float = D(gt=0)
    purpose: str = D()
    chapter: int = D(0)
    visual_prompt: str = D("")
    shot_type: Literal["close_up", "medium", "wide", "macro", "pov", "text_card"] = D("medium")
    model: str = D("")
    seed: int = D(0)
    reference_assets: list[str] = D(default_factory=list)
    vo_line: str = D("")
    on_screen_text: str = D("")
    transition: Literal["cut", "crossfade", "whip", "fade_black"] = D("cut")


class StageCost(_M):
    stage: str
    provider: str
    model: str
    estimated_usd: float = 0.0
    actual_usd: float = 0.0


class Production(_M):
    providers: dict[str, str] = D(default_factory=dict)
    cost_usd: list[StageCost] = D(default_factory=list)
    total_cost_usd: float = D(0.0)
    render_time_s: float = D(0.0)
    qc: dict[str, Any] = D(default_factory=dict)
    policy_flags: list[dict[str, Any]] = D(default_factory=list)
    ai_disclosure: dict[str, Any] = D(default_factory=dict)
    continuity_bible: dict[str, Any] = D(default_factory=dict)
    is_mock: bool = D(True)


class ResultRecord(_M):
    source: Literal["simulated", "csv_meta", "csv_tiktok", "api_meta", "api_tiktok"] = D()
    variant: str = D("a")
    date_start: str = D("")
    date_end: str = D("")
    attribution_window_days: int = D(7)
    window_closed: bool = D(True)
    metrics: dict[str, float] = D(default_factory=dict)
    is_simulated: bool = D()
    raw: dict[str, Any] = D(default_factory=dict)


class Genome(_M):
    schema_version: Literal["genome.v1"] = D(SCHEMA_VERSION)
    identity: Identity = Field(default_factory=Identity)
    brief: Brief
    format: Format = Field(default_factory=Format)
    hook: Hook = Field(default_factory=Hook)
    narrative: Narrative = Field(default_factory=Narrative)
    visual: Visual = Field(default_factory=Visual)
    audio: Audio = Field(default_factory=Audio)
    text: Text = Field(default_factory=Text)
    offer_mechanics: OfferMechanics = Field(default_factory=OfferMechanics)
    scenes: list[SceneGenome] = D(default_factory=list)
    production: Production = Field(default_factory=Production)
    results: list[ResultRecord] = D(default_factory=list)

    @property
    def id(self) -> str:
        return self.identity.genome_id

    def ad_name(self, variant: str = "a") -> str:
        """Every ad must be published under this name so results can be linked back."""
        return f"rlc_{self.id}_{variant}"

    def normalize(self) -> "Genome":
        """Apply derived constraints: aspect from platform, duration cap, CTA inside the ad."""
        b, f, t = self.brief, self.format, self.text
        f.aspect_ratio = PLATFORM_ASPECT[b.platform]
        f.duration_s = min(f.duration_s, PLATFORM_MAX_S[b.platform])
        f.scene_count = max(1, round(f.duration_s / f.avg_shot_length_s))
        t.cta_time_s = round(min(max(t.cta_time_s, 0.5 * f.duration_s), f.duration_s - 1.0), 2)
        if self.audio.voice.accent == "none" and t.caption_style == "none":
            t.caption_style = "minimal"  # an ad with no voice still needs words on screen
        return self

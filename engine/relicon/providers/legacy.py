"""Adapters that keep the original engine/providers clients behind the new interfaces."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from ..config import REPO_ROOT
from .base import VideoProvider, VoiceProvider
from .prices import price


def _legacy_path() -> None:
    p = str(REPO_ROOT / "engine")
    if p not in sys.path:
        sys.path.insert(0, p)


class ElevenLabsVoice(VoiceProvider):
    """engine/providers/elevenlabs.py (eleven_multilingual_v2), $0.08 per 1K chars (verified)."""
    name, model, paid = "elevenlabs", "eleven_multilingual_v2", True

    def __init__(self) -> None:
        super().__init__()
        _legacy_path()
        from providers.elevenlabs import ElevenLabsProvider  # type: ignore
        self.client = ElevenLabsProvider()

    def estimate(self, chars: int) -> float:
        return chars / 1000 * price("elevenlabs:multilingual")

    def speak(self, text: str, out: Path, voice: dict[str, Any]) -> Path:
        cfg = {"voice_tone": {"high": "energetic"}.get(voice.get("energy", "medium"), "professional"),
               "voice_gender": "female"}
        if not self.client.generate_audio(text, str(out), cfg):
            raise RuntimeError("elevenlabs generation failed")
        self.last_cost_usd += self.estimate(len(text))
        return out


class LumaVideo(VideoProvider):
    """engine/providers/luma.py (ray-2). Price unverified: blocked unless the owner sets an override."""
    name, model, paid = "luma", "ray-2", True
    max_clip_s = 5.0

    def __init__(self) -> None:
        super().__init__()
        _legacy_path()
        from providers.luma import LumaProvider  # type: ignore
        self.client = LumaProvider()

    def estimate(self, clip_seconds: list[float]) -> float:
        return sum(5.0 for _ in clip_seconds) * price("luma:ray-2:720p")

    def video(self, prompt: str, seconds: float, aspect: str, seed: int, out: Path,
              keyframe: Path | None, spec: dict[str, Any]) -> Path:
        url = self.client.generate_video(prompt, aspect_ratio=aspect)
        if not self.client.download_video(url, str(out)):
            raise RuntimeError("luma download failed")
        self.last_cost_usd += self.estimate([seconds])
        return out

"""Provider interfaces. Every model sits behind one of these.

Each provider reports `paid` and `estimate(...)` so the cost planner can enforce the budget
before anything is called, and `last_cost_usd` so the real cost gets logged.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class Provider(ABC):
    name: str = "base"
    model: str = ""
    paid: bool = False
    is_mock: bool = False

    def __init__(self) -> None:
        self.last_cost_usd = 0.0


class TextProvider(Provider):
    @abstractmethod
    def complete(self, system: str, prompt: str, max_tokens: int = 2000, role: str = "planner") -> str: ...

    def estimate(self, in_tokens: int, out_tokens: int) -> float:
        return 0.0


class ImageProvider(Provider):
    @abstractmethod
    def image(self, prompt: str, aspect: str, seed: int, out: Path, spec: dict[str, Any]) -> Path: ...

    def estimate(self, n_images: int) -> float:
        return 0.0


class VideoProvider(Provider):
    max_clip_s: float = 10.0
    aspects: tuple[str, ...] = ("9:16", "16:9", "1:1")
    image_to_video: bool = True

    @abstractmethod
    def video(self, prompt: str, seconds: float, aspect: str, seed: int, out: Path,
              keyframe: Path | None, spec: dict[str, Any]) -> Path: ...

    def estimate(self, clip_seconds: list[float]) -> float:
        return 0.0


class VoiceProvider(Provider):
    @abstractmethod
    def speak(self, text: str, out: Path, voice: dict[str, Any]) -> Path: ...

    def estimate(self, chars: int) -> float:
        return 0.0


class MusicProvider(Provider):
    @abstractmethod
    def music(self, seconds: float, out: Path, spec: dict[str, Any]) -> Path: ...

    def estimate(self, seconds: float) -> float:
        return 0.0


class SfxProvider(Provider):
    @abstractmethod
    def sfx(self, kind: str, seconds: float, out: Path) -> Path: ...

    def estimate(self, seconds: float) -> float:
        return 0.0


class JudgeProvider(Provider):
    @abstractmethod
    def judge(self, video: Path, genome: Any, frames: list[Path]) -> dict[str, Any]:
        """Return {"fields": {path: {"expected", "observed", "match": bool|None}}, "rubric": {...}}."""

"""Pick providers. Mock is the default; a paid provider needs its key AND a job budget."""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import Settings, get_settings
from . import mock
from .base import (ImageProvider, JudgeProvider, MusicProvider, SfxProvider, TextProvider, VideoProvider,
                   VoiceProvider)
from .judge import MeasuredJudge


class ProviderUnavailable(RuntimeError):
    pass


@dataclass
class ProviderSet:
    text: TextProvider
    image: ImageProvider
    video: VideoProvider
    voice: VoiceProvider
    music: MusicProvider
    sfx: SfxProvider
    judge: JudgeProvider
    notes: list[str] = field(default_factory=list)

    @property
    def all(self):
        return [self.text, self.image, self.video, self.voice, self.music, self.sfx, self.judge]

    @property
    def any_paid(self) -> bool:
        return any(p.paid for p in self.all)

    @property
    def is_mock(self) -> bool:
        return not self.any_paid

    def describe(self) -> dict[str, str]:
        return {k: f"{p.name}:{p.model}" for k, p in zip(
            ["text", "image", "video", "voice", "music", "sfx", "judge"], self.all)}


def mock_set() -> ProviderSet:
    return ProviderSet(mock.MockText(), mock.MockImage(), mock.MockVideo(), mock.MockVoice(),
                       mock.MockMusic(), mock.MockSfx(), MeasuredJudge())


def build(mode: str | None = None, s: Settings | None = None, video: str | None = None) -> ProviderSet:
    s = s or get_settings()
    mode = mode or s.providers
    ps = mock_set()
    if mode == "mock":
        return ps
    if s.anthropic_key:
        from .anthropic import AnthropicText, ClaudeJudge
        ps.text, ps.judge = AnthropicText(s.anthropic_key), ClaudeJudge(s.anthropic_key)
    else:
        ps.notes.append("no ANTHROPIC_API_KEY: rule-based planner and measured judge")
    video = video or ("minimax" if s.minimax_key else "luma" if s.luma_key else "")
    if video == "minimax":
        from .minimax import MinimaxVideo
        ps.video = MinimaxVideo(s.minimax_key)
    elif video == "luma":
        from .legacy import LumaVideo
        ps.video = LumaVideo()
    else:
        raise ProviderUnavailable("real mode needs HAILUO_API_KEY (MiniMax) or LUMA_API_KEY")
    if s.elevenlabs_key:
        from .legacy import ElevenLabsVoice
        ps.voice = ElevenLabsVoice()
    else:
        ps.notes.append("no ELEVENLABS_API_KEY: mock voice")
    ps.notes.append("music and sfx: local synthesis ($0, license generated:local)")
    return ps

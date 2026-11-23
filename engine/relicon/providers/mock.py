"""Mock providers. They make real, playable media with ffmpeg, offline, for $0.

Everything they render carries a visible MOCK label so nobody mistakes it for a real ad.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

from .. import media
from .base import ImageProvider, MusicProvider, SfxProvider, TextProvider, VideoProvider, VoiceProvider

PALETTES = {"warm": ("0xE8743B", "0xF6C85F"), "cool": ("0x1F6FB2", "0x6FD0C2"),
            "neutral": ("0x8A8A8A", "0xD9D4CC"), "high_contrast": ("0x111111", "0xF2E205"),
            "pastel": ("0xF7B7C6", "0xB8E1DD")}


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


class MockText(TextProvider):
    name, model, is_mock = "mock", "mock-text", True

    def complete(self, system: str, prompt: str, max_tokens: int = 2000, role: str = "planner") -> str:
        raise NotImplementedError("MockText has no model; pipeline steps use their rule-based path")


class MockImage(ImageProvider):
    name, model, is_mock = "mock", "mock-keyframe", True

    def image(self, prompt: str, aspect: str, seed: int, out: Path, spec: dict[str, Any]) -> Path:
        w, h = media.size_for(aspect, spec.get("short_side", 540))
        c0, c1 = PALETTES.get(spec.get("palette", "warm"), PALETTES["warm"])
        wd = out.parent / "txt"
        label = f"{spec.get('purpose', 'scene')} / {spec.get('shot_type', 'medium')}"
        fs = max(14, w // 22)
        vf = ",".join([
            f"drawbox=x={w*0.3:.0f}:y={h*0.38:.0f}:w={w*0.4:.0f}:h={h*0.24:.0f}:color=white@0.85:t=fill",
            media.drawtext(spec.get("subject", "product"), wd, x="(w-tw)/2", y=f"{h*0.48:.0f}", fontsize=fs, fontcolor="black"),
            media.drawtext(label, wd, x="(w-tw)/2", y=f"{h*0.12:.0f}", fontsize=fs, fontcolor="white"),
            media.drawtext("MOCK KEYFRAME", wd, x=12, y=12, fontsize=int(fs * 0.7), fontcolor="white@0.8")])
        shift = (seed % 11 - 5) * 30  # each scene gets its own hue so cuts are visible
        media.ff("-f", "lavfi", "-i", f"gradients=s={w}x{h}:c0={c0}:c1={c1}:seed={seed % 2**31}:n=2",
                 "-vf", f"hue=h={shift}:b={(seed % 5 - 2) * 0.6},{vf}", "-frames:v", "1", str(out))
        return out


class MockVideo(VideoProvider):
    """Ken Burns move over the keyframe; motion speed follows motion_intensity."""
    name, model, is_mock = "mock", "mock-video", True
    max_clip_s = 600.0
    aspects = ("9:16", "16:9", "1:1", "4:5")

    def video(self, prompt: str, seconds: float, aspect: str, seed: int, out: Path,
              keyframe: Path | None, spec: dict[str, Any]) -> Path:
        w, h = media.size_for(aspect, spec.get("short_side", 540))
        if keyframe is None:
            keyframe = out.with_suffix(".key.png")
            MockImage().image(prompt, aspect, seed, keyframe, spec)
        frames = max(1, int(math.ceil(seconds * media.FPS)))
        speed = {"low": 0.0008, "medium": 0.0018, "high": 0.0035}[spec.get("motion", "medium")]
        vf = (f"scale={w*2}:{h*2},zoompan=z='min(zoom+{speed},1.5)':d={frames}"
              f":x='iw/2-(iw/zoom/2)+sin(on/9)*{6 + seed % 7}':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps={media.FPS},"
              + media.drawtext("MOCK RENDER", out.parent / "txt", x=12, y="h-th-12", fontsize=max(12, w // 36),
                               fontcolor="white@0.7"))
        media.ff("-loop", "1", "-i", str(keyframe), "-vf", vf, "-t", f"{seconds:.3f}", "-r", str(media.FPS),
                 "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-an", str(out))
        return out


class MockVoice(VoiceProvider):
    """Syllable-rate tone bursts: real audio with the right timing, clearly not a human voice."""
    name, model, is_mock = "mock", "mock-voice", True

    def speak(self, text: str, out: Path, voice: dict[str, Any]) -> Path:
        words = max(1, len(text.split()))
        secs = words / (voice.get("pace_wpm", 150) / 60.0)
        f0 = {"low": 150, "medium": 190, "high": 230}[voice.get("energy", "medium")]
        rate = voice.get("pace_wpm", 150) / 60.0 * 1.4  # syllables per second
        expr = (f"0.45*sin(2*PI*({f0}+25*sin(2*PI*0.7*t))*t)*pow(abs(sin(PI*{rate:.3f}*t)),0.6)")
        media.ff("-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d={secs:.2f}", "-ac", "1", str(out))
        return out


class MockMusic(MusicProvider):
    name, model, is_mock = "mock", "mock-music", True

    def music(self, seconds: float, out: Path, spec: dict[str, Any]) -> Path:
        bpm = spec.get("bpm", 110)
        beat = 60.0 / bpm
        root = {"lofi": 196, "pop": 262, "hip_hop": 110, "electronic": 220, "acoustic": 247,
                "cinematic_score": 131}.get(spec.get("genre", "pop"), 262)
        amp = {"low": 0.15, "medium": 0.25, "high": 0.35}[spec.get("energy", "medium")]
        kick = f"0.8*exp(-18*mod(t,{beat:.4f}))*sin(2*PI*55*t)"
        chord = f"{amp}*(sin(2*PI*{root}*t)+0.6*sin(2*PI*{root*1.26:.1f}*t)+0.5*sin(2*PI*{root*1.5:.1f}*t))/2.1"
        media.ff("-f", "lavfi", "-i", f"aevalsrc='({kick}+{chord})*0.5':s=44100:d={seconds:.2f}",
                 "-ac", "2", str(out))
        return out


class MockSfx(SfxProvider):
    name, model, is_mock = "mock", "mock-sfx", True

    def sfx(self, kind: str, seconds: float, out: Path) -> Path:
        media.ff("-f", "lavfi", "-i", f"anoisesrc=d={seconds:.2f}:c=pink:a=0.4", "-af",
                 f"afade=t=in:d={seconds/2:.2f},afade=t=out:st={seconds/2:.2f}:d={seconds/2:.2f},"
                 "highpass=f=800", "-ac", "2", str(out))
        return out

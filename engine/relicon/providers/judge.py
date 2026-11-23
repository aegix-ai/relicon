"""Measured judge: checks genome fields that can be measured from the file with ffmpeg alone.

Fields it cannot measure (hook type, style, people on screen...) are reported as
match=None / "not_evaluated". With ANTHROPIC_API_KEY the Claude vision judge covers those.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .. import media
from .base import JudgeProvider


def color_track(video: Path) -> list[tuple[float, float, float, float]]:
    """(time, mean Y, mean U, mean V) at 4 samples per second, one decode pass."""
    log = media.ff_log("-i", str(video), "-vf", "fps=4,signalstats,metadata=print", "-an", "-f", "null", "-")
    ts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
    cols = [[float(x) for x in re.findall(rf"lavfi\.signalstats\.{k}AVG=([\d.]+)", log)] for k in "YUV"]
    return list(zip(ts, *cols))


def at(track: list[tuple], t: float) -> tuple:
    return min(track, key=lambda p: abs(p[0] - t))


def scene_cuts(video: Path, threshold: float = 0.04) -> list[float]:
    log = media.ff_log("-i", str(video), "-vf", f"select='gt(scene,{threshold})',metadata=print", "-an", "-f", "null", "-")
    return [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]


class MeasuredJudge(JudgeProvider):
    name, model, is_mock = "measured", "ffmpeg-measured-v1", True
    UNMEASURABLE = ["hook.hook_type", "hook.first_frame_subject", "visual.style", "visual.human_presence",
                    "visual.setting", "text.cta_text", "text.caption_style"]

    def judge(self, video: Path, genome: Any, frames: list[Path]) -> dict[str, Any]:
        info = media.probe(video)
        vs = next(s for s in info["streams"] if s["codec_type"] == "video")
        dur = float(vs.get("duration", info["format"]["duration"]))
        w, h = int(vs["width"]), int(vs["height"])
        a, b = media.ASPECTS[genome.format.aspect_ratio]
        from ..pipeline.assemble import XFADE
        cuts = scene_cuts(video)
        track = color_track(video)
        bounds = [s.start_s for s in genome.scenes[1:]]

        def changed(sc) -> bool:  # visible change across the boundary, any transition type
            d = XFADE[sc.transition][1]
            a, b = at(track, sc.start_s - d - 0.3), at(track, sc.start_s + 0.3)
            return sum(abs(x - y) for x, y in zip(a[1:], b[1:])) > 6
        hit = [any(abs(c - sc.start_s) <= 0.5 for c in cuts) or changed(sc) for sc in genome.scenes[1:]]
        recall = sum(hit) / len(hit) if hit else 1.0
        cta = genome.text.cta_time_s
        before = sorted(at(track, (s.start_s + s.end_s) / 2)[1] for s in genome.scenes if s.end_s <= cta)
        ref = before[len(before) // 2] if before else at(track, max(0.2, cta - 0.5))[1]
        ratio = at(track, min(cta + 0.6, dur - 0.2))[1] / max(ref, 1.0)
        fields: dict[str, dict[str, Any]] = {
            "format.duration_s": {"expected": genome.format.duration_s, "observed": round(dur, 2),
                                  "match": abs(dur - genome.format.duration_s) <= 0.6},
            "format.aspect_ratio": {"expected": genome.format.aspect_ratio, "observed": f"{w}x{h}",
                                    "match": abs(w / h - a / b) < 0.02},
            "format.scene_count": {"expected": len(genome.scenes), "observed": f"{len(cuts)} cuts, boundary recall {recall:.2f}",
                                   "match": recall >= 0.8},
        }
        fields["text.end_card"] = {"expected": genome.text.end_card, "observed": f"luma ratio after CTA {ratio:.2f}",
                                   "match": (ratio < 0.6) == genome.text.end_card}
        for p in self.UNMEASURABLE:
            fields[p] = {"expected": None, "observed": "not_evaluated (needs a vision model)", "match": None}
        return {"judge": self.model, "fields": fields, "rubric": {}, "note": "measured fields only"}

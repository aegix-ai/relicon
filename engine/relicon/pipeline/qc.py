"""Step 8: automated QC. Technical checks with ffmpeg, then the judge (genome fidelity)."""
from __future__ import annotations

import re
from pathlib import Path

from .. import media
from ..config import get_settings
from ..genome.models import Genome
from .assemble import XFADE


def _check(ok: bool, detail: object) -> dict:
    return {"pass": bool(ok), "detail": detail}


def black_intervals(video: Path) -> list[tuple[float, float]]:
    log = media.ff_log("-i", str(video), "-vf", "blackdetect=d=0.4:pix_th=0.08", "-an", "-f", "null", "-")
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]


def freeze_intervals(video: Path) -> list[float]:
    log = media.ff_log("-i", str(video), "-vf", "freezedetect=n=-60dB:d=2", "-an", "-f", "null", "-")
    return [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]


def loudness(video: Path) -> tuple[float, float]:
    log = media.ff_log("-i", str(video), "-af", "ebur128=peak=true", "-vn", "-f", "null", "-")
    summ = log[log.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    pk = re.search(r"Peak:\s+(-?[\d.inf]+) dBFS", summ)
    return i, float(pk.group(1)) if pk else -99.0


def technical(g: Genome, master: Path, boxes: list[dict], clips: list[Path]) -> tuple[dict, list[str]]:
    s = get_settings()
    checks: dict[str, dict] = {}
    streams = {st["codec_type"]: float(st.get("duration", 0)) for st in media.probe(master)["streams"]}
    vd, ad = streams.get("video", 0.0), streams.get("audio", 0.0)
    checks["duration"] = _check(abs(vd - g.format.duration_s) <= 0.5 and abs(ad - g.format.duration_s) <= 0.5,
                                {"expected": g.format.duration_s, "video": round(vd, 2), "audio": round(ad, 2)})
    fades = [sc.start_s for sc in g.scenes if sc.transition == "fade_black"]
    blacks = [iv for iv in black_intervals(master) if not any(iv[0] - 0.8 <= t <= iv[1] + 0.8 for t in fades)]
    checks["black_frames"] = _check(not blacks, blacks)
    frozen = freeze_intervals(master)
    checks["frozen_frames"] = _check(not frozen, frozen)
    lufs, peak = loudness(master)
    checks["loudness"] = _check(abs(lufs - s.lufs_target) <= 2.0, {"integrated_lufs": lufs, "target": s.lufs_target})
    checks["audio_clipping"] = _check(peak <= -0.1, {"true_peak_dbfs": peak})
    over = [b["text"] for b in boxes if (b["kind"] == "caption" and b["n_lines"] > 2) or b["w"] > b["safe"][2] - b["safe"][0] + 1]
    checks["caption_overflow"] = _check(not over, over[:5])
    outside = [b["text"] for b in boxes if b["x"] < b["safe"][0] - 1 or b["y"] < b["safe"][1] - 1
               or b["x"] + b["w"] > b["safe"][2] + 1 or b["y"] + b["h"] > b["safe"][3] + 1]
    checks["safe_zones"] = _check(not outside, outside[:5])
    bad_scenes = []
    for i, (sc, c) in enumerate(zip(g.scenes, clips)):
        need = sc.end_s - sc.start_s
        try:
            ok = media.duration(c) >= need - 0.05 and not black_intervals(c)
        except media.MediaError:
            ok = False
        if not ok:
            bad_scenes.append(sc.scene_id)
    checks["scene_clips"] = _check(not bad_scenes, bad_scenes)
    return checks, bad_scenes


def extract_frames(video: Path, g: Genome, wd: Path) -> list[Path]:
    wd.mkdir(parents=True, exist_ok=True)
    times = [0.5] + [(sc.start_s + sc.end_s) / 2 for sc in g.scenes[1:]]
    if len(times) > 8:
        times = [times[0]] + times[1::max(1, len(times) // 7)][:7]
    out = []
    for k, t in enumerate(times):
        f = wd / f"frame_{k:02d}.jpg"
        media.ff("-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=out_range=full,format=yuvj420p", "-q:v", "4", str(f))
        out.append(f)
    return out


def fidelity_score(judged: dict) -> dict:
    vals = [v["match"] for v in judged["fields"].values()]
    ev = [v for v in vals if v is not None]
    return {"evaluated": len(ev), "total": len(vals), "confirmed": sum(ev),
            "fidelity": round(sum(ev) / len(ev), 3) if ev else None, "coverage": round(len(ev) / len(vals), 3)}

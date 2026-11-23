"""Step 7: ffmpeg assembly.

- scene clips joined with xfade transitions (cut = one-frame fade), chunked for long ads
- VO placed per scene, music bed ducked under VO (sidechaincompress), whooshes on transitions
- loudness normalised to the configured integrated LUFS target (loudnorm)
- captions, hook text, on-screen text and end card burned in inside each platform's safe zone
- exports for 9:16, 1:1, 4:5 and 16:9
"""
from __future__ import annotations

from pathlib import Path

from .. import media
from ..config import get_settings
from ..genome.models import Genome

XFADE = {"cut": ("cut", 0.0), "crossfade": ("fade", 0.35), "whip": ("slideleft", 0.25),
         "fade_black": ("fadeblack", 0.5)}
# Conservative safe zones (fraction of frame kept clear: top, bottom, left, right), from the
# platforms' creative guides; UI overlays differ by app version, so these lean safe.
SAFE = {"tiktok": (0.10, 0.22, 0.06, 0.16), "meta_reels": (0.14, 0.22, 0.06, 0.08),
        "meta_feed": (0.05, 0.08, 0.05, 0.05), "youtube_shorts": (0.10, 0.20, 0.06, 0.14),
        "youtube_instream": (0.08, 0.14, 0.05, 0.05)}
EXPORT_ASPECTS = ("9:16", "1:1", "4:5", "16:9")
CHUNK = 20


def overlap(g: Genome, i: int) -> float:
    """Extra seconds clip i must have so the next transition does not shorten the ad."""
    return XFADE[g.scenes[i + 1].transition][1] if i + 1 < len(g.scenes) else 0.0


def join_clips(g: Genome, clips: list[Path], wd: Path, size: tuple[int, int]) -> Path:
    w, h = size
    parts: list[Path] = []
    for c0 in range(0, len(clips), CHUNK):
        idx = list(range(c0, min(c0 + CHUNK, len(clips))))
        args: list[str] = []
        fl: list[str] = []
        lens = []
        for k, i in enumerate(idx):
            sc = g.scenes[i]
            L = (sc.end_s - sc.start_s) + (overlap(g, i) if i != idx[-1] else 0.0)
            lens.append(L)
            args += ["-i", str(clips[i])]
            fl.append(f"[{k}:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={media.FPS},"
                      f"setsar=1,format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=0:{L:.3f},setpts=PTS-STARTPTS,fps={media.FPS}[c{k}]")
        last, acc = "c0", lens[0]
        for k in range(1, len(idx)):
            tr, d = XFADE[g.scenes[idx[k]].transition]
            if tr == "cut":
                fl.append(f"[{last}][c{k}]concat=n=2:v=1:a=0,fps={media.FPS}[x{k}]")
                acc += lens[k]
            else:
                off = acc - d
                fl.append(f"[{last}][c{k}]xfade=transition={tr}:duration={d:.3f}:offset={off:.3f},fps={media.FPS}[x{k}]")
                acc = off + lens[k]
            last = f"x{k}"
        out = wd / f"join_{c0:04d}.mp4"
        media.ff(*args, "-filter_complex", ";".join(fl), "-map", f"[{last}]", "-r", str(media.FPS),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(out))
        parts.append(out)
    if len(parts) == 1:
        return parts[0]
    lst = wd / "join.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    out = wd / "joined.mp4"
    media.ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out))
    return out


def mix_audio(g: Genome, vo: list[Path | None], music: Path | None, sfx: Path | None, wd: Path) -> Path:
    s = get_settings()
    T = float(g.format.duration_s)
    args: list[str] = []
    fl: list[str] = []
    fmt = "aformat=sample_fmts=fltp:sample_rates=44100:channel_layouts=stereo"
    n = 0
    labels = []
    for sc, p in zip(g.scenes, vo):
        L = sc.end_s - sc.start_s
        if p is None:
            args += ["-f", "lavfi", "-t", f"{L:.3f}", "-i", "anullsrc=r=44100:cl=stereo"]
        else:
            args += ["-i", str(p)]
        fl.append(f"[{n}:a]{fmt},atrim=0:{L:.3f},apad=whole_dur={L:.3f},asetpts=PTS-STARTPTS[v{n}]")
        labels.append(f"[v{n}]")
        n += 1
    fl.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1,asplit=2[vo][vosc]")
    mix = ["[vo]"]
    if music is not None and g.audio.music.genre != "none":
        args += ["-stream_loop", "-1", "-i", str(music)]
        fl.append(f"[{n}:a]{fmt},atrim=0:{T:.3f},volume={g.audio.music.volume_ratio * 2:.3f}[mus]")
        fl.append("[mus][vosc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=350[duck]")
        mix.append("[duck]")
        n += 1
    else:
        fl.append("[vosc]anullsink")
    times = [sc.start_s for sc in g.scenes[1:] if sc.transition != "cut"]
    every = {"none": 0, "low": 0, "medium": 3, "high": 1}[g.audio.sfx_density]
    if every:
        times += [sc.start_s for k, sc in enumerate(g.scenes[1:], 1) if sc.transition == "cut" and k % every == 0]
    times = sorted(t for t in times if t < T - 0.3)[:60] if g.audio.sfx_density != "none" else []
    if sfx is not None and times:
        args += ["-i", str(sfx)]
        fl.append(f"[{n}:a]{fmt},asplit={len(times)}" + "".join(f"[s{k}]" for k in range(len(times))))
        for k, t in enumerate(times):
            ms = max(0, int((t - 0.2) * 1000))
            fl.append(f"[s{k}]adelay={ms}|{ms},volume=0.5[sd{k}]")
        fl.append("".join(f"[sd{k}]" for k in range(len(times))) + f"amix=inputs={len(times)}:normalize=0[sfx]")
        mix.append("[sfx]")
    fl.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
              f"loudnorm=I={s.lufs_target}:TP={s.true_peak_db}:LRA=11,aresample=44100,atrim=0:{T:.3f}[aout]")
    out = wd / "mix.m4a"
    media.ff(*args, "-filter_complex", ";".join(fl), "-map", "[aout]", "-c:a", "aac", "-b:a", "160k", str(out))
    return out


def caption_chunks(g: Genome) -> list[tuple[float, float, str]]:
    """Timed caption chunks. bold_word_by_word shows 3 words at a time; others show the whole line."""
    if g.text.caption_style == "none":
        return []
    out = []
    for sc in g.scenes:
        words = sc.vo_line.split()
        if not words:
            continue
        a, b = sc.start_s, min(sc.end_s, g.text.cta_time_s if sc.purpose != "cta" else sc.end_s)
        if b - a < 0.3:
            continue
        step = 3 if g.text.caption_style == "bold_word_by_word" else max(len(words), 1)
        groups = [" ".join(words[i:i + step]) for i in range(0, len(words), step)]
        dt = (b - a) / len(groups)
        out += [(a + k * dt, a + (k + 1) * dt, t) for k, t in enumerate(groups)]
    return out


def layout(g: Genome, aspect: str, short_side: int) -> list[dict]:
    """Every text box with its rect, so QC can verify safe zones and overflow."""
    w, h = media.size_for(aspect, short_side)
    top, bottom, left, right = SAFE[g.brief.platform]
    sx0, sx1, sy0, sy1 = w * left, w * (1 - right), h * top, h * (1 - bottom)
    sw = sx1 - sx0
    boxes = []

    def box(text: str, a: float, b: float, fs: int, anchor: str, kind: str, color: str = "white") -> None:
        max_chars = max(8, int(sw / (fs * 0.56)))
        lines = media.wrap(text, max_chars)
        lh = int(fs * 1.25)
        bh = lh * len(lines)
        y0 = {"bottom": sy1 - bh, "top": sy0, "center": (sy0 + sy1) / 2 - bh / 2, "upper": sy0 + (sy1 - sy0) * 0.18}[anchor]
        for k, line in enumerate(lines):
            tw = len(line) * fs * 0.56
            x = sx0 + (sw - tw) / 2
            boxes.append({"kind": kind, "text": line, "t0": a, "t1": b, "fs": fs, "x": x, "y": y0 + k * lh,
                          "w": tw, "h": lh, "color": color, "n_lines": len(lines),
                          "safe": [sx0, sy0, sx1, sy1]})

    base = max(16, int(min(w, h) / 18))
    style = g.text.caption_style
    for a, b, t in caption_chunks(g):
        box(t, a, b, int(base * (1.35 if style == "bold_word_by_word" else 0.9)), "bottom", "caption")
    if g.hook.on_screen_text:
        box(g.hook.on_screen_text.upper(), 0.0, min(3.0, g.scenes[0].end_s), int(base * 1.3), "top", "hook", "yellow")
    for sc in g.scenes[1:]:
        if sc.on_screen_text and sc.purpose != "cta" and sc.end_s <= g.text.cta_time_s:
            box(sc.on_screen_text, sc.start_s, sc.end_s, int(base * 1.0), "upper", "scene_text")
    T = float(g.format.duration_s)
    box(g.text.cta_text.upper(), g.text.cta_time_s, T, int(base * 1.6), "center", "cta", "white")
    if g.text.end_card:
        box(g.brief.product, g.text.cta_time_s, T, int(base * 0.9), "upper", "end_card", "white")
        if g.offer_mechanics.discount_pct:
            box(f"{g.offer_mechanics.discount_pct}% OFF", g.text.cta_time_s, T, int(base * 1.1), "bottom", "end_card", "yellow")
    return boxes


def overlay_filters(g: Genome, boxes: list[dict], wd: Path, w: int, h: int) -> list[str]:
    f = []
    T = float(g.format.duration_s)
    if g.text.end_card:
        f.append(f"drawbox=x=0:y=0:w={w}:h={h}:color=black@0.62:t=fill:enable='between(t,{g.text.cta_time_s:.2f},{T:.2f})'")
    for b in boxes:
        sx0, sx1 = b["safe"][0], b["safe"][2]
        opts = {"x": f"'{sx0:.0f}+({sx1 - sx0:.0f}-tw)/2'", "y": f"{b['y']:.0f}", "fontsize": b["fs"], "fontcolor": b["color"],
                "borderw": max(2, b["fs"] // 12), "bordercolor": "black",
                "enable": f"'between(t,{b['t0']:.2f},{b['t1']:.2f})'"}
        if b["kind"] == "caption" and g.text.caption_style == "subtitle_bar":
            opts.update(box=1, boxcolor="black@0.55", boxborderw=8)
        f.append(media.drawtext(b["text"], wd / "txt", **opts))
    return f


def reframe(src_aspect: str, aspect: str, w: int, h: int) -> str:
    if src_aspect == aspect:
        return f"[0:v]scale={w}:{h},setsar=1[base]"
    return (f"[0:v]split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bg];"
            f"[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[base]")


def export(g: Genome, video: Path, audio: Path, aspect: str, short_side: int, out: Path, wd: Path) -> tuple[Path, list[dict]]:
    w, h = media.size_for(aspect, short_side)
    boxes = layout(g, aspect, short_side)
    filters = overlay_filters(g, boxes, wd, w, h)
    cur = video
    # Linux caps one argument at 128 KB, so very long ads burn text in batches.
    batches = [filters[i:i + 120] for i in range(0, len(filters), 120)] or [[]]
    for k, batch in enumerate(batches):
        first, last = k == 0, k == len(batches) - 1
        head = reframe(g.format.aspect_ratio, aspect, w, h) if first else "[0:v]null[base]"
        graph = head + (";[base]" + ",".join(batch) + "[v]" if batch else ";[base]null[v]")
        dst = out if last else wd / f"burn_{aspect.replace(':', 'x')}_{k}.mp4"
        ins = ["-i", str(cur)] + (["-i", str(audio)] if last else [])
        maps = ["-map", "[v]"] + (["-map", "1:a", "-c:a", "copy"] if last else ["-an"])
        media.ff(*ins, "-filter_complex", graph, *maps,
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                 "-t", f"{g.format.duration_s:.3f}", "-movflags", "+faststart", str(dst))
        cur = dst
    return out, boxes


def assemble(g: Genome, clips: list[Path], vo: list[Path | None], music: Path | None, sfx: Path | None,
             out_dir: Path, short_side: int, aspects: tuple[str, ...] = EXPORT_ASPECTS, prefix: str = "ad") -> dict:
    wd = out_dir / "work"
    wd.mkdir(parents=True, exist_ok=True)
    master_size = media.size_for(g.format.aspect_ratio, short_side)
    joined = join_clips(g, clips, wd, master_size)
    audio = mix_audio(g, vo, music, sfx, wd)
    outputs, layouts = {}, {}
    for a in aspects:
        p, boxes = export(g, joined, audio, a, short_side, out_dir / f"{prefix}_{a.replace(':', 'x')}.mp4", wd)
        outputs[a], layouts[a] = str(p), boxes
    return {"outputs": outputs, "layouts": layouts, "master": outputs.get(g.format.aspect_ratio, next(iter(outputs.values())))}

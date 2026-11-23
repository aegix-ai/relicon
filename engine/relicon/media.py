"""Small ffmpeg/ffprobe helpers shared by mock providers, assembly and QC."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

ASPECTS = {"9:16": (9, 16), "1:1": (1, 1), "4:5": (4, 5), "16:9": (16, 9)}
FPS = 25


class MediaError(RuntimeError):
    pass


def run(args: list[str], timeout: int = 900) -> str:
    if not shutil.which(args[0]):
        raise MediaError(f"{args[0]} not found; install ffmpeg")
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise MediaError(f"{' '.join(args[:6])}... failed: {p.stderr[-1500:]}")
    return p.stderr + p.stdout


def ff(*args: str, timeout: int = 900) -> str:
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", "-loglevel", "error", *args], timeout=timeout)


def ff_log(*args: str, timeout: int = 900) -> str:
    """Like ff() but keeps info-level stderr (for detect filters)."""
    return run(["ffmpeg", "-hide_banner", "-nostdin", "-y", *args], timeout=timeout)


def probe(path: str | Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    return json.loads(out[out.index("{"):])


def duration(path: str | Path) -> float:
    return float(probe(path)["format"]["duration"])


def size_for(aspect: str, short_side: int) -> tuple[int, int]:
    a, b = ASPECTS[aspect]
    if a <= b:
        w, h = short_side, short_side * b / a
    else:
        w, h = short_side * a / b, short_side
    return int(w) // 2 * 2, int(h) // 2 * 2


@lru_cache(maxsize=1)
def font_file() -> str:
    for c in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/liberation/LiberationSans-Bold.ttf"):
        if Path(c).exists():
            return c
    if shutil.which("fc-match"):
        out = subprocess.run(["fc-match", "-f", "%{file}", "sans:bold"], capture_output=True, text=True).stdout
        if out and Path(out).exists():
            return out
    raise MediaError("no TTF font found; install fonts-dejavu-core")


def drawtext(text: str, workdir: Path, **opts: object) -> str:
    """drawtext filter that reads its text from a file, so no filtergraph escaping is needed."""
    workdir.mkdir(parents=True, exist_ok=True)
    import hashlib
    f = workdir / f"txt_{hashlib.sha1(text.encode()).hexdigest()[:10]}.txt"
    f.write_text(re.sub(r"[\r\n]+", " ", text))
    extra = ":".join(f"{k}={v}" for k, v in opts.items())
    return f"drawtext=fontfile={font_file()}:textfile={f}:expansion=none" + (f":{extra}" if extra else "")


def wrap(text: str, max_chars: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= max_chars:
            cur = f"{cur} {w}".strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

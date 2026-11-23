"""MiniMax (Hailuo) video client. Same endpoints as the original engine/providers/hailuo.py,
but with a configurable model, no random prompt edits (the genome must match the video),
and per-clip cost from the verified price table.
"""
from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

import httpx

from .base import VideoProvider
from .prices import price

BASE = "https://api.minimax.io/v1"


class MinimaxVideo(VideoProvider):
    name, paid = "minimax", True
    max_clip_s = 10.0
    aspects = ("9:16", "16:9", "1:1")

    def __init__(self, key: str):
        super().__init__()
        self.key = key
        self.model = os.getenv("RELICON_MINIMAX_MODEL", "MiniMax-Hailuo-02")
        self.resolution = "768P"

    def _clip_len(self, seconds: float) -> int:
        return 6 if seconds <= 6 else 10

    def estimate(self, clip_seconds: list[float]) -> float:
        return sum(price(f"{self.model}:{self.resolution}:{self._clip_len(s)}s") for s in clip_seconds)

    def video(self, prompt: str, seconds: float, aspect: str, seed: int, out: Path,
              keyframe: Path | None, spec: dict[str, Any]) -> Path:
        h = {"Authorization": f"Bearer {self.key}"}
        body: dict[str, Any] = {"model": self.model, "prompt": prompt[:1900], "duration": self._clip_len(seconds),
                                "resolution": self.resolution, "prompt_optimizer": False}
        if keyframe is not None:
            body["first_frame_image"] = "data:image/png;base64," + base64.b64encode(keyframe.read_bytes()).decode()
        r = httpx.post(f"{BASE}/video_generation", json=body, headers=h, timeout=60)
        r.raise_for_status()
        task = r.json()["task_id"]
        deadline = time.time() + 900
        while time.time() < deadline:
            time.sleep(10)
            q = httpx.get(f"{BASE}/query/video_generation", params={"task_id": task}, headers=h, timeout=30).json()
            if q.get("status") == "Success":
                f = httpx.get(f"{BASE}/files/retrieve", params={"file_id": q["file_id"]}, headers=h, timeout=30).json()
                url = f["file"]["download_url"]
                out.write_bytes(httpx.get(url, timeout=300).content)
                self.last_cost_usd += self.estimate([seconds])
                return out
            if q.get("status") == "Fail":
                raise RuntimeError(f"minimax task {task} failed: {q}")
        raise TimeoutError(f"minimax task {task} timed out")

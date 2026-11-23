"""Resumable job graph: every step is cached by a content hash of its inputs, retried with
backoff, and reports progress events."""
from __future__ import annotations

import hashlib
import json
import time
import traceback
from pathlib import Path
from typing import Any, Callable

Event = dict[str, Any]


def content_hash(*parts: Any) -> str:
    raw = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class Job:
    def __init__(self, job_id: str, root: Path, on_event: Callable[[Event], None] | None = None,
                 retries: int = 3, backoff_s: float = 1.0):
        self.id = job_id
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "steps").mkdir(exist_ok=True)
        self.on_event = on_event
        self.retries = retries
        self.backoff_s = backoff_s
        self.events: list[Event] = []
        self.status = "running"

    def emit(self, step: str, status: str, progress: float, **extra: Any) -> None:
        ev = {"job_id": self.id, "step": step, "status": status, "progress": round(progress, 3),
              "t": time.time(), **extra}
        self.events.append(ev)
        with open(self.root / "events.jsonl", "a") as f:
            f.write(json.dumps(ev, default=str) + "\n")
        if self.on_event:
            self.on_event(ev)

    def step(self, name: str, inputs: Any, fn: Callable[[], Any], progress: float = 0.0,
             validate: Callable[[Any], bool] | None = None) -> Any:
        """Run fn once per unique inputs. The result must be JSON-serialisable."""
        key = content_hash(name, inputs)
        cache = self.root / "steps" / f"{name}-{key}.json"
        if cache.exists():
            cached = json.loads(cache.read_text())["result"]
            if validate is None or validate(cached):
                self.emit(name, "cached", progress)
                return cached
        self.emit(name, "started", progress)
        err = None
        for attempt in range(self.retries):
            try:
                t0 = time.time()
                result = fn()
                cache.write_text(json.dumps({"key": key, "result": result, "secs": time.time() - t0}, default=str))
                self.emit(name, "done", progress, secs=round(time.time() - t0, 2))
                return result
            except NonRetryable:
                raise
            except Exception as e:  # noqa: BLE001 - provider errors vary
                err = e
                self.emit(name, "retry", progress, attempt=attempt + 1, error=str(e)[:300])
                time.sleep(self.backoff_s * 2 ** attempt)
        self.emit(name, "failed", progress, error="".join(traceback.format_exception_only(err))[:500])
        raise err  # type: ignore[misc]


class NonRetryable(RuntimeError):
    """Budget refusals, policy blocks and bad input: retrying cannot help."""

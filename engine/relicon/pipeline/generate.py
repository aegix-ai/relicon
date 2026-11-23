"""One sentence -> finished, packaged ad. The 10 steps run as a resumable job graph."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from .. import media
from ..config import get_settings
from ..genome.models import Brief, Genome, StageCost
from ..genome.priors import template_genome
from ..providers.registry import ProviderSet, build
from . import brief as brief_step
from . import cost, planner, policy, qc
from .assemble import EXPORT_ASPECTS, assemble, overlap
from .jobs import Job, NonRetryable


class PolicyBlocked(NonRetryable):
    pass


def _exists(p: Any) -> bool:
    return isinstance(p, str) and Path(p).exists()


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _concat(parts: list[Path], out: Path) -> Path:
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    media.ff("-f", "concat", "-safe", "0", "-i", str(lst), "-c:v", "libx264", "-preset", "veryfast",
             "-pix_fmt", "yuv420p", str(out))
    return out


class Pipeline:
    def __init__(self, providers: ProviderSet | None = None, short_side: int | None = None,
                 on_event: Callable[[dict], None] | None = None, store: Any = None):
        self.s = get_settings()
        self.ps = providers or build()
        self.short_side = short_side or int(os.getenv("RELICON_SHORT_SIDE", 540 if self.ps.is_mock else 1080))
        self.on_event = on_event
        self.store = store
        self.workers = max(1, min(4, os.cpu_count() or 2))

    # step 1 + 2
    def propose(self, sentence: str | None, brief: Brief | None, genome: Genome | None, duration: int | None,
                platform: str | None, objective: str | None) -> Genome:
        if genome is not None:
            return genome.model_copy(deep=True).normalize()
        b = brief or brief_step.expand(sentence or "", self.ps.text, platform, objective)
        try:
            from ..learning.engine import propose_for_brief
            g = propose_for_brief(b, self.store)
        except Exception:  # noqa: BLE001 - no policy yet for this niche
            g = None
        g = g or template_genome(b)
        if duration:
            frac = g.text.cta_time_s / g.format.duration_s
            g.format.duration_s = duration
            g.text.cta_time_s = frac * duration
        return g.normalize()

    def storyboard(self, job: Job, g: Genome, out: Path) -> dict:
        sb = out / "storyboard"
        sb.mkdir(parents=True, exist_ok=True)
        keys = []
        for i, sc in enumerate(g.scenes):
            spec = {"purpose": sc.purpose, "shot_type": sc.shot_type, "palette": g.visual.palette,
                    "subject": g.hook.first_frame_subject if i == 0 else g.brief.product, "short_side": self.short_side}
            p = sb / f"{sc.scene_id}.png"
            keys.append(job.step(f"key_{sc.scene_id}", [sc.visual_prompt, sc.seed, spec, self.ps.image.model, g.format.aspect_ratio],
                                 lambda sc=sc, spec=spec, p=p: str(self.ps.image.image(sc.visual_prompt, g.format.aspect_ratio, sc.seed, p, spec)),
                                 validate=_exists))
        bible = g.production.continuity_bible
        if bible:
            bd = out / "bible"
            bd.mkdir(exist_ok=True)
            for ref in bible["reference_assets"]:
                p = out / ref
                subj = "lead character sheet" if "lead" in ref else g.brief.product
                job.step(f"bible_{p.stem}", [ref, bible["seed_base"], subj],
                         lambda p=p, subj=subj: str(self.ps.image.image(subj, g.format.aspect_ratio, bible["seed_base"], p,
                                                                        {"purpose": "continuity bible", "subject": subj,
                                                                         "palette": g.visual.palette, "short_side": self.short_side})),
                         validate=_exists)
        vo = self.voice(job, g, out)
        clips = []
        for sc, k in zip(g.scenes, keys):
            L = sc.end_s - sc.start_s + overlap(g, g.scenes.index(sc))
            p = sb / f"{sc.scene_id}_still.mp4"
            clips.append(Path(job.step(f"still_{sc.scene_id}", [k, L], lambda k=k, L=L, p=p: (media.ff(
                "-loop", "1", "-i", k, "-t", f"{L:.3f}", "-r", str(media.FPS), "-c:v", "libx264", "-preset", "ultrafast",
                "-pix_fmt", "yuv420p", str(p)), str(p))[1], validate=_exists)))
        music = self.music(job, g, out)
        draft = job.step("animatic", [g.model_dump(include={"scenes", "text", "audio", "format"}), keys, vo],
                         lambda: assemble(g, clips, [Path(v) if v else None for v in vo], Path(music), None, out / "draft",
                                          min(self.short_side, 360), (g.format.aspect_ratio,), "animatic"),
                         validate=lambda r: _exists(r.get("master")))
        return {"keyframes": keys, "vo": vo, "animatic": draft["master"], "music": music}

    def voice(self, job: Job, g: Genome, out: Path) -> list[str | None]:
        vd = out / "voice"
        vd.mkdir(parents=True, exist_ok=True)
        res: list[str | None] = []
        for sc in g.scenes:
            if g.audio.voice.accent == "none" or not sc.vo_line:
                res.append(None)
                continue
            p = vd / f"{sc.scene_id}.wav"
            cfg = g.audio.voice.model_dump()
            res.append(job.step(f"vo_{sc.scene_id}", [sc.vo_line, cfg, self.ps.voice.model],
                                lambda sc=sc, p=p, cfg=cfg: str(self.ps.voice.speak(sc.vo_line, p, cfg)), validate=_exists))
        return res

    def music(self, job: Job, g: Genome, out: Path) -> str:
        p = out / "music.wav"
        spec = g.audio.music.model_dump()
        return job.step("music", [spec, g.format.duration_s, self.ps.music.model],
                        lambda: str(self.ps.music.music(float(g.format.duration_s), p, spec)), validate=_exists)

    def render_scene(self, g: Genome, i: int, key: str, out: Path, seed_bump: int = 0) -> str:
        sc = g.scenes[i]
        need = sc.end_s - sc.start_s + overlap(g, i)
        vd = out / "clips"
        vd.mkdir(parents=True, exist_ok=True)
        spec = {"motion": g.hook.motion_intensity if i == 0 else "medium", "purpose": sc.purpose,
                "palette": g.visual.palette, "short_side": self.short_side, "shot_type": sc.shot_type}
        k = max(1, -(-need // self.ps.video.max_clip_s))
        kf = Path(key) if self.ps.video.image_to_video else None
        if k == 1:
            return str(self.ps.video.video(sc.visual_prompt, need, g.format.aspect_ratio, sc.seed + seed_bump,
                                           vd / f"{sc.scene_id}.mp4", kf, spec))
        parts = [self.ps.video.video(sc.visual_prompt, need / k, g.format.aspect_ratio, sc.seed + seed_bump + j,
                                     vd / f"{sc.scene_id}_{j}.mp4", kf if j == 0 else None, spec) for j in range(int(k))]
        return str(_concat(parts, vd / f"{sc.scene_id}.mp4"))

    def run(self, sentence: str | None = None, *, brief: Brief | None = None, genome: Genome | None = None,
            duration: int | None = None, platform: str | None = None, objective: str | None = None,
            budget: float | None = None, draft: bool = False, aspects: tuple[str, ...] = EXPORT_ASPECTS,
            job_id: str | None = None, campaign: str = "") -> dict:
        t0 = time.time()
        budget = budget if budget is not None else (self.s.default_budget_usd if self.ps.any_paid else 0.0)
        g = self.propose(sentence, brief, genome, duration, platform, objective)
        job_id = job_id or f"job_{g.id}"
        out = self.s.outputs / g.id
        job = Job(job_id, out / "job", self.on_event)
        job.emit("brief", "done", 0.05, brief=g.brief.model_dump())
        g = Genome.model_validate(job.step("plan", [g.model_dump(exclude={"identity": {"created_at"}}), self.ps.text.model],
                                           lambda: planner.plan(g, self.ps.text, self.ps.video.model).model_dump(), 0.1))
        g.production.providers = self.ps.describe()
        g.production.is_mock = self.ps.is_mock
        g.production.ai_disclosure = {}
        cp = cost.plan_cost(g, self.ps, budget, draft=True)
        sb = self.storyboard(job, g, out)
        job.emit("storyboard", "done", 0.35, animatic=sb["animatic"])
        if draft:
            return self._package(g, out, {"draft": sb["animatic"]}, {"cost_plan": cp}, None, sb, t0, job, campaign, draft=True)
        cp = cost.plan_cost(g, self.ps, budget, draft=False)
        job.emit("cost_plan", "done", 0.4, total=cp["total_estimated_usd"], budget=budget)
        clips: list[str] = [""] * len(g.scenes)

        def one(i: int) -> None:
            sc = g.scenes[i]
            clips[i] = job.step(f"render_{sc.scene_id}", [sc.model_dump(), self.ps.video.model, self.short_side,
                                                          g.format.aspect_ratio, overlap(g, i)],
                                lambda: self.render_scene(g, i, sb["keyframes"][i], out), 0.4 + 0.35 * i / len(g.scenes),
                                validate=_exists)
        with ThreadPoolExecutor(self.workers) as ex:
            list(ex.map(one, range(len(g.scenes))))
        sfx = job.step("sfx", [g.audio.sfx_density, self.ps.sfx.model],
                       lambda: str(self.ps.sfx.sfx("whoosh", 0.4, out / "sfx.wav")), validate=_exists)
        asm = self._assemble(job, g, clips, sb, sfx, out, aspects)
        # step 8: QC, re-render failing scenes once if the budget allows
        checks, bad = qc.technical(g, Path(asm["master"]), asm["layouts"][g.format.aspect_ratio], [Path(c) for c in clips])
        rerendered = []
        if bad:
            spent = sum(p.last_cost_usd for p in self.ps.all)
            for sid in bad:
                i = next(k for k, sc in enumerate(g.scenes) if sc.scene_id == sid)
                if self.ps.any_paid and spent + self.ps.video.estimate([g.scenes[i].end_s - g.scenes[i].start_s]) > budget:
                    break
                clips[i] = self.render_scene(g, i, sb["keyframes"][i], out, seed_bump=1000)
                rerendered.append(sid)
            if rerendered:
                asm = self._assemble(job, g, clips, sb, sfx, out, aspects, tag="qc")
                checks, bad = qc.technical(g, Path(asm["master"]), asm["layouts"][g.format.aspect_ratio], [Path(c) for c in clips])
        frames = qc.extract_frames(Path(asm["master"]), g, out / "frames")
        judged = self.ps.judge.judge(Path(asm["master"]), g, frames)
        g.production.qc = {"technical": checks, "judge": judged, "fidelity": qc.fidelity_score(judged),
                           "passed": all(c["pass"] for c in checks.values()), "rerendered": rerendered}
        job.emit("qc", "done", 0.9, passed=g.production.qc["passed"])
        # step 9: policy
        flags, disclosure = policy.check(g)
        g.production.policy_flags, g.production.ai_disclosure = flags, disclosure
        job.emit("policy", "done", 0.95, flags=len(flags), blocked=policy.blocked(flags))
        return self._package(g, out, asm["outputs"], {"cost_plan": cp}, asm, sb, t0, job, campaign)

    def _assemble(self, job: Job, g: Genome, clips: list[str], sb: dict, sfx: str, out: Path, aspects, tag: str = "") -> dict:
        return job.step(f"assemble{tag}", [clips, [_sha(Path(c)) for c in clips], sb["vo"], sb["music"], aspects,
                                           g.model_dump(include={"text", "hook", "scenes", "audio", "format"})],
                        lambda: assemble(g, [Path(c) for c in clips], [Path(v) if v else None for v in sb["vo"]],
                                         Path(sb["music"]), Path(sfx), out, self.short_side, aspects),
                        0.8, validate=lambda r: all(_exists(p) for p in r["outputs"].values()))

    def _package(self, g: Genome, out: Path, videos: dict, costs: dict, asm: dict | None, sb: dict, t0: float,
                 job: Job, campaign: str, draft: bool = False) -> dict:
        actual = {p.name + ":" + p.model: round(p.last_cost_usd, 4) for p in self.ps.all if p.last_cost_usd}
        stages = costs["cost_plan"]["stages"]
        g.production.cost_usd = [StageCost(**st, actual_usd=actual.get(f"{st['provider']}:{st['model']}", 0.0)) for st in stages]
        g.production.total_cost_usd = round(sum(actual.values()), 4)
        g.production.render_time_s = round(time.time() - t0, 2)
        (out / "genome.json").write_text(g.model_dump_json(indent=2))
        files = {k: {"path": v, "sha256": _sha(Path(v)), "bytes": Path(v).stat().st_size,
                     "duration_s": round(media.duration(v), 2)} for k, v in videos.items()}
        manifest = {"genome_id": g.id, "ad_name": g.ad_name(), "draft": draft, "is_mock": self.ps.is_mock,
                    "label": "MOCK RENDER (placeholder media, not a real ad)" if self.ps.is_mock else "real providers",
                    "videos": files, "storyboard": sb["keyframes"], "animatic": sb["animatic"],
                    "providers": self.ps.describe(), "provider_notes": self.ps.notes,
                    "publish_instructions": f"Name the ad exactly '{g.ad_name()}' in Ads Manager so results can be imported.",
                    "events": len(job.events)}
        report = {"genome_id": g.id, **costs, "actual_by_provider": actual, "actual_total_usd": g.production.total_cost_usd,
                  "render_time_s": g.production.render_time_s}
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (out / "cost_report.json").write_text(json.dumps(report, indent=2))
        if not draft:
            shutil.rmtree(out / "work", ignore_errors=True)
        if self.store is not None:
            self.store.put("genome", g.id, json.loads(g.model_dump_json()), campaign=campaign, niche=g.brief.niche)
            self.store.put("ad", g.id, {"manifest": manifest, "cost_report": report, "dir": str(out)},
                           campaign=campaign, niche=g.brief.niche)
        job.emit("package", "done", 1.0, out=str(out))
        return {"genome": g, "dir": str(out), "manifest": manifest, "cost_report": report}

"""HTTP API for the dashboard. Every simulated payload carries is_simulated so the UI can badge it."""
from __future__ import annotations

import asyncio
import json
import tempfile
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import REPO_ROOT, get_settings
from .store import Store

app = FastAPI(title="Relicon engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
_S = get_settings()
_S.outputs.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_S.outputs)), name="media")
JOBS: dict[str, dict] = {}


def store() -> Store:
    return Store(_S.database_url)


def _url(p: str | None) -> str | None:
    if not p:
        return None
    try:
        return "/media/" + str(Path(p).resolve().relative_to(_S.outputs.resolve()))
    except ValueError:
        return None


@app.get("/api/health")
def health():
    return {"ok": True, "providers": _S.providers, "live_apis": _S.live_apis}


@app.get("/api/ads")
def ads():
    out = []
    for d in store().list("ad"):
        man = d["manifest"]
        out.append({"genome_id": man["genome_id"], "ad_name": man["ad_name"], "is_mock": man["is_mock"],
                    "label": man.get("label"), "draft": man.get("draft"),
                    "videos": {a: _url(v["path"]) for a, v in (man.get("videos") or {}).items()},
                    "animatic": _url(man.get("animatic")), "cost": d["cost_report"]})
    return out[::-1]


@app.get("/api/genomes/{gid}")
def genome(gid: str):
    d = store().get("genome", gid)
    if d is None:
        raise HTTPException(404, "no such genome")
    return d


@app.get("/api/campaigns")
def campaigns():
    groups: dict[str, dict] = {}
    for d in store().list("genome"):
        c = d.get("brief", {}).get("niche", "")
        g = groups.setdefault(c, {"niche": c, "ads": 0, "with_results": 0, "is_simulated": False, "best_roas": 0.0})
        g["ads"] += 1
        for r in d.get("results", []):
            g["with_results"] += 1
            g["is_simulated"] |= bool(r.get("is_simulated"))
            g["best_roas"] = max(g["best_roas"], r["metrics"].get("roas", 0))
    return list(groups.values())


@app.get("/api/learning/{niche}")
def learning(niche: str):
    from .learning import policy
    st = store()
    vs = [{"version": v["version"], "created_at": v["created_at"], "n_obs": len(v["obs_ids"]),
           "is_simulated": v.get("is_simulated")} for v in policy.versions(st, niche) if v.get("version")]
    return {"active": policy.active(st, niche), "versions": vs}


class Rollback(BaseModel):
    version: str


@app.post("/api/learning/{niche}/rollback")
def rollback(niche: str, body: Rollback):
    from .learning import policy
    try:
        return policy.rollback(store(), niche, body.version)
    except KeyError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/api/eval")
def evals():
    d = REPO_ROOT / "evals"
    if not (d / "summary.json").exists():
        return {"available": False}
    return {"available": True, "summary": json.loads((d / "summary.json").read_text()),
            "report": (d / "REPORT.md").read_text(), "is_simulated": True}


@app.get("/api/sim/scenarios")
def scenarios():
    from .simulator.scenarios import all_scenarios
    return [{"name": n, "niche": s.niche, "platform": s.platform, "sentence": s.sentence} for n, s in all_scenarios().items()]


class SimReq(BaseModel):
    scenario: str = "coffee_nightshift@tiktok"
    generations: int = 3
    batch: int = 8
    seed: int = 0


@app.post("/api/sim/run")
def sim_run(r: SimReq):
    from .cli import simulate
    return {"is_simulated": True, "log": simulate(store(), r.scenario, min(r.generations, 20), min(r.batch, 16), r.seed,
                                                  quiet=True)}


class GenReq(BaseModel):
    sentence: str
    duration: int | None = None
    platform: str | None = None
    budget: float | None = None
    draft: bool = False


@app.post("/api/generate")
def generate(r: GenReq):
    jid = uuid.uuid4().hex[:10]
    JOBS[jid] = {"events": [], "done": False, "result": None, "error": None}

    def work():
        from .pipeline.generate import Pipeline
        from .providers.registry import build
        try:
            res = Pipeline(build(_S.providers), store=store(), on_event=JOBS[jid]["events"].append).run(
                sentence=r.sentence, duration=r.duration, platform=r.platform,
                budget=r.budget if r.budget is not None else _S.default_budget_usd, draft=r.draft)
            JOBS[jid]["result"] = {"genome_id": res["genome"].id, "dir": res["dir"]}
        except Exception as e:  # noqa: BLE001 - reported to the client
            JOBS[jid]["error"] = str(e)
        JOBS[jid]["done"] = True
    threading.Thread(target=work, daemon=True).start()
    return {"job_id": jid}


@app.get("/api/jobs/{jid}/events")
async def job_events(jid: str):
    if jid not in JOBS:
        raise HTTPException(404, "no such job")

    async def stream():
        i = 0
        while True:
            j = JOBS[jid]
            while i < len(j["events"]):
                yield f"data: {json.dumps(j['events'][i], default=str)}\n\n"
                i += 1
            if j["done"]:
                yield f"event: done\ndata: {json.dumps({'result': j['result'], 'error': j['error']})}\n\n"
                return
            await asyncio.sleep(0.3)
    return StreamingResponse(stream(), media_type="text/event-stream")


class ImportReq(BaseModel):
    csv_text: str
    preset: str = "meta"
    fx_to_usd: float | None = None


@app.post("/api/import")
def import_results(r: ImportReq):
    from .performance.csv_import import import_csv
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write(r.csv_text)
    return import_csv(store(), fh.name, r.preset, r.fx_to_usd)


@app.get("/api/imports")
def imports():
    return store().list("import")

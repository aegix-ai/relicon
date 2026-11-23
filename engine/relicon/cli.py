"""relicon CLI: generate, simulate, import, learn, next, rollback, eval, demo, prices."""
from __future__ import annotations

import argparse
import json
import sys

from .config import get_settings
from .store import Store

SIM = "[SIMULATED]"


def _store() -> Store:
    return Store(get_settings().database_url)


def _pipeline(args, store):
    from .pipeline.generate import Pipeline
    from .providers.registry import build
    return Pipeline(build(args.providers), short_side=args.short_side, store=store,
                    on_event=lambda e: print(f"  [{e['step']}] {e['status']}", file=sys.stderr) if args.verbose else None)


def cmd_generate(args) -> dict:
    store = _store()
    r = _pipeline(args, store).run(sentence=args.sentence, duration=args.duration, platform=args.platform,
                                   budget=args.budget, draft=args.draft, campaign=args.campaign)
    g = r["genome"]
    print(f"ad {g.id} -> {r['dir']}\n  {r['manifest']['label']}\n  cost ${r['cost_report']['actual_total_usd']:.2f}"
          f"  QC {'pass' if all(c['pass'] for c in g.production.qc.get('technical', {}).values()) else 'see manifest'}"
          f"\n  publish as: {g.ad_name('a')}")
    return r


def simulate(store, scenario: str, generations: int, k: int, seed: int = 0, render: bool = False,
             short_side: int = 160, duration: int | None = None, quiet: bool = False) -> list[dict]:
    from .genome.models import ResultRecord
    from .learning.engine import learn, next_for
    from .pipeline.planner import plan
    from .providers.mock import MockText
    from .simulator.market import SimulatedMarket
    from .simulator.scenarios import get
    sc = get(scenario)
    market = SimulatedMarket(sc, seed=seed)
    log = []
    for gen in range(generations):
        batch = next_for(store, sc.brief, k=k, seed=seed * 1000 + gen)
        if render:
            from .pipeline.generate import Pipeline
            p = Pipeline(short_side=short_side, store=store)
            batch = [p.run(genome=g, duration=duration)["genome"] for g in batch]
        else:
            batch = [plan(g, MockText()) for g in batch]
        rows = market.launch(batch, generation=gen)
        for g, row in zip(batch, rows):
            g.results.append(ResultRecord.model_validate(row["record"]))
            store.put("genome", g.id, g.model_dump(), campaign=f"sim:{scenario}", niche=sc.niche)
        pol = learn(store, sc.niche, gen)
        roas = [row["record"]["metrics"]["roas"] for row in rows]
        entry = {"generation": gen, "policy": pol["version"], "mean_roas": sum(roas) / len(roas), "max_roas": max(roas),
                 "insights": len(pol["summary"]["insights"]), "is_simulated": True}
        store.put("sim_run", f"{scenario}:{seed}:{gen}", entry, campaign=f"sim:{scenario}", niche=sc.niche)
        log.append(entry)
        if not quiet:
            print(f"{SIM} gen {gen}: policy {pol['version']}, observed ROAS mean {entry['mean_roas']:.2f} max "
                  f"{entry['max_roas']:.2f}, {entry['insights']} insights")
    return log


def cmd_simulate(args):
    return simulate(_store(), args.scenario, args.generations, args.batch, args.seed, args.render, args.short_side,
                    args.duration)


def cmd_import(args):
    from .performance.csv_import import import_csv
    rep = import_csv(_store(), args.file, args.preset, args.fx_to_usd, args.window_days, not args.window_open,
                     json.loads(args.map) if args.map else None)
    print(json.dumps({k: rep[k] for k in ("rows", "matched")} | {"unmatched": len(rep["unmatched"]),
                                                                "errors": len(rep["errors"])}))
    for u in rep["unmatched"][:20]:
        print(f"  unmatched line {u['line']}: {u['ad_name']!r} ({u['why']})")
    for e in rep["errors"][:20]:
        print(f"  error line {e['line']}: {e['why']}")
    return rep


def cmd_learn(args):
    from .learning.engine import learn
    pol = learn(_store(), args.niche)
    s = pol["summary"]
    tag = SIM if pol["is_simulated"] else ""
    print(f"{tag} policy {pol['version']} for {args.niche}: {s['n_used']} ads used, {s['below_floor']} below floor")
    for i in s["insights"][:10]:
        print("  -", i["text"])
    return pol


def cmd_next(args):
    from .learning.engine import brief_for, next_for
    store = _store()
    gs = next_for(store, brief_for(store, args.niche), k=args.batch, seed=args.seed)
    for g in gs:
        print(f"{g.id}  {g.identity.selection_reason}")
    return gs


def cmd_rollback(args):
    from .learning.policy import rollback
    doc = rollback(_store(), args.niche, args.version)
    print(f"active policy for {args.niche} is now {doc['version']}")


def cmd_eval(args):
    from .evals.report import main
    print(main(quick=args.quick))


def cmd_prices(args):
    from .providers.prices import table
    for row in table():
        print(json.dumps(row))


def cmd_demo(args):
    """Zero-key loop: render one ad, simulate generations through the store, render what the learner picks next."""
    from .learning.engine import propose_for_brief
    from .simulator.scenarios import get
    store = _store()
    q = args.quick
    print("1/3 render one ad from a sentence (mock providers, real media)")
    first = _pipeline(args, store).run(sentence="cold-brew coffee for night-shift nurses", duration=6 if q else 15)
    print(f"    {first['dir']}")
    gens, k = (2, 4) if q else (6, 8)
    print(f"2/3 {SIM} launch {gens} generations of {k} ads into the simulated market, learn after each")
    log = simulate(store, "coffee_nightshift@tiktok", gens, k, seed=args.seed)
    sc = get("coffee_nightshift@tiktok")
    g = propose_for_brief(sc.brief, store)
    print(f"3/3 render the ad the learner proposes next\n    reason: {g.identity.selection_reason}")
    if not args.short_side and g.format.duration_s > 60:
        args.short_side = 240  # long ads render at low resolution in the demo to keep it fast
    r = _pipeline(args, store).run(genome=g, duration=6 if q else None)
    print(f"    {r['dir']}\n{SIM} observed mean ROAS by generation: "
          + ", ".join(f"{e['mean_roas']:.2f}" for e in log))
    return {"first": first, "log": log, "next": r}


def main(argv: list[str] | None = None) -> int:
    s = get_settings()
    ap = argparse.ArgumentParser(prog="relicon")
    ap.add_argument("--providers", default=s.providers, choices=["mock", "real"])
    ap.add_argument("--short-side", type=int, default=None)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate", help="one sentence -> packaged ad")
    g.add_argument("sentence")
    g.add_argument("--duration", type=int)
    g.add_argument("--platform")
    g.add_argument("--budget", type=float, default=s.default_budget_usd)
    g.add_argument("--draft", action="store_true", help="storyboard + animatic only")
    g.add_argument("--campaign", default="")
    g.set_defaults(fn=cmd_generate)
    m = sub.add_parser("simulate", help="closed loop on the simulated market")
    m.add_argument("--scenario", default="coffee_nightshift@tiktok")
    m.add_argument("--generations", type=int, default=6)
    m.add_argument("--batch", type=int, default=8)
    m.add_argument("--seed", type=int, default=0)
    m.add_argument("--render", action="store_true", help="render every ad (slow); default plans only")
    m.add_argument("--duration", type=int)
    m.set_defaults(fn=cmd_simulate)
    i = sub.add_parser("import", help="import a Meta or TikTok CSV export")
    i.add_argument("file")
    i.add_argument("--preset", choices=["meta", "tiktok"], default="meta")
    i.add_argument("--fx-to-usd", type=float)
    i.add_argument("--window-days", type=int, default=7)
    i.add_argument("--window-open", action="store_true", help="attribution window not closed yet")
    i.add_argument("--map", help='JSON column overrides, e.g. {"spend": "Amount spent (EUR)"}')
    i.set_defaults(fn=cmd_import)
    for name, fn in (("learn", cmd_learn), ("next", cmd_next)):
        p = sub.add_parser(name)
        p.add_argument("niche")
        p.add_argument("--batch", type=int, default=8)
        p.add_argument("--seed", type=int, default=0)
        p.set_defaults(fn=fn)
    r = sub.add_parser("rollback")
    r.add_argument("niche")
    r.add_argument("version")
    r.set_defaults(fn=cmd_rollback)
    e = sub.add_parser("eval")
    e.add_argument("--quick", action="store_true")
    e.set_defaults(fn=cmd_eval)
    sub.add_parser("prices").set_defaults(fn=cmd_prices)
    d = sub.add_parser("demo")
    d.add_argument("--quick", action="store_true")
    d.add_argument("--seed", type=int, default=0)
    d.set_defaults(fn=cmd_demo)
    args = ap.parse_args(argv)
    args.fn(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

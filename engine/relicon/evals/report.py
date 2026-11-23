"""`relicon eval`: closed-loop comparison on the SIMULATED market -> evals/REPORT.md + charts + summary.json."""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from ..config import REPO_ROOT
from ..simulator.scenarios import all_scenarios, get
from . import harness

BANNER = "> **SIMULATED.** Every number below comes from a made-up market in `engine/relicon/simulator`. It is not real ad performance."


def _curve(runs, key):
    return np.mean([[g[key] for g in r.gens] for r in runs], axis=0)


def _reach(r, frac):
    for g in r.gens:
        if g["recommended"] >= frac:
            return g["impressions"]
    return None


def _plot(path: Path, curves: dict, title: str, ylabel: str):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, y in curves.items():
        ax.plot(range(len(y)), y, marker="o", ms=3, label=name)
    ax.set_title(f"SIMULATED - {title}")
    ax.set_xlabel("generation")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    ax.legend()
    fig.text(0.99, 0.01, "simulated market, not real data", ha="right", fontsize=7, color="gray")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def production(durations, short_side: int) -> list[dict]:
    from ..genome.priors import template_genome
    from ..pipeline.brief import rule_brief
    from ..pipeline.generate import Pipeline
    rows = []
    b = rule_brief("cold-brew coffee for night-shift nurses")
    for d in durations:
        g = template_genome(b, d)
        if d >= 120:
            g.format.avg_shot_length_s = 5
        t = time.time()
        r = Pipeline(short_side=short_side).run(genome=g)
        g = r["genome"]
        q = g.production.qc
        fid = q["fidelity"]
        rows.append({"duration_s": d, "scenes": len(g.scenes), "chapters": len(g.format.chapters),
                     "render_s": round(time.time() - t, 1), "qc_pass": all(c["pass"] for c in q["technical"].values()),
                     "fidelity": fid["fidelity"], "fields_measured": fid.get("evaluated"),
                     "real_equivalent_usd": r["cost_report"]["cost_plan"]["real_equivalent_usd"]["total_usd"]})
    return rows


def _say(msg: str) -> None:
    import sys
    print(f"[eval] {msg}", file=sys.stderr, flush=True)


def main(quick: bool = False, out_dir: Path | None = None) -> Path:
    t0 = time.time()
    out = Path(out_dir or REPO_ROOT / "evals")
    out.mkdir(parents=True, exist_ok=True)
    scen = ["coffee_nightshift@tiktok", "skincare_dry@meta_reels"] if quick else list(all_scenarios())
    seeds = [1] if quick else [1, 2, 3]
    gens, k = (4, 6) if quick else (15, 8)
    runs = {m: [] for m in harness.METHODS}
    for n_i, name in enumerate(scen):
        _say(f"main runs {n_i + 1}/{len(scen)}: {name} ({time.time() - t0:.0f} s)")
        for m in harness.METHODS:
            for s in seeds:
                runs[m].append(harness.run(get(name), m, s, gens=gens, k=k)[0])
    # robustness: relicon vs llm_only
    rob_scen = scen[:2] if quick else ["coffee_nightshift@tiktok", "skincare_dry@meta_reels", "fitness_home@tiktok",
                                       "saas_freelance@meta_reels"]
    _say("robustness runs")
    rob = {}
    for m in ("relicon", "llm_only"):
        rob[("high noise", m)] = [harness.run(get(n), m, s, gens=gens, k=k, noise="high")[0] for n in rob_scen for s in seeds]
        rob[("drift", m)] = [harness.run(get(n), m, s, gens=gens, k=k, drift_at=gens // 2)[0] for n in rob_scen for s in seeds]
    # cold start vs warm start from a sibling niche in the same vertical (beauty has two niches)
    pairs = [("skincare_teen@tiktok", "skincare_dry@tiktok")] if quick else \
        [("skincare_teen@tiktok", "skincare_dry@tiktok"), ("skincare_teen@meta_reels", "skincare_dry@meta_reels")]
    _say("cold vs warm start")
    cold, warm = [], []
    for target, sib in pairs:
        for s in seeds:
            _, hist = harness.run(get(sib), "relicon", 100 + s, gens=gens, k=k)
            cold.append(harness.run(get(target), "relicon", s, gens=gens, k=k)[0])
            warm.append(harness.run(get(target), "relicon", s, gens=gens, k=k, history=hist, variant="warm")[0])
    _say("production renders")
    prod = production([6] if quick else [6, 15, 30, 60, 300], 160 if quick else 240)

    curves = {m: _curve(r, "batch_mean") for m, r in runs.items()}
    recs = {m: _curve(r, "recommended") for m, r in runs.items()}
    _plot(out / "learning_curve.png", curves, "mean true value of launched ads / oracle", "share of oracle")
    _plot(out / "recommended.png", recs, "true value of the recommended ad / oracle", "share of oracle")
    _plot(out / "regret.png", {m: np.cumsum(_curve(r, "regret")) for m, r in runs.items()},
          "cumulative regret per ad (ROAS units)", "cumulative regret")
    _plot(out / "robustness.png", {f"{a} / {m}": _curve(v, "batch_mean") for (a, m), v in rob.items()} |
          {"cold start": _curve(cold, "batch_mean"), "warm start (sibling niche)": _curve(warm, "batch_mean")},
          "robustness", "share of oracle")

    def pct(x):
        return f"{100 * x:.0f}%"
    L = ["# Relicon evaluation report", "", BANNER, "",
         f"Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC, commit `{_git()}`, runtime {time.time() - t0:.0f} s, "
         f"mode `{'quick' if quick else 'full'}`.", "",
         f"Setup: {len(scen)} scenarios (niche x platform), seeds {seeds}, {gens} generations, {k} ads per generation, "
         f"$150 per ad for 7 days, results read after the 7-day attribution window. The oracle is the best genome found by "
         f"coordinate ascent on the hidden truth (a lower bound on the true optimum). Baselines: `random` (random genomes), "
         f"`template` (best-practice template plus copy tweaks), `llm_only` (mock creative director with priors and no data, D8: "
         f"no API key in this run).", "",
         "## Main result", "", "![learning curve](learning_curve.png)", "",
         "| method | gen 0 | gen " + str(gens // 2) + f" | gen {gens - 1} | recommended ad, last gen | cumulative regret |",
         "|---|---|---|---|---|---|"]
    for m in harness.METHODS:
        c, rc = curves[m], recs[m]
        reg = np.cumsum(_curve(runs[m], "regret"))[-1]
        L.append(f"| {m} | {pct(c[0])} | {pct(c[gens // 2])} | {pct(c[-1])} | {pct(rc[-1])} | {reg:.1f} |")
    L += ["", "Share of oracle = true expected ROAS of the ad / oracle ROAS, averaged over runs.", "",
          "## Impressions until the recommended ad reaches a share of the oracle", "",
          "| method | 50% | 75% | 90% |", "|---|---|---|---|"]
    for m in harness.METHODS:
        cells = []
        for f in (0.5, 0.75, 0.9):
            v = [_reach(r, f) for r in runs[m]]
            hit = [x for x in v if x is not None]
            cells.append(f"{np.median(hit) / 1e6:.2f}M ({len(hit)}/{len(v)} runs)" if hit else f"not reached (0/{len(v)})")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L += ["", "![recommended](recommended.png) ![regret](regret.png)", "", "## Robustness", "",
          "| condition | relicon, last gen | llm_only, last gen |", "|---|---|---|"]
    for a in ("high noise", "drift"):
        L.append(f"| {a} | {pct(_curve(rob[(a, 'relicon')], 'batch_mean')[-1])} | {pct(_curve(rob[(a, 'llm_only')], 'batch_mean')[-1])} |")
    L += [f"| cold start (no history) | {pct(_curve(cold, 'batch_mean')[-1])} | - |",
          f"| warm start (history from sibling niche, same vertical) | {pct(_curve(warm, 'batch_mean')[-1])} | - |", "",
          f"First generation, cold vs warm: {pct(_curve(cold, 'batch_mean')[0])} vs {pct(_curve(warm, 'batch_mean')[0])}. "
          f"High noise = ad-level noise 0.5 logit and 35% of the budget. Drift = the hook and click effects flip at "
          f"generation {gens // 2}.", "", "![robustness](robustness.png)", "", "## Per scenario (relicon vs best baseline, last generation)", "",
          "| scenario | relicon | best baseline |", "|---|---|---|"]
    for name in scen:
        rv = np.mean([r.gens[-1]["batch_mean"] for r in runs["relicon"] if r.scenario == name])
        bb = max((np.mean([r.gens[-1]["batch_mean"] for r in runs[m] if r.scenario == name]), m) for m in harness.METHODS[1:])
        L.append(f"| {name} | {pct(rv)} | {pct(bb[0])} ({bb[1]}) |")
    L += ["", "## Production (mock providers, this machine)", "",
          "| duration | scenes | chapters | render time | technical QC | genome fidelity (measured fields) | real-stack cost estimate |",
          "|---|---|---|---|---|---|---|"]
    for p in prod:
        L.append(f"| {p['duration_s']} s | {p['scenes']} | {p['chapters']} | {p['render_s']} s | {'pass' if p['qc_pass'] else 'FAIL'} | "
                 f"{pct(p['fidelity'])} ({p['fields_measured']}) | ${p['real_equivalent_usd']:.2f} |")
    L += ["", "Mock renders are placeholder media. Fidelity covers only fields measurable without a vision model (D6). "
          "Real-stack cost uses verified prices only (MiniMax Hailuo-02, ElevenLabs, Claude); ads over the $5 default budget are refused unless the job budget is raised.", "",
          "## Limits", "",
          "- The market is invented. Its effect sizes were set so the oracle is a few times better than a median ad; real markets may be flatter or steeper.",
          "- Conversion rate is close to unlearnable at $150 per ad (about 5 conversions per ad). Relicon mostly learns hook rate and clicks, which caps how close it gets to the oracle.",
          "- Model settings (prior sd 0.12, local candidate pool) were picked on `coffee_nightshift@tiktok`; all scenarios use different market seeds.",
          "- The LLM-only baseline is the mock director in this run. With `ANTHROPIC_API_KEY` it would call claude-opus-5-5.", ""]
    (out / "REPORT.md").write_text("\n".join(L))
    summary = {"is_simulated": True, "generated_at": datetime.now(timezone.utc).isoformat(), "quick": quick,
               "curves": {m: [round(float(x), 4) for x in c] for m, c in curves.items()},
               "recommended": {m: [round(float(x), 4) for x in c] for m, c in recs.items()}, "production": prod}
    (out / "summary.json").write_text(json.dumps(summary, indent=1))
    return out / "REPORT.md"


def _git() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"

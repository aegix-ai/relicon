import numpy as np

from relicon.genome import space
from relicon.genome.priors import template_genome
from relicon.pipeline.planner import plan
from relicon.providers.mock import MockText
from relicon.simulator.market import SimulatedMarket
from relicon.simulator.oracle import best_genome
from relicon.simulator.scenarios import NICHES, PLATFORMS, all_scenarios, get

SC = get("coffee_nightshift@tiktok")


def test_scenarios_cover_spec():
    sc = all_scenarios()
    assert len(NICHES) >= 5 and len(PLATFORMS) >= 2 and len(sc) == len(NICHES) * len(PLATFORMS)
    assert len({s.vertical for s in sc.values()}) >= 4


def test_results_are_labeled_and_consistent():
    m = SimulatedMarket(SC, seed=3)
    row = m.launch([plan(template_genome(SC.brief), MockText())])[0]
    rec = row["record"]
    assert rec["is_simulated"] and rec["source"] == "simulated"
    mt = rec["metrics"]
    assert mt["impressions"] > 5000 and 0 < mt["hook_rate"] < 1 and 0 < mt["hold_rate"] < 1
    assert mt["views_3s"] >= mt["q25"] >= mt["q50"] >= mt["q75"] >= mt["q100"]
    assert mt["link_clicks"] >= mt["conversions"]
    assert abs(mt["roas"] - mt["revenue"] / mt["spend"]) < 1e-6


def test_seeded_and_deterministic():
    g = template_genome(SC.brief)
    a = SimulatedMarket(SC, seed=5).launch([g])[0]["record"]["metrics"]
    b = SimulatedMarket(SC, seed=5).launch([g])[0]["record"]["metrics"]
    assert a == b


def test_fatigue_and_delay():
    g = template_genome(SC.brief)
    m = SimulatedMarket(SC, seed=1)
    daily = m.launch([g], budget_per_ad=4000, days=14)[0]["record"]["raw"]["daily"]
    early = sum(d["views_3s"] for d in daily[:3]) / sum(d["impressions"] for d in daily[:3])
    late = sum(d["views_3s"] for d in daily[-3:]) / sum(d["impressions"] for d in daily[-3:])
    assert late < early, "hook rate decays as frequency and age grow"
    fresh = SimulatedMarket(SC, seed=1).launch([g], budget_per_ad=3000, report_after_days=7)[0]["record"]
    closed = SimulatedMarket(SC, seed=1).launch([g], budget_per_ad=3000)[0]["record"]
    assert not fresh["window_closed"] and closed["window_closed"]
    assert fresh["metrics"]["conversions"] < closed["metrics"]["conversions"]


def test_genomes_differ_and_oracle_beats_random():
    m = SimulatedMarket(SC)
    rng = np.random.default_rng(0)
    vals = [m.expected_value(space.sample(SC.brief, rng)) for _ in range(30)]
    assert max(vals) > 2 * min(vals)
    _, ov = best_genome(m, restarts=1)
    assert ov > max(vals)


def test_drift_changes_truth():
    m = SimulatedMarket(SC, drift_at=5)
    g = template_genome(SC.brief)
    assert m.expected_value(g, 0) != m.expected_value(g, 6)

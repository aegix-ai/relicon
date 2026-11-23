import json
from pathlib import Path

import pytest

from relicon import media
from relicon.genome import Genome
from relicon.genome.priors import template_genome
from relicon.pipeline import cost, planner, policy
from relicon.pipeline.brief import rule_brief
from relicon.pipeline.generate import Pipeline
from relicon.providers import mock
from relicon.providers.prices import UnverifiedPrice, price
from relicon.providers.registry import mock_set

BRIEF = rule_brief("cold-brew coffee for night-shift nurses")


def test_brief_infers_and_marks():
    b = rule_brief("hydrating serum for dry winter skin on reels")
    assert b.vertical == "beauty" and b.platform == "meta_reels"
    assert "price_point" in b.inferred_fields and "platform" not in b.inferred_fields
    assert b.product == "hydrating serum" and b.audience_persona == "dry winter skin on reels"


def test_full_mock_render_6s(tmp_path):
    events = []
    p = Pipeline(short_side=160, on_event=events.append)
    r = p.run(genome=template_genome(BRIEF, 6))
    g: Genome = r["genome"]
    out = Path(r["dir"])
    assert set(r["manifest"]["videos"]) == {"9:16", "1:1", "4:5", "16:9"}
    for a, f in r["manifest"]["videos"].items():
        info = media.probe(f["path"])
        assert {s["codec_type"] for s in info["streams"]} == {"video", "audio"}
        assert abs(float(info["format"]["duration"]) - 6) < 0.3
    assert r["manifest"]["is_mock"] and "MOCK" in r["manifest"]["label"]
    assert Genome.model_validate_json((out / "genome.json").read_text()).id == g.id
    assert all(c["pass"] for c in g.production.qc["technical"].values()), g.production.qc["technical"]
    assert g.production.qc["fidelity"]["fidelity"] >= 0.75
    assert json.loads((out / "cost_report.json").read_text())["actual_total_usd"] == 0
    assert g.production.ai_disclosure["ai_generated"] is True
    assert [e["step"] for e in events][-1] == "package"
    # resume: same genome again -> every expensive step is served from cache
    events.clear()
    Pipeline(short_side=160, on_event=events.append).run(genome=g)
    started = {e["step"] for e in events if e["status"] == "started"}
    assert not any(s.startswith(("render_", "key_", "vo_", "assemble")) for s in started), started


def test_draft_stops_before_render():
    r = Pipeline(short_side=160).run(genome=template_genome(BRIEF, 6), draft=True)
    assert r["manifest"]["draft"] and Path(r["manifest"]["animatic"]).exists()
    assert not (Path(r["dir"]) / "clips").exists()


def test_long_form_plan_has_chapters_and_bible():
    g = template_genome(BRIEF, 180)
    g = planner.plan(g, mock.MockText())
    assert len(g.format.chapters) == 4 and g.production.continuity_bible["characters"]
    seeds = {s.seed for s in g.scenes}
    assert len(seeds) == 1, "lead character keeps one fixed seed"
    assert all(g.brief.product in s.visual_prompt for s in g.scenes)
    assert abs(g.scenes[-1].end_s - 180) < 1e-6 and g.scenes[0].start_s == 0


@pytest.mark.parametrize("d", [6, 10, 15, 20, 30, 45, 60, 90, 120, 180, 300])
def test_plan_timing_covers_duration(d):
    g = planner.plan(template_genome(BRIEF, d), mock.MockText())
    spans = [(s.start_s, s.end_s) for s in g.scenes]
    assert spans[0][0] == 0 and abs(spans[-1][1] - d) < 1e-6
    assert all(abs(a[1] - b[0]) < 1e-6 for a, b in zip(spans, spans[1:]))
    assert g.scenes[-1].purpose == "cta" and abs(g.scenes[-1].start_s - g.text.cta_time_s) < 1e-6


class PaidVideo(mock.MockVideo):
    paid = True

    def estimate(self, clip_seconds):
        return 0.5 * len(clip_seconds)


def test_budget_gate():
    ps = mock_set()
    ps.video = PaidVideo()
    g = planner.plan(template_genome(BRIEF, 15), ps.text)
    with pytest.raises(cost.BudgetExceeded, match="need a job budget"):
        cost.plan_cost(g, ps, None)
    with pytest.raises(cost.BudgetExceeded, match="over budget"):
        cost.plan_cost(g, ps, 1.0)
    assert cost.plan_cost(g, ps, 5.0)["total_estimated_usd"] == 0.5 * len(g.scenes)


def test_unverified_price_refused(monkeypatch):
    with pytest.raises(UnverifiedPrice):
        price("luma:ray-2:720p")
    monkeypatch.setenv("RELICON_PRICE_OVERRIDE_LUMA_RAY_2_720P", "0.2")
    assert price("luma:ray-2:720p") == 0.2


def test_policy_flags_health_claims():
    b = rule_brief("sleep gummies for stressed parents")
    g = planner.plan(template_genome(b, 15), mock.MockText())
    g.scenes[1].vo_line = "Clinically proven to cure anxiety."
    flags, disc = policy.check(g)
    assert policy.blocked(flags) and {f["kind"] for f in flags} >= {"health_claim"}
    assert disc["platform"] == "tiktok" and disc["ai_generated"]

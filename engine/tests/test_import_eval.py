import csv

import pytest

from relicon.genome.priors import template_genome
from relicon.performance.csv_import import LiveConnector, import_csv
from relicon.pipeline.brief import rule_brief
from relicon.store import Store


def _csv(path, rows, header):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header)
        w.writeheader()
        w.writerows(rows)


def test_meta_import_links_by_ad_name_and_reports_unmatched(tmp_path):
    st = Store(f"sqlite:///{tmp_path}/r.db")
    g = template_genome(rule_brief("cold-brew coffee for night-shift nurses"))
    st.put("genome", g.id, g.model_dump(), niche=g.brief.niche)
    hdr = ["Ad name", "Reporting starts", "Reporting ends", "Impressions", "Reach", "Amount spent (USD)",
           "3-second video plays", "Video plays at 25%", "Video plays at 50%", "Video plays at 75%",
           "Video plays at 100%", "Link clicks", "Purchases", "Purchases conversion value"]
    base = dict(zip(hdr[1:], ["2026-11-01", "2026-11-07", "20,000", "15000", "$150.00", "5000", "3000", "2000",
                              "1500", "1000", "120", "6", "180"]))
    _csv(tmp_path / "m.csv", [{"Ad name": g.ad_name("a"), **base}, {"Ad name": "summer promo v2", **base},
                              {"Ad name": "rlc_ffffffffffff_a", **base}], hdr)
    rep = import_csv(st, tmp_path / "m.csv", "meta")
    assert rep["matched"] == 1 and len(rep["unmatched"]) == 2
    rec = st.get("genome", g.id)["results"][0]
    assert rec["is_simulated"] is False and rec["source"] == "csv_meta"
    assert rec["metrics"]["impressions"] == 20000 and abs(rec["metrics"]["hook_rate"] - 0.25) < 1e-9
    assert abs(rec["metrics"]["roas"] - 1.2) < 1e-9


def test_foreign_currency_needs_rate(tmp_path):
    st = Store(f"sqlite:///{tmp_path}/r.db")
    g = template_genome(rule_brief("hydrating serum for dry skin"))
    st.put("genome", g.id, g.model_dump())
    hdr = ["Ad name", "Impressions", "Cost", "Currency"]
    _csv(tmp_path / "t.csv", [{"Ad name": g.ad_name("b"), "Impressions": "5000", "Cost": "100", "Currency": "EUR"}], hdr)
    assert import_csv(st, tmp_path / "t.csv", "tiktok")["errors"]
    rep = import_csv(st, tmp_path / "t.csv", "tiktok", fx_to_usd=1.1)
    assert rep["matched"] == 1 and abs(st.get("genome", g.id)["results"][0]["metrics"]["spend"] - 110) < 1e-6


def test_live_connector_is_a_labeled_stub(monkeypatch):
    with pytest.raises(RuntimeError):
        LiveConnector("meta")
    monkeypatch.setenv("RELICON_LIVE_APIS", "1")
    with pytest.raises(NotImplementedError, match="STUB"):
        LiveConnector("meta").fetch()


@pytest.mark.integration
def test_quick_eval_writes_labeled_report(tmp_path):
    from relicon.evals.report import main
    p = main(quick=True, out_dir=tmp_path)
    text = p.read_text()
    assert "SIMULATED" in text and (tmp_path / "learning_curve.png").exists()
    assert "| relicon |" in text and "| random |" in text and "| llm_only |" in text

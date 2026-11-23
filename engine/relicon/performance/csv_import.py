"""CSV import of real ad results (Meta Ads Manager, TikTok Ads Manager).

Rows link to genomes only through the ad name `rlc_<genome_id>_<variant>`. A row without that name, or with an id
not in the store, is reported as unmatched. Nothing is guessed.
Column names follow the export headers as the presets list them; they were not checked against a live export
(no account here), so `--map` lets you override any column.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

from ..genome.models import Genome, ResultRecord
from .base import derive

NAME = re.compile(r"rlc_([0-9a-f]{12})_([A-Za-z0-9]+)")
PRESETS = {
    "meta": {"ad_name": "Ad name", "date_start": "Reporting starts", "date_end": "Reporting ends",
             "impressions": "Impressions", "reach": "Reach", "spend": "Amount spent (USD)",
             "views_3s": "3-second video plays", "q25": "Video plays at 25%", "q50": "Video plays at 50%",
             "q75": "Video plays at 75%", "q100": "Video plays at 100%", "link_clicks": "Link clicks",
             "conversions": "Purchases", "revenue": "Purchases conversion value", "currency": "Currency"},
    # TikTok reports 2-second views, not 3-second; they are used as the hook count and labeled so in raw.
    "tiktok": {"ad_name": "Ad name", "date_start": "Start time", "date_end": "End time",
               "impressions": "Impressions", "reach": "Reach", "spend": "Cost", "views_3s": "2-second video views",
               "q25": "Video views at 25%", "q50": "Video views at 50%", "q75": "Video views at 75%",
               "q100": "Video views at 100%", "link_clicks": "Clicks (destination)", "conversions": "Conversions",
               "revenue": "Total purchase value", "currency": "Currency"},
}


def _num(v: str | None) -> float:
    if v in (None, "", "-", "--"):
        return 0.0
    return float(str(v).replace(",", "").replace("$", "").replace("%", "").strip())


def import_csv(store, path: str | Path, preset: str = "meta", fx_to_usd: float | None = None,
               window_days: int = 7, window_closed: bool = True, mapping: dict | None = None) -> dict:
    cols = {**PRESETS[preset], **(mapping or {})}
    rep = {"file": str(path), "preset": preset, "rows": 0, "matched": 0, "unmatched": [], "errors": []}
    updated: dict[str, Genome] = {}
    with open(path, newline="", encoding="utf-8-sig") as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):
            rep["rows"] += 1
            name = row.get(cols["ad_name"], "") or ""
            m = NAME.search(name)
            gid = m.group(1) if m else None
            doc = updated.get(gid) or (store.get("genome", gid) if gid else None)
            if doc is None:
                rep["unmatched"].append({"line": i, "ad_name": name,
                                         "why": "no rlc_<genome_id>_<variant> in name" if not m else "genome id not in store"})
                continue
            cur = (row.get(cols.get("currency", ""), "") or "USD").upper()
            if cur != "USD" and fx_to_usd is None:
                rep["errors"].append({"line": i, "why": f"currency {cur}: pass --fx-to-usd, not guessing a rate"})
                continue
            fx = fx_to_usd if cur != "USD" else 1.0
            try:
                counts = {k: _num(row.get(c)) for k, c in cols.items()
                          if k not in ("ad_name", "date_start", "date_end", "currency")}
            except ValueError as e:
                rep["errors"].append({"line": i, "why": f"bad number: {e}"})
                continue
            counts["spend"] *= fx
            counts["revenue"] *= fx
            g = doc if isinstance(doc, Genome) else Genome.model_validate(doc)
            g.results.append(ResultRecord(
                source=f"csv_{preset}", variant=m.group(2), date_start=row.get(cols["date_start"], ""),
                date_end=row.get(cols["date_end"], ""), attribution_window_days=window_days,
                window_closed=window_closed, metrics=derive(counts), is_simulated=False,
                raw={"row": row, "currency": cur, "fx_to_usd": fx,
                     "hook_count": "2-second views" if preset == "tiktok" else "3-second views"}))
            updated[gid] = g
            rep["matched"] += 1
    for gid, g in updated.items():
        store.put("genome", gid, g.model_dump(), niche=g.brief.niche)
    store.put("import", f"{Path(path).name}:{rep['rows']}", rep)
    return rep


class LiveConnector:
    """STUB. Live Meta/TikTok API pulls are not implemented. Enabled only with RELICON_LIVE_APIS=1, and even then
    it raises, so nobody mistakes it for working code. Use CSV import."""

    def __init__(self, platform: str):
        from ..config import get_settings
        if not get_settings().live_apis:
            raise RuntimeError("live APIs are off (set RELICON_LIVE_APIS=1)")
        self.platform = platform

    def fetch(self, **_):
        raise NotImplementedError(f"STUB: live {self.platform} connector not built; export a CSV and run `relicon import`")

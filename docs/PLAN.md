# Plan

Each milestone ends with green tests, a working demo step and a commit.

| Milestone | Builds | Keeps / replaces |
|---|---|---|
| M0 | AUDIT, ARCHITECTURE, PLAN, DECISIONS | - |
| M1 | Remove outputs, pycache, logs, `video_service_old.py`; fix .gitignore; `engine/pyproject.toml`; Makefile; docker compose Postgres; CI | Replaces root `pyproject.toml` (Replit leftover) and the conflicting `engine/requirements.txt` |
| M2 | Genome models, tags, JSON Schema, TS types; generation writes genome.json; dashboard reads it | New `relicon/genome` |
| M3 | Brief, planner (up to 300 s, chapters, continuity bible), storyboard and animatic, cost plan, render, ffmpeg assembly, QC, policy, package; mock providers with real media; Anthropic provider; adapters for Luma, Hailuo, ElevenLabs, OpenAI | Replaces `core/orchestrator.py`, `planning_service.py`, `assembly_service.py`, `cost_tracker.py`. Keeps `providers/*.py` HTTP clients behind adapters. |
| M4 | Simulated market, 5 niches x 2 platforms, genome-only fast mode, oracle | New |
| M5 | Funnel model, Thompson batch, creative director, insights, fatigue, delay, policy snapshots, boundary test | New |
| M6 | `relicon eval`, REPORT.md, charts | New |
| M7 | CSV import (Meta, TikTok presets), live connectors behind a flag | Reuses the OAuth routes |
| M8 | Dashboard: Studio, Campaigns, Ads, Learning, Simulation Lab, Data; demo mode without Supabase | Keeps the existing design system |
| M9 | README with status table, diagram, charts, demo script; one real-provider ad (needs owner keys and budget) | Replaces README |

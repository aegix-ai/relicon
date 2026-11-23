# Audit of the starting code (2026-11-23)

Base: `aegix-ai/relicon` main at `Merge pull request #1` (42 commits, 218 tracked files).
Reference: `aegix-ai/relicon-generator` (public, older engine). Its three report files were read via the GitHub API.

## How this was checked

- Read every engine Python file and the main dashboard and API route files.
- Ran the engine in `MOCK_MODE=true` with Python 3.12 (`uv venv`).
- Ran gitleaks 8.30.1 over the full git history (39 commits scanned, about 30 MB): **no leaks found**.

## Engine (`engine/`)

| Part | Status | Evidence |
|---|---|---|
| `core/orchestrator.py` | **Broken** | Calls `PlanningService.create_video_architecture(brand_name=...)`, but the method takes one `brand_info` dict. Run result: `got an unexpected keyword argument 'brand_name'`, returns `None`. |
| `core/orchestrator.py` audio step | **Broken** | Calls `audio_service.generate_voiceover(...)`, a method that does not exist. |
| `core/orchestrator.py` assembly step | **Broken** | Calls `assemble_final_video(video_clips=..., audio_path=...)`; the real parameters are `video_files`, `audio_file`. |
| Mock mode | **Broken** | `VideoService.__init__` builds `LumaProvider()` and `HailuoProvider()` before checking `MOCK_MODE`, so it raises `LUMA_API_KEY environment variable is required` with no keys. |
| `providers/mock_video.py` | Works partly | Makes a real 6 s blue ffmpeg clip with "MOCK VIDEO" text. Sleeps 3 s per call. |
| `providers/mock_audio.py`, `mock_text.py` | Works partly | ffmpeg sine tone; fixed 3-scene JSON. Do not implement the `AudioGenerator` interface methods the services call. |
| `providers/luma.py` | Untested | Uses `ray-2`, 720p, 5 s via `api.lumalabs.ai/dream-machine/v1/generations`. Luma docs now point to a new "Luma Agents API"; the old endpoint may be legacy. Price in code ($0.40 per 5 s) not verified. |
| `providers/hailuo.py` | Untested | Uses model `video-01`, which is not on MiniMax's current or legacy price page. |
| `providers/elevenlabs.py` | Untested | `eleven_multilingual_v2` TTS and `sound-generation` for music. |
| `providers/openai.py` | Untested | GPT-4o planning. `openai_optimized.py` is not wired anywhere (dead code). |
| `core/cost_tracker.py` | Stub | Fixed constants ($0.40 per scene, $0.15 per OpenAI call, $0.05 per TTS). No budget enforcement before rendering. |
| `core/planning_service.py` | Works with a text provider | 3 fixed scenes, 15 to 18 s only. |
| `core/assembly_service.py` | Partly works | Concat plus audio mux. No captions, no ducking, no loudness target, no multi-aspect export. |
| `core/music_service.py` | Partly works | ffmpeg mix; "built-in tracks" are generated tones. |
| `core/video_service_old.py` | Dead code | Not imported anywhere. |
| `utils/performance_monitor.py` | Dead code | Not imported. |
| `backend/core/job_manager.py` | Works around the broken orchestrator | In-memory jobs, so jobs are lost on restart. |
| `server.py` | Starts, but every generation fails | Depends on the broken orchestrator. |
| Tests | **None** | No test files in the repo. |
| Committed junk | Present | 6 MP4s in `engine/outputs/` (13 MB), 20 `__pycache__/*.pyc`, `engine.log`, `server.log`. |
| Dependencies | Inconsistent | `pyproject.toml` pins `langchain==0.0.340`; `engine/requirements.txt` pins `langchain==0.3.7`. Pydantic 2.5 does not build on Python 3.14. |

## Dashboard and API (`app/`, `lib/`)

| Part | Status | Evidence |
|---|---|---|
| Next.js 14 app, shadcn UI | Works (UI) | Studio, Campaigns, Ads, Analytics, Chat, Settings pages exist. |
| Supabase | Required | `lib/supabase.ts` throws at import if `NEXT_PUBLIC_SUPABASE_*` is missing, so the dashboard cannot run with zero keys. |
| Database schema | **Missing** | Code queries 14 tables (`generated_videos`, `campaigns`, `social_posts`, ...) but no schema file is committed (`db:schema` script points to a missing `supabase-schema.sql`). |
| Auth | Supabase only | `ProtectedRoute` sends users to `/login` without a Supabase session. |
| Meta/TikTok OAuth routes | Partly done | Connect and callback routes exist. TikTok upload is a `TODO` in `app/api/social/publish/route.ts:355`. |
| Analytics sync cron | Untested | Needs live tokens. |
| Hardcoded host | Present | `middleware.ts` CSP lists one Supabase project host. Not a secret. |

## relicon-generator (older engine)

Its own reports say Docker, the frontend and video creation were broken, and that "the only video file is a text mock file". The code is an older copy of the same engine. One thing is better: its orchestrator calls `create_video_architecture(brand_info)` and `assemble_final_video(video_files, audio_file, ...)` with the right signatures. Nothing else is worth porting; the new pipeline replaces both orchestrators.

## Summary

- Works: the UI shell, the provider HTTP clients (unverified against live APIs), ffmpeg basics.
- Broken: the whole generation path, mock mode, the job server.
- Stubbed or fake: cost tracking, music "tracks", TikTok publish.
- Missing: tests, DB schema, genome, simulation, learning, evals, CI.

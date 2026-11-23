# Decisions

Each entry: what was decided and why.

## D1. New package `engine/relicon`, old engine code kept only behind adapters
The old orchestrator, planner, assembly and cost tracker are broken or too narrow (3 fixed scenes, 15 to 18 s). Rewriting them as one job graph costs less than patching four inconsistent call sites. The provider HTTP clients (`engine/providers/luma.py`, `hailuo.py`, `elevenlabs.py`, `openai.py`) are kept and wrapped by adapters in `relicon/providers/legacy.py`.

## D2. Store: SQLAlchemy with a JSON document table; Postgres in docker compose, SQLite fallback
Genomes, results and policies are nested JSON. One `docs` table (kind, id, campaign, niche, data) keeps the code small and works on both databases. Tests and CI use SQLite so they need no services. `make demo` starts Postgres with docker compose when docker is usable and falls back to SQLite with a printed notice.

## D3. Learning model: conjugate weighted Bayesian logistic approximation with a pooling cascade
PyMC or NumPyro would need minutes per fit. The eval runs 5 scenarios x 2 platforms x 4 methods x many seeds x 10+ generations, and CI must finish under 10 minutes. Each funnel step is fit as a Bayesian linear model on the empirical logit of the rate, weighted by binomial information n·p·(1−p) (the standard normal approximation to a binomial GLM). Partial pooling is a cascade: the global posterior is the prior for the vertical, the vertical posterior is the prior for the niche, and the niche posterior is the prior for the brand. Each level's prior is widened by a between-group variance τ² so groups can differ. Fits take milliseconds and give full Gaussian posteriors for Thompson sampling. Cost: posteriors are approximate when counts are tiny; the impression floor (D7) limits that.

## D4. Default real video provider: MiniMax-Hailuo-02 at 768P, 6 s
Checked on 2026-11-23 at https://platform.minimax.io/docs/guides/pricing-video : Hailuo-02 is $0.28 per 768P 6 s clip (listed under Legacy). The current MiniMax-H3 is $0.08 per second at 768P ($0.48 per 6 s). Hailuo-02 is cheaper per clip and the request format matches the existing client. The model name is configurable (`RELICON_MINIMAX_MODEL`).

## D5. Luma price is unverified, so Luma is blocked from paid renders by default
Luma's pricing page says web credits do not apply to the API and links a billing page that could not be read; third-party sites disagree ($0.15 to $0.35 per second at 720p). Rule 4 forbids guessing. The cost planner refuses any provider whose price is unverified unless the owner sets `RELICON_PRICE_OVERRIDE_LUMA_PER_S`.

## D6. Mock judge measures only what can be measured from pixels and audio without a model
In zero-key mode the "VLM judge" cannot honestly score hook type or style. The mock judge checks fields it can measure with ffmpeg: duration, aspect ratio, scene count (scene-cut detection), CTA end-card timing, captions present, voice present. Other fields report `not_evaluated`. With `ANTHROPIC_API_KEY`, a Claude vision judge scores the rest from extracted frames.

## D7. Evidence floor default: 1,000 impressions per variant
A 1% CTR at 1,000 impressions gives about 10 clicks, the least that gives a usable interval. Configurable with `RELICON_MIN_IMPRESSIONS`.

## D8. LLM-only baseline in zero-key mode
Without a key, the "LLM-only, no data" baseline uses the mock creative director with priors only and no posterior. With `ANTHROPIC_API_KEY`, it uses claude-opus-5-5. The report states which one ran.

## D9. Work on branch `feat/self-improving-engine`
The repo's main branch is untouched until the owner merges.

## D10. New MiniMax client instead of reusing `engine/providers/hailuo.py`
The old client appends random "cinematography" phrases and a random seed tag to every prompt, so the video would no longer match its genome, and it hardcodes model `video-01` and `720p`, neither of which is on MiniMax's price page. `relicon/providers/minimax.py` keeps the same endpoints with the prompt unchanged and a configurable model. Untested against the live API (no key in this environment).

## D11. Music and sound effects are synthesized locally in every mode
ElevenLabs lists Music at $0.15/min and Sound Effects at $0.12/min (checked 2026-11-23), but its Music endpoint could not be checked against docs here. Local synthesis costs $0, has a clear license (`generated:local`), and keeps real renders cheap. A paid music provider can be added behind `MusicProvider`.

## D12. Safe zones are conservative fractions, not pixel specs
TikTok, Reels and Shorts move their UI between app versions. `assemble.SAFE` keeps captions out of the top 10 to 14%, bottom 20 to 22% and the right-side button rail. QC checks every text box against these rects. Tighten them if a platform publishes exact numbers.

## D13. Hard cuts use concat, only real transitions use xfade
A chain of 1-frame xfades stopped the video stream early (7.5 s of video in a 15 s file) while the container still reported 15 s. Cuts now use concat, crossfade/whip/fade-to-black use xfade, all at a 1/25 timebase, and QC checks video and audio stream durations separately.

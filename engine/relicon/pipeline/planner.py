"""Step 3: genome -> script and scene plan. Timing is rule-based (so the structure is always
right); words come from an LLM when a key is set, else from templates.

Ads over 60 s get chapters and a continuity bible (characters, product look, locations,
palette, fixed seeds) that is prefixed to every visual prompt.
"""
from __future__ import annotations

import hashlib
import json

from ..genome.models import Chapter, Genome, SceneGenome
from ..providers.base import TextProvider

BEATS = {
    "hook_problem_solution_cta": ["hook", "problem", "solution", "proof", "cta"],
    "story": ["hook", "setup", "conflict", "turn", "resolution", "cta"],
    "demo": ["hook", "demo_step", "demo_step", "result", "cta"],
    "listicle": ["hook", "item", "item", "item", "cta"],
    "comparison": ["hook", "old_way", "new_way", "proof", "cta"],
    "testimonial_style": ["hook", "testimonial", "proof", "cta"],
    "founder_story": ["hook", "founder_why", "build", "result", "cta"],
    "unboxing": ["hook", "unbox", "reveal", "use", "cta"],
    "problem_agitate_solve": ["hook", "problem", "agitate", "solve", "cta"],
}
SHOT = {"hook": "close_up", "problem": "medium", "solution": "macro", "proof": "medium", "cta": "text_card",
        "demo_step": "pov", "result": "close_up", "item": "macro", "old_way": "wide", "new_way": "close_up",
        "testimonial": "medium", "unbox": "pov", "reveal": "macro", "use": "medium"}
ANGLE = {"pain": ("tired of settling for less", "no more bad days"),
         "desire": ("wanting something better", "the upgrade you deserve"),
         "status": ("looking like everyone else", "the one people ask about"),
         "savings": ("paying too much", "more for less"),
         "convenience": ("short on time", "zero effort, every time"),
         "fear_of_missing_out": ("missing what everyone else found", "before it sells out")}
HOOK = {"question": "Still {pain}?", "bold_claim": "This {product} changes everything.",
        "pattern_interrupt": "Stop. Look at this.", "problem_shot": "This is what {pain} looks like.",
        "result_first": "Here is the result first.", "social_proof": "Thousands of {persona} already switched.",
        "curiosity_gap": "Nobody tells {persona} this."}
LINES = {"problem": "You know the feeling, {pain}.", "agitate": "And it only gets worse every week.",
         "solution": "Meet {product}. {benefit}.", "solve": "{product} fixes it. {benefit}.",
         "proof": "{proof}", "setup": "Meet someone like you.", "conflict": "Every day felt the same.",
         "turn": "Then came {product}.", "resolution": "Now it is {benefit}.", "demo_step": "Watch how simple it is.",
         "result": "That is the difference.", "item": "Reason {n}: {benefit}.", "old_way": "The old way is slow.",
         "new_way": "The new way is {product}.", "testimonial": "I tried {product} and never went back.",
         "founder_why": "I built {product} because I needed it.", "build": "We tested it again and again.",
         "unbox": "Here is what is inside.", "reveal": "Look at that finish.", "use": "And it just works.",
         "cta": "{cta} {offer}"}
PROOF = {"testimonial": "Real customers say it works.", "demo": "See it work right here.",
         "stat": "Most people notice a difference in a week.", "expert": "Experts helped design it.",
         "ugc_review": "The reviews say it all.", "before_after": "Before, and after."}


def _seed(*parts: object) -> int:
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def fit_beats(structure: str, n: int) -> list[str]:
    beats = BEATS[structure]
    if n <= 2:
        return ["hook", "cta"][:max(n, 1)] if n == 2 else ["hook"]
    middle = beats[1:-1]
    return ["hook"] + [middle[i * len(middle) // (n - 2)] for i in range(n - 2)] + ["cta"]


def continuity_bible(g: Genome) -> dict:
    b, v = g.brief, g.visual
    lead = {"id": "lead", "sheet": f"{b.audience_persona}, same face, same hair, same outfit in every shot",
            "seed": _seed(g.id, "lead")} if v.human_presence != "none" else None
    return {"characters": [lead] if lead else [],
            "product_look": f"{b.product}, same packaging, same colors, label facing camera",
            "locations": [v.setting], "palette": v.palette, "lighting": v.lighting,
            "seed_base": _seed(g.id, "bible"),
            "reference_assets": ["bible/lead_sheet.png", "bible/product.png"] if lead else ["bible/product.png"]}


def timing(g: Genome, n: int) -> list[tuple[float, float]]:
    d, cta = float(g.format.duration_s), g.text.cta_time_s
    if n == 1:
        return [(0.0, d)]
    hook_end = cta if n == 2 else min(3.0, cta)
    spans = [(0.0, hook_end)]
    mid = n - 2
    for i in range(mid):
        a = hook_end + (cta - hook_end) * i / mid
        spans.append((a, hook_end + (cta - hook_end) * (i + 1) / mid))
    spans.append((cta, d))
    return [(round(a, 2), round(b, 2)) for a, b in spans]


def rule_lines(g: Genome, beats: list[str]) -> list[dict]:
    b = g.brief
    pain, benefit = ANGLE[g.narrative.angle]
    ctx = {"product": b.product, "persona": b.audience_persona, "pain": pain.format(product=b.product),
           "benefit": benefit.capitalize(), "cta": g.text.cta_text + ".",
           "offer": (f"{g.offer_mechanics.discount_pct}% off today." if g.offer_mechanics.discount_pct else b.offer)}
    proofs = g.narrative.proof_types or ["demo"]
    out, item_n = [], 0
    for i, beat in enumerate(beats):
        if beat == "item":
            item_n += 1
        line = HOOK[g.hook.hook_type] if beat == "hook" else LINES.get(beat, "{benefit}.")
        line = line.format(**ctx, n=item_n, proof=PROOF[proofs[i % len(proofs)]])
        words = line.split()
        dense = g.text.text_density
        ost = " ".join(words[: {"low": 3, "medium": 5, "high": 8}[dense]]) if beat in ("hook", "cta") or dense == "high" else ""
        out.append({"vo_line": line, "on_screen_text": ost,
                    "visual": f"{SHOT.get(beat, 'medium').replace('_', ' ')} of {b.product}, {beat.replace('_', ' ')} moment"})
    return out


def llm_lines(g: Genome, beats: list[str], spans: list[tuple[float, float]], llm: TextProvider) -> list[dict]:
    from ..providers.anthropic import parse_json
    spec = [{"beat": bt, "seconds": round(e - s, 1), "max_words": int((e - s) * g.audio.voice.pace_wpm / 60 * 0.85)}
            for bt, (s, e) in zip(beats, spans)]
    prompt = ("Write the script for this ad. Follow the genome exactly (hook type, angle, tone, proof types, CTA).\n"
              f"Genome: {g.model_dump_json(include={'brief', 'hook', 'narrative', 'visual', 'text', 'offer_mechanics'})}\n"
              f"Scenes: {json.dumps(spec)}\nReturn JSON {{\"scenes\": [{{\"vo_line\", \"on_screen_text\", \"visual\"}}]}} "
              "with one entry per scene, VO within max_words, no medical or financial promises.")
    data = parse_json(llm.complete("You are a direct-response ad scriptwriter.", prompt, 3000, role="planner"))
    rows = data["scenes"]
    if len(rows) != len(beats):
        raise ValueError("LLM returned the wrong number of scenes")
    return rows


def plan(g: Genome, llm: TextProvider, video_model: str = "mock-video") -> Genome:
    g = g.model_copy(deep=True).normalize()
    n = g.format.scene_count
    beats = fit_beats(g.format.structure, n)
    spans = timing(g, len(beats))
    rows = rule_lines(g, beats) if llm.is_mock else llm_lines(g, beats, spans, llm)
    long_form = g.format.duration_s > 60
    bible = continuity_bible(g)
    g.production.continuity_bible = bible if long_form else {}
    chapter_len = 45.0
    g.format.chapters = ([Chapter(title=f"Part {i + 1}", start_s=i * chapter_len,
                                  end_s=min((i + 1) * chapter_len, g.format.duration_s))
                          for i in range(int(-(-g.format.duration_s // chapter_len)))] if long_form else [])
    prefix = (f"[{bible['product_look']}; {'; '.join(c['sheet'] for c in bible['characters'])}; "
              f"{g.visual.setting}, {g.visual.palette} palette, {g.visual.lighting} light] ") if long_form else ""
    style = f"{g.visual.style.replace('_', ' ')}, {g.visual.camera_motion.replace('_', ' ')} camera, " \
            f"{g.visual.human_presence.replace('_', ' ')} on screen"
    scenes = []
    for i, (beat, (s, e), row) in enumerate(zip(beats, spans, rows)):
        chap = int(s // chapter_len) if long_form else 0
        prev_chap = int(spans[i - 1][0] // chapter_len) if (long_form and i) else chap
        trans = "fade_black" if chap != prev_chap else (
            "cut" if i == 0 or g.hook.motion_intensity == "high" else
            "crossfade" if g.narrative.tone in ("calm", "warm") else "whip" if g.hook.motion_intensity == "medium" and i % 3 == 0 else "cut")
        lead_seed = bible["characters"][0]["seed"] if (long_form and bible["characters"]) else _seed(g.id, i)
        scenes.append(SceneGenome(
            scene_id=f"s{i + 1:02d}", start_s=s, end_s=e, purpose=beat, chapter=chap,
            visual_prompt=f"{prefix}{row['visual']}, {style}", shot_type=SHOT.get(beat, "medium"),
            model=video_model, seed=lead_seed, reference_assets=bible["reference_assets"] if long_form else [],
            vo_line=row["vo_line"], on_screen_text=row.get("on_screen_text", ""), transition=trans))
    g.scenes = scenes
    g.hook.on_screen_text = scenes[0].on_screen_text
    g.narrative.claims = [sc.vo_line for sc in scenes if sc.purpose in ("proof", "result", "solution", "solve")]
    return g

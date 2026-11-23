"""Step 1: one sentence -> structured brief. Never asks the user; marks what it inferred."""
from __future__ import annotations

import json
import re

from ..genome.models import Brief
from ..providers.base import TextProvider

VERTICALS = {
    "food_bev": ["coffee", "tea", "snack", "drink", "brew", "protein", "juice", "kombucha", "energy", "chocolate"],
    "beauty": ["skincare", "serum", "moistur", "makeup", "lipstick", "sunscreen", "shampoo", "skin"],
    "fitness": ["gym", "workout", "yoga", "fitness", "dumbbell", "running", "bike"],
    "home": ["candle", "mattress", "pillow", "kitchen", "cleaner", "vacuum", "sofa"],
    "saas": ["app", "software", "saas", "tool", "platform", "crm", "plugin"],
    "fashion": ["shoe", "sneaker", "dress", "hoodie", "jacket", "watch", "bag"],
    "pets": ["dog", "cat", "pet", "puppy"],
    "health": ["supplement", "vitamin", "sleep", "gummies", "posture"],
}
DEFAULT_PRICE = {"food_bev": 28, "beauty": 42, "fitness": 79, "home": 65, "saas": 19, "fashion": 89,
                 "pets": 35, "health": 39, "general": 40}
PLATFORM_WORDS = {"tiktok": "tiktok", "reels": "meta_reels", "instagram": "meta_reels", "facebook": "meta_feed",
                  "shorts": "youtube_shorts", "youtube": "youtube_instream"}


def slug(s: str, n: int = 3) -> str:
    words = [w for w in re.findall(r"[a-z0-9]+", s.lower()) if w not in {"a", "an", "the", "for", "of", "and", "to"}]
    return "_".join(words[:n]) or "general"


def rule_brief(sentence: str, platform: str | None = None, objective: str | None = None) -> Brief:
    s = sentence.strip().rstrip(".")
    low = s.lower()
    product, audience = s, ""
    if " for " in low:
        product, audience = re.split(r"\s+for\s+", s, maxsplit=1, flags=re.I)
    vertical = next((v for v, kws in VERTICALS.items() if any(k in low for k in kws)), "general")
    inferred = ["vertical", "niche", "price_point", "offer", "brand"]
    plat = platform or next((p for w, p in PLATFORM_WORDS.items() if w in low), None)
    if plat is None:
        plat = "tiktok"
        inferred.append("platform")
    if objective is None:
        inferred.append("objective")
    if not audience:
        inferred.append("audience_persona")
    return Brief(product=product.strip(), offer="", price_point=DEFAULT_PRICE[vertical], vertical=vertical,
                 niche=f"{slug(product, 2)}__{slug(audience, 2)}" if audience else slug(product, 3),
                 brand="unbranded", audience_persona=audience.strip() or "broad adult audience",
                 platform=plat, objective=objective or "roas", inferred_fields=inferred)


SYSTEM = "You turn one-sentence ad requests into JSON briefs. Never ask questions; infer and list inferred fields."


def expand(sentence: str, llm: TextProvider, platform: str | None = None, objective: str | None = None) -> Brief:
    base = rule_brief(sentence, platform, objective)
    if llm.is_mock:
        return base
    from ..providers.anthropic import parse_json
    prompt = (f"Request: {sentence!r}\nReturn JSON with keys product, offer, price_point (number, USD), vertical, "
              f"niche (snake_case), brand, audience_persona, constraints (list), inferred_fields (list of keys you guessed). "
              f"Platform is {base.platform}, objective {base.objective}. Draft: {base.model_dump_json()}")
    data = parse_json(llm.complete(SYSTEM, prompt, 800, role="planner"))
    keep = {k: data[k] for k in ("product", "offer", "price_point", "vertical", "niche", "brand",
                                 "audience_persona", "constraints", "inferred_fields") if k in data}
    return Brief.model_validate({**json.loads(base.model_dump_json()), **keep})

"""Public scenario definitions: the brief and market settings an advertiser would know.
The response functions live in simulator/truth and are never shown to the learner."""
from __future__ import annotations

from dataclasses import dataclass

from ..genome.models import Brief

NICHES = {
    "coffee_nightshift": ("food_bev", "cold-brew coffee", "night-shift nurses", 28.0),
    "skincare_dry": ("beauty", "hydrating serum", "people with dry winter skin", 42.0),
    "skincare_teen": ("beauty", "acne patches", "teens with breakouts", 18.0),
    "fitness_home": ("fitness", "adjustable dumbbells", "people in small apartments", 129.0),
    "saas_freelance": ("saas", "invoicing app", "freelance designers", 15.0),
    "pets_senior": ("pets", "joint chews", "owners of senior dogs", 34.0),
}
PLATFORMS = ("tiktok", "meta_reels")


@dataclass(frozen=True)
class Scenario:
    name: str
    niche: str
    vertical: str
    platform: str
    brief: Brief
    seed: int

    @property
    def sentence(self) -> str:
        return f"{self.brief.product} for {self.brief.audience_persona}"


def all_scenarios() -> dict[str, Scenario]:
    out = {}
    for i, (niche, (vertical, product, persona, price)) in enumerate(NICHES.items()):
        for j, plat in enumerate(PLATFORMS):
            name = f"{niche}@{plat}"
            brief = Brief(product=product, price_point=price, vertical=vertical, niche=niche, brand=f"{niche}_brand",
                          audience_persona=persona, platform=plat, objective="roas")
            out[name] = Scenario(name, niche, vertical, plat, brief, seed=1000 + 17 * i + j)
    return out


def get(name: str) -> Scenario:
    sc = all_scenarios()
    if name not in sc:
        raise KeyError(f"unknown scenario {name!r}; choose from {sorted(sc)}")
    return sc[name]

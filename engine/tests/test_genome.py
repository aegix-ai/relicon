import json

import numpy as np

from relicon.config import REPO_ROOT
from relicon.genome import Brief, Genome
from relicon.genome import space
from relicon.genome.models import cta_bounds
from relicon.genome.export import json_schema, typescript

BRIEF = Brief(product="cold brew", niche="coffee_nightshift", vertical="food_bev", platform="tiktok")


def test_every_leaf_is_tagged():
    tags = space.tag_map()
    assert set(tags.values()) == {"learnable", "fixed", "derived"}
    assert tags["brief.platform"] == "fixed"
    assert tags["hook.hook_type"] == "learnable"
    assert tags["production.total_cost_usd"] == "derived"
    assert len(space.learnable_fields()) >= 30


def test_sample_and_roundtrip():
    rng = np.random.default_rng(0)
    for _ in range(50):
        g = space.sample(BRIEF, rng)
        g2 = Genome.model_validate_json(g.model_dump_json())
        assert g2 == g
        assert g.format.aspect_ratio == "9:16"
        lo, hi = cta_bounds(g.format.duration_s)
        assert lo - 1e-6 <= g.text.cta_time_s <= hi + 1e-6
        assert g.ad_name().startswith(f"rlc_{g.id}_")


def test_platform_caps_duration():
    rng = np.random.default_rng(1)
    b = BRIEF.model_copy(update={"platform": "youtube_shorts"})
    assert all(space.sample(b, rng).format.duration_s <= 60 for _ in range(40))


def test_mutate_changes_only_learnable_fields():
    rng = np.random.default_rng(2)
    g = space.sample(BRIEF, rng)
    c = space.mutate(g, rng, n_fields=3)
    assert c.brief == g.brief and c.identity.parent_ids == [g.id] and c.id != g.id
    assert 0 < space.distance(g, c) <= 3 / len(space.learnable_fields()) + 1e-9


def test_committed_schema_and_types_are_current():
    s = json_schema()
    assert json.loads((REPO_ROOT / "schemas/genome.v1.json").read_text()) == s
    assert (REPO_ROOT / "lib/genome.ts").read_text() == typescript(s)

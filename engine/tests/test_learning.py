import numpy as np
import pytest

from relicon.genome import space
from relicon.genome.models import ResultRecord, SceneGenome
from relicon.genome.priors import template_genome
from relicon.learning import credit, fatigue, features, policy
from relicon.learning.data import Observation
from relicon.learning.engine import Learner, learn, next_for, propose_for_brief
from relicon.pipeline.brief import rule_brief
from relicon.store import Store

B = rule_brief("cold-brew coffee for night-shift nurses")
HOOK = "hook.hook_type"


def synth(n, rng, brief=B, window_closed=True, imps=20000, effect=0.6):
    """Known truth: hook_type=question raises the hook logit by `effect`; nothing else matters."""
    out = []
    for _ in range(n):
        g = space.sample(brief, rng)
        z = -1.2 + (effect if space.get(g, HOOK) == "question" else 0.0)
        h = 1 / (1 + np.exp(-z))
        v3 = rng.binomial(imps, h)
        clicks = rng.binomial(v3, 0.03)
        conv = rng.binomial(clicks, 0.05)
        m = {"impressions": imps, "views_3s": v3, "q25": int(v3 * .6), "q50": int(v3 * .4), "q75": int(v3 * .3),
             "q100": int(v3 * .2), "link_clicks": clicks, "conversions": conv, "spend": 150.0, "revenue": conv * 30.0}
        out.append(Observation(g, ResultRecord(source="csv_meta", is_simulated=False, metrics=m, window_closed=window_closed)))
    return out


def test_features_shape_and_roundtrip():
    x = features.encode(template_genome(B))
    assert x.shape == (features.dim(),) and x[0] == 1 and features.dim() > 100


def test_model_recovers_known_effect_and_insight():
    obs = synth(120, np.random.default_rng(0))
    lr = Learner(B).fit(obs)
    q = template_genome(B); space.put(q, HOOK, "question")
    o = template_genome(B); space.put(o, HOOK, "problem_shot")
    X = features.encode_many([q, o])
    mu, _ = lr.model.logits(X, "hook")
    assert 0.4 < mu[0] - mu[1] < 0.8
    ins = [i for i in lr.insights() if i["field"] == HOOK and i["level"] == "question" and i["step"] == "hook"]
    assert ins and ins[0]["effect_rel"] > 0 and ins[0]["ci90_rel"][0] > 0


def test_floor_and_delay_rules():
    rng = np.random.default_rng(1)
    obs = synth(10, rng, imps=500) + synth(10, rng, window_closed=False)
    lr = Learner(B, floor=1000).fit(obs)
    assert lr.model.excluded == 10 and lr.model.fits["hook"].n_obs == 10
    assert lr.model.fits["cvr"].n_obs == 0, "open attribution window -> conversions not used"


def test_thompson_batch_is_distinct_and_explained():
    lr = Learner(B).fit(synth(60, np.random.default_rng(2)))
    batch = lr.next_batch(8, np.random.default_rng(3), generation=4, policy_version="p0004")
    assert len(batch) == 8 and len({space.fingerprint(g) for g in batch}) == 8
    kinds = [g.identity.selection_reason.split(":")[0] for g in batch]
    assert kinds.count("explore") == 2 and kinds.count("thompson") == 6
    assert all(g.identity.generation == 4 and g.identity.policy_version == "p0004" for g in batch)
    assert sum(space.get(g, HOOK) == "question" for g in batch) >= 4, "exploits the known winner"


def test_pooling_borrows_from_sibling_niche():
    rng = np.random.default_rng(4)
    sib = rule_brief("iced tea for night-shift nurses")
    assert sib.vertical == B.vertical and sib.niche != B.niche
    lr = Learner(B).fit(synth(80, rng, brief=sib))
    assert lr.model.fits["hook"].n_by_level[1] == 80
    q = template_genome(B); space.put(q, HOOK, "question")
    mu, _ = lr.model.logits(features.encode_many([q, template_genome(B)]), "hook")
    assert mu[0] - mu[1] > 0.3, "vertical data informs a niche with no data"


def test_scene_credit_finds_leaky_beat():
    rng = np.random.default_rng(5)
    obs = []
    for _ in range(30):
        g = template_genome(B)
        g.scenes = [SceneGenome(scene_id="s0", purpose="hook", start_s=0, end_s=3.75),
                    SceneGenome(scene_id="s1", purpose="problem", start_s=3.75, end_s=7.5),
                    SceneGenome(scene_id="s2", purpose="solution", start_s=7.5, end_s=11.25),
                    SceneGenome(scene_id="s3", purpose="cta", start_s=11.25, end_s=15)]
        v3 = 10000
        s = [1.0, 0.9, 0.45, 0.4, 0.36]  # the problem window loses viewers much faster
        m = {"views_3s": v3, "q25": int(v3 * s[1] * rng.uniform(.98, 1.02)), "q50": int(v3 * s[2]),
             "q75": int(v3 * s[3]), "q100": int(v3 * s[4]), "impressions": 40000}
        obs.append(Observation(g, ResultRecord(source="csv_meta", is_simulated=False, metrics=m)))
    c = credit.scene_credit(obs)
    assert next(iter(c)) == "problem" and c["problem"]["rel_hazard"] > 1.5


def test_fatigue_estimate():
    obs = []
    for _ in range(5):
        daily = [{"day": d, "impressions": 3000, "views_3s": int(3000 * 0.3 * 0.95 ** d)} for d in range(7)]
        obs.append(Observation(template_genome(B), ResultRecord(source="csv_meta", is_simulated=False, metrics={"impressions": 21000},
                                                                raw={"daily": daily})))
    f = fatigue.estimate(obs)
    assert -0.07 < f["per_day"] < -0.03 and fatigue.needs_refresh(7, f)


def test_store_learn_snapshot_rollback_and_propose(tmp_path):
    st = Store(f"sqlite:///{tmp_path}/r.db")
    assert propose_for_brief(B, st) is None, "no policy yet -> pipeline falls back to the template"
    for o in synth(40, np.random.default_rng(6)):
        o.genome.results = [o.record]
        st.put("genome", o.genome.id, o.genome.model_dump(), niche=B.niche)
    p1 = learn(st, B.niche)
    assert p1["version"] == "p0001" and len(p1["obs_ids"]) == 40
    for o in synth(40, np.random.default_rng(7)):
        o.genome.results = [o.record]
        st.put("genome", o.genome.id, o.genome.model_dump(), niche=B.niche)
    p2 = learn(st, B.niche)
    assert p2["version"] == "p0002" and p2["parent"] == "p0001" and policy.active(st, B.niche)["version"] == "p0002"
    policy.rollback(st, B.niche, "p0001")
    assert policy.active(st, B.niche)["version"] == "p0001"
    batch = next_for(st, B, k=4)
    assert len(batch) == 4 and all(g.identity.policy_version == "p0001" for g in batch)
    g = propose_for_brief(B, st)
    assert g is not None and g.identity.selection_reason
    with pytest.raises(KeyError):
        policy.rollback(st, B.niche, "p0099")

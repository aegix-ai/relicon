from relicon.cli import main
from relicon.store import Store


import pytest


@pytest.mark.integration
def test_zero_key_demo_loop():
    """Full loop with no keys, no network: render, simulate, learn, propose, render."""
    assert main(["--short-side", "160", "demo", "--quick"]) == 0
    st = Store()
    from relicon.learning.policy import active
    pol = active(st, "coffee_nightshift")
    assert pol and pol["is_simulated"] and len(pol["obs_ids"]) == 8
    ads = st.list("ad")
    assert len(ads) == 2


def test_store_roundtrip(tmp_path):
    s = Store(f"sqlite:///{tmp_path}/t.db")
    s.put("genome", "g1", {"a": 1}, campaign="c", niche="n")
    assert s.get("genome", "g1") == {"a": 1}
    assert len(s.list("genome", campaign="c")) == 1

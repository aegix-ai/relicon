from relicon.cli import main
from relicon.store import Store


def test_cli_runs():
    assert main(["demo"]) == 0


def test_store_roundtrip(tmp_path):
    s = Store(f"sqlite:///{tmp_path}/t.db")
    s.put("genome", "g1", {"a": 1}, campaign="c", niche="n")
    assert s.get("genome", "g1") == {"a": 1}
    assert len(s.list("genome", campaign="c")) == 1

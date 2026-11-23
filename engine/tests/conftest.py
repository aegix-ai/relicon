import pytest


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Every test gets its own RELICON_HOME and SQLite DB; no keys leak in."""
    monkeypatch.setenv("RELICON_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "HAILUO_API_KEY", "MINIMAX_API_KEY", "LUMA_API_KEY",
              "ELEVENLABS_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("RELICON_PROVIDERS", "mock")
    yield

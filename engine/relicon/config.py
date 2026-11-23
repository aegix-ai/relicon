"""Runtime settings, all from environment variables. Zero keys is a valid setup."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _f(name: str, default: float) -> float:
    return float(os.getenv(name, default))


@dataclass
class Settings:
    home: Path = field(default_factory=lambda: Path(os.getenv("RELICON_HOME", REPO_ROOT / ".relicon")))
    database_url: str = ""
    default_budget_usd: float = field(default_factory=lambda: _f("RELICON_BUDGET_USD", 5.0))
    lufs_target: float = field(default_factory=lambda: _f("RELICON_LUFS_TARGET", -14.0))
    true_peak_db: float = field(default_factory=lambda: _f("RELICON_TRUE_PEAK_DB", -1.5))
    min_impressions: int = field(default_factory=lambda: int(_f("RELICON_MIN_IMPRESSIONS", 1000)))
    exploration_share: float = field(default_factory=lambda: _f("RELICON_EXPLORATION_SHARE", 0.25))
    live_apis: bool = field(default_factory=lambda: os.getenv("RELICON_LIVE_APIS", "0") == "1")
    providers: str = field(default_factory=lambda: os.getenv("RELICON_PROVIDERS", "mock"))  # mock | real
    anthropic_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    openai_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    minimax_key: str = field(default_factory=lambda: os.getenv("HAILUO_API_KEY", os.getenv("MINIMAX_API_KEY", "")))
    luma_key: str = field(default_factory=lambda: os.getenv("LUMA_API_KEY", ""))
    elevenlabs_key: str = field(default_factory=lambda: os.getenv("ELEVENLABS_API_KEY", ""))

    def __post_init__(self) -> None:
        self.home = Path(self.home)
        if not self.database_url:
            self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{self.home / 'relicon.db'}")

    @property
    def outputs(self) -> Path:
        p = self.home / "outputs"
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def cache(self) -> Path:
        p = self.home / "cache"
        p.mkdir(parents=True, exist_ok=True)
        return p


def get_settings() -> Settings:
    s = Settings()
    s.home.mkdir(parents=True, exist_ok=True)
    return s

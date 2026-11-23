"""Document store: one JSON table on Postgres (docker compose) or SQLite (fallback, tests)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Iterable

from sqlalchemy import JSON, Column, DateTime, MetaData, String, Table, create_engine, select, delete

from .config import get_settings

meta = MetaData()
docs = Table(
    "relicon_docs", meta,
    Column("kind", String(32), primary_key=True),
    Column("id", String(96), primary_key=True),
    Column("campaign", String(96), index=True),
    Column("niche", String(96), index=True),
    Column("created_at", DateTime(timezone=True)),
    Column("data", JSON),
)

KINDS = {"genome", "ad", "result", "campaign", "policy", "insight", "job", "sim_run", "import"}


class Store:
    def __init__(self, url: str | None = None):
        url = url or get_settings().database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        self.engine = create_engine(url, future=True)
        meta.create_all(self.engine)

    def put(self, kind: str, id: str, data: dict[str, Any], campaign: str = "", niche: str = "") -> None:
        assert kind in KINDS, kind
        data = json.loads(json.dumps(data, default=str))
        with self.engine.begin() as c:
            c.execute(delete(docs).where(docs.c.kind == kind, docs.c.id == id))
            c.execute(docs.insert().values(kind=kind, id=id, campaign=campaign, niche=niche,
                                           created_at=datetime.now(timezone.utc), data=data))

    def get(self, kind: str, id: str) -> dict[str, Any] | None:
        with self.engine.connect() as c:
            row = c.execute(select(docs.c.data).where(docs.c.kind == kind, docs.c.id == id)).first()
        return row[0] if row else None

    def list(self, kind: str, campaign: str | None = None, niche: str | None = None, limit: int = 10_000) -> list[dict]:
        q = select(docs.c.data).where(docs.c.kind == kind)
        if campaign:
            q = q.where(docs.c.campaign == campaign)
        if niche:
            q = q.where(docs.c.niche == niche)
        q = q.order_by(docs.c.created_at).limit(limit)
        with self.engine.connect() as c:
            return [r[0] for r in c.execute(q)]

    def put_many(self, kind: str, items: Iterable[tuple[str, dict, str, str]]) -> None:
        for id, data, campaign, niche in items:
            self.put(kind, id, data, campaign, niche)

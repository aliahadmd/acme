"""SQLAlchemy engine + session factory (sync — see AGENTS.md for the async policy)."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, pool
from sqlmodel import Session, create_engine

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    url = get_settings().database_url
    if url.startswith("sqlite"):
        # In-memory sqlite needs a shared connection (used by tests / schema export).
        return create_engine(
            url, connect_args={"check_same_thread": False}, poolclass=pool.StaticPool
        )
    return create_engine(url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    with Session(get_engine()) as session:
        yield session

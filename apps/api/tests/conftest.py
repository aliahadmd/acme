import os

# Set before app modules import Settings (which fail fast on a missing DATABASE_URL).
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("ENVIRONMENT", "local")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")

import pytest  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from app.db.session import get_engine  # noqa: E402


@pytest.fixture(autouse=True)
def _database():
    """Fresh sqlite schema per test — keeps tests DB-free (no postgres needed)."""
    SQLModel.metadata.create_all(get_engine())
    yield
    SQLModel.metadata.drop_all(get_engine())

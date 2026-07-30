"""
Declarative base for all ORM models, plus a simple table-creation helper.

No Alembic yet (see Sprint 2 auth notes) — init_db() runs create_all()
on startup, which is fine for one model but should be replaced with real
migrations before a second model is added.
"""

from sqlalchemy.orm import DeclarativeBase

from app.db.session import engine


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    # Import models here (not at module top) so they're registered on
    # Base.metadata before create_all runs, without causing circular imports.
    from app.models import document, document_chunk, knowledge_edge, knowledge_node, user  # noqa: F401

    Base.metadata.create_all(bind=engine)

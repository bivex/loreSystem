"""Minimal base helper for SQLite repository implementations.

Extracted from the monolithic ``sqlite_repositories.py``. Unlike the
in-memory repositories (which share a trivial ``dict`` storage and so can
share a generic CRUD base), the SQLite repositories embed entity-specific
SQL in every method: ``save`` hard-codes the table column list,
``find_by_id`` hard-codes the table name, etc. A behavior-preserving
refactor therefore cannot abstract the SQL into a generic base class.

This module instead provides only the thin shared plumbing every SQLite
repository relies on: a typed ``db`` reference (a
:class:`~src.infrastructure.sqlite.database.SQLiteDatabase`) and a couple
of convenience execution helpers. Concrete repositories continue to own
their SQL verbatim.
"""

from __future__ import annotations

from typing import Any, Optional, Sequence

from src.infrastructure.sqlite.database import SQLiteDatabase


class SQLiteRepositoryBase:
    """Shared plumbing for SQLite-backed repositories.

    Subclasses receive a :class:`SQLiteDatabase` and call
    ``self.db.get_connection()`` to run SQL, exactly as the original
    monolith did. The helper methods here are optional conveniences; the
    concrete repository methods remain responsible for their own SQL.
    """

    def __init__(self, db: SQLiteDatabase) -> None:
        self.db = db

    def _execute(self, sql: str, params: Sequence[Any] = ()) -> None:
        """Run a write/DDL statement inside a managed connection."""
        with self.db.get_connection() as conn:
            conn.execute(sql, params)

    def _fetchone(self, sql: str, params: Sequence[Any] = ()) -> Optional[Any]:
        """Run a SELECT and return the first row (or ``None``)."""
        with self.db.get_connection() as conn:
            return conn.execute(sql, params).fetchone()

    def _fetchall(self, sql: str, params: Sequence[Any] = ()) -> list:
        """Run a SELECT and return all rows."""
        with self.db.get_connection() as conn:
            return conn.execute(sql, params).fetchall()


__all__ = ["SQLiteRepositoryBase"]

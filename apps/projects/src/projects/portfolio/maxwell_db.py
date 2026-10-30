"""The portal database through role maxwell_projects: read, add a project, set dossier_id (migration 20261029231000)."""

from __future__ import annotations

import re
import secrets
import threading
import unicodedata
from typing import Any

TABLES = {"whiteboard": "whiteboard_docs", "canvas": "portal_canvases", "tasks": "portal_boards",
          "research": "portal_research_workspaces"}
PROJECTS = (
    "SELECT p.slug, p.title, p.created_at::text AS updated_at, d.status AS dossier "
    "FROM portal_projects p LEFT JOIN kernel_dossiers d ON d.slug = p.slug"
)
ITEMS = (
    "SELECT 'whiteboard' AS kind, id::text, title, status, dossier_id, updated_at::text, 0 AS steps, 0 AS done "
    "FROM whiteboard_docs "
    "UNION ALL SELECT 'canvas', id::text, name, 'active', dossier_id, updated_at::text, 0, 0 FROM portal_canvases "
    "UNION ALL SELECT 'tasks', b.id::text, b.title, 'active', b.dossier_id, b.updated_at::text, count(c.id), "
    "count(c.id) FILTER (WHERE c.col = 'done') FROM portal_boards b LEFT JOIN portal_cards c ON c.board_id = b.id "
    "WHERE b.kind = 'kanban' GROUP BY b.id "
    "UNION ALL SELECT 'research', id::text, name, 'active', dossier_id, created_at::text, 0, 0 "
    "FROM portal_research_workspaces"
)


def slug_for(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower())
    return f"{base.strip('-')[:60] or 'project'}-{secrets.token_hex(3)}"


class MaxwellDb:
    """One connection, opened on first use and again after a failure."""

    def __init__(self, dsn: str):
        self.dsn, self._lock, self._connection = dsn, threading.Lock(), None

    def _run(self, work):
        import psycopg
        from psycopg.rows import dict_row

        with self._lock:
            for attempt in (1, 2):
                if self._connection is None or self._connection.closed:
                    self._connection = psycopg.connect(self.dsn, row_factory=dict_row, autocommit=True, connect_timeout=5)
                try:
                    return work(self._connection)
                except psycopg.OperationalError:
                    self._connection = None
                    if attempt == 2:
                        raise

    def read(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        def work(c):
            with c.pipeline():
                projects, items = c.execute(PROJECTS), c.cursor().execute(ITEMS)
            return projects.fetchall(), items.fetchall()
        return self._run(work)

    def file(self, refs: list[str], slug: str | None) -> int:
        """Puts each item in the project (None: in no project); unknown kinds are refused."""
        def work(c):
            moved = 0
            with c.transaction():
                for ref in refs:
                    kind, _, row_id = ref.partition(":")
                    table = TABLES.get(kind)
                    if table is None:
                        raise ValueError(ref)
                    moved += c.execute(f"UPDATE {table} SET dossier_id = %s WHERE id::text = %s", (slug, row_id)).rowcount
            return moved
        return self._run(work)

    def create(self, title: str, by: str) -> str:
        slug = slug_for(title)
        self._run(lambda c: c.execute(
            "INSERT INTO portal_projects (slug, title, created_by) VALUES (%s, %s, %s)", (slug, title, by)))
        return slug

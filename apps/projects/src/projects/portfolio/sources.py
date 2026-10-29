"""The existing Maxwell project work, read once from the portal database (read-only)."""

from __future__ import annotations

from typing import Any

# A non-draft dossier is a project; whiteboard_docs.dossier_id already names a board's project.
QUERIES = {
    "dossier": "SELECT slug AS id, title, status, updated_at FROM kernel_dossiers WHERE status <> 'draft'",
    "whiteboard": "SELECT id::text, title, status, dossier_id AS project, updated_at FROM whiteboard_docs",
    "canvas": "SELECT id::text, name AS title, updated_at FROM portal_canvases",
    "tasks": (
        "SELECT b.id::text, b.title, b.updated_at, count(c.id) AS steps, "
        "count(c.id) FILTER (WHERE c.col = 'done') AS step "
        "FROM portal_boards b LEFT JOIN portal_cards c ON c.board_id = b.id "
        "WHERE b.kind = 'kanban' GROUP BY b.id"
    ),
    "research": "SELECT id::text, name AS title, created_at AS updated_at FROM portal_research_workspaces",
}


def item(source: str, row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ref": f"{source}:{row['id']}",
        "kind": source,
        "title": (row.get("title") or "").strip() or "untitled",
        "status": row.get("status") or "active",
        "project": f"dossier:{row['project']}" if row.get("project") else None,
        "steps": int(row.get("steps") or 0),
        "step": int(row.get("step") or 0),
        "updated_at": str(row.get("updated_at") or ""),
    }


def read(dsn: str) -> list[dict[str, Any]]:
    """Every source row as an item, in one read-only transaction."""
    import psycopg
    from psycopg.rows import dict_row

    rows: list[dict[str, Any]] = []
    # node-postgres spells libpq's sslmode=require as no-verify; the worker's DSN uses it.
    dsn = dsn.replace("sslmode=no-verify", "sslmode=require")
    with psycopg.connect(dsn, row_factory=dict_row, connect_timeout=5) as connection:
        connection.read_only = True
        for source, query in QUERIES.items():
            rows.extend(item(source, row) for row in connection.execute(query))
    return rows

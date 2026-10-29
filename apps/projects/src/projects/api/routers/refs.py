"""HTTP routes: what a ``#projects_note:<id>`` names, for the person asking (PlantCraft
``docs/app-standard.md``, 4b, ``[[contributes.refs]]``): its title, state and page."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from projects.api.deps import CurrentUser, RuntimeDep, note_or_404

router = APIRouter()
KIND = "projects_note"


@router.get(f"/api/refs/{KIND}/{{note_id}}")
def note_ref(note_id: str, rt: RuntimeDep, _user: CurrentUser) -> dict[str, Any]:
    note = note_or_404(rt, note_id)
    return {
        "title": note["text"][:80],
        "status": "follow-up" if note.get("follow_up") else None,
        "url": f"/projects/notes/{note['note_id']}",
    }

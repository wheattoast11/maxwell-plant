"""HTTP routes: every project with what belongs to it; moves go through the suite's folders routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from plantcraft_sdk.server.folders import folders_router

from projects.api.deps import CurrentUser, EditorUser, RuntimeDep
from projects.portfolio.service import KIND

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
folders = folders_router(
    (KIND,), editor=EditorUser, exists=lambda rt, _kind, ref: rt.portfolio.movable(ref),
    store=lambda rt: rt.portfolio.folders,
)


@router.get("")
def portfolio(rt: RuntimeDep, _user: CurrentUser) -> dict[str, Any]:
    return rt.portfolio.view()

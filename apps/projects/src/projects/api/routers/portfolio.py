"""HTTP routes: every project with its work, filing items into a project, and starting one."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from projects.api.deps import CurrentUser, EditorUser, RuntimeDep
from projects.i18n import t

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
Refs = list[str]


class FileBody(BaseModel):
    refs: Refs = Field(min_length=1, max_length=50)
    project: str | None = Field(default=None, max_length=90)


class NewProject(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    refs: Refs = Field(default_factory=list, max_length=50)


@router.get("")
def portfolio(rt: RuntimeDep, _user: CurrentUser) -> dict[str, Any]:
    return rt.portfolio.view()


@router.post("/file")
def file(body: FileBody, rt: RuntimeDep, user: EditorUser) -> dict[str, Any]:
    try:
        out = rt.portfolio.file(body.refs, body.project)
    except (KeyError, ValueError) as exc:
        raise HTTPException(422, t("No such project or item.")) from exc
    rt.audit(user, "portfolio.filed", body.project or "none", {"items": len(body.refs)})
    return out


@router.post("/projects", status_code=201)
def create(body: NewProject, rt: RuntimeDep, user: EditorUser) -> dict[str, Any]:
    try:
        out = rt.portfolio.create(body.title.strip(), body.refs, user.username)
    except ValueError as exc:
        raise HTTPException(422, t("No such item.")) from exc
    rt.audit(user, "portfolio.created", out["created"], {"items": len(body.refs)})
    return out

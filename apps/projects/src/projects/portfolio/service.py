"""One list of projects: portal_projects, and every whiteboard, process box, task list and research workspace by dossier_id."""

from __future__ import annotations

import re
import threading
import time
import unicodedata
from typing import Any, Protocol

CACHE_SECONDS = 30.0


class Source(Protocol):
    def read(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]: ...
    def file(self, refs: list[str], slug: str | None) -> int: ...
    def create(self, title: str, by: str) -> str: ...


def words(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", title).lower()) if len(w) > 2}


def view(projects: list[dict[str, Any]], items: list[dict[str, Any]]) -> dict[str, Any]:
    out = {p["slug"]: {"id": p["slug"], "title": p["title"], "updated_at": p["updated_at"],
                       "dossier": p["dossier"], "items": [], "archived": 0} for p in projects}
    titles = {slug: words(p["title"]) for slug, p in out.items()}
    loose: dict[str, dict[str, Any]] = {}
    hidden = 0
    for row in items:
        i = {"ref": f"{row['kind']}:{row['id']}", "kind": row["kind"], "title": (row["title"] or "").strip() or "untitled",
             "status": row["status"], "steps": int(row["steps"]), "step": int(row["done"]), "updated_at": row["updated_at"] or ""}
        home = out.get(row["dossier_id"] or "")
        if i["status"] == "archived":
            if home:
                home["archived"] += 1
            else:
                hidden += 1
        elif home:
            home["items"].append(i)
            home["updated_at"] = max(home["updated_at"], i["updated_at"])
        else:
            group = loose.setdefault(i["title"], {**i, "refs": []})
            group["refs"].append(i["ref"])
            group["updated_at"] = max(group["updated_at"], i["updated_at"])
    for group in loose.values():
        w = words(group["title"])
        group["suggest"] = next((slug for slug, t in titles.items() if t & w), None)
    for p in out.values():
        p["steps"], p["done"] = sum(i["steps"] for i in p["items"]), sum(i["step"] for i in p["items"])
    newest = lambda x: x["updated_at"]  # noqa: E731
    return {"projects": sorted(out.values(), key=newest, reverse=True),
            "loose": sorted(loose.values(), key=newest, reverse=True), "hidden": hidden}


class Portfolio:
    def __init__(self, source: Source | None):
        self.source = source
        self._lock = threading.Lock()
        self._cache: tuple[float, dict[str, Any] | None] = (0.0, None)

    def view(self) -> dict[str, Any]:
        if self.source is None:
            return {"projects": [], "loose": [], "hidden": 0, "connected": False}
        with self._lock:
            at, cached = self._cache
            if cached is None or time.monotonic() - at > CACHE_SECONDS:
                cached = {**view(*self.source.read()), "connected": True}
                self._cache = (time.monotonic(), cached)
        return cached

    def _changed(self) -> dict[str, Any]:
        self._cache = (0.0, None)
        return self.view()

    def file(self, refs: list[str], slug: str | None) -> dict[str, Any]:
        known = {p["id"] for p in self.view()["projects"]}
        if slug is not None and slug not in known:
            raise KeyError(slug)
        self.source.file(refs, slug)
        return self._changed()

    def create(self, title: str, refs: list[str], by: str) -> dict[str, Any]:
        slug = self.source.create(title, by)
        if refs:
            self.source.file(refs, slug)
        return {**self._changed(), "created": slug}

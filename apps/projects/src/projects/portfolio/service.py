"""One list of projects out of the five places Maxwell project work lives today."""

from __future__ import annotations

import re
import threading
import time
import unicodedata
from collections.abc import Callable
from typing import Any

from plantcraft_sdk.server.folders import FolderStore

KIND = "item"
CACHE_SECONDS = 30.0


def words(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKC", title).lower()) if len(w) > 2}


def view(items: list[dict[str, Any]], folders: list[dict[str, Any]], placed: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Every project is a folder; a dossier's folder carries its title, so linked boards land in it."""
    dossiers = {i["ref"]: i["title"] for i in items if i["kind"] == "dossier"}
    by_name = {f["name"]: f["folder_id"] for f in folders}
    projects = {f["folder_id"]: {"id": f["folder_id"], "title": f["name"], "updated_at": f["created_at"],
                                 "origin": "maxwell" if f["name"] in dossiers.values() else "here",
                                 "items": [], "archived": 0} for f in folders}
    titles = {pid: words(p["title"]) for pid, p in projects.items()}
    loose: dict[str, dict[str, Any]] = {}
    hidden = 0
    for i in items:
        if i["kind"] == "dossier":
            continue
        home = (placed.get(i["ref"]) or {}).get("folder_id") or by_name.get(dossiers.get(i["project"] or "", ""))
        archived = i["status"] == "archived"
        if home in projects:
            p = projects[home]
            if archived:
                p["archived"] += 1
            else:
                p["items"].append({**i, "linked": not placed.get(i["ref"])})
                p["updated_at"] = max(p["updated_at"], i["updated_at"])
        elif archived:
            hidden += 1
        else:
            group = loose.setdefault(i["title"], {**i, "refs": [], "suggest": None})
            group["refs"].append(i["ref"])
            group["updated_at"] = max(group["updated_at"], i["updated_at"])
    for group in loose.values():
        w = words(group["title"])
        group["suggest"] = next((pid for pid, t in titles.items() if t & w), None)
    for p in projects.values():
        p["steps"] = sum(i["steps"] for i in p["items"])
        p["done"] = sum(i["step"] for i in p["items"])
    newest = lambda x: x["updated_at"]  # noqa: E731
    return {"projects": sorted(projects.values(), key=newest, reverse=True),
            "loose": sorted(loose.values(), key=newest, reverse=True), "hidden": hidden}


class Portfolio:
    def __init__(self, folders: FolderStore, reader: Callable[[], list[dict[str, Any]]] | None):
        self.folders, self.reader = folders, reader
        self._lock = threading.Lock()
        self._cache: tuple[float, list[dict[str, Any]]] = (0.0, [])

    def items(self) -> list[dict[str, Any]]:
        if self.reader is None:
            return []
        with self._lock:
            at, rows = self._cache
            if time.monotonic() - at > CACHE_SECONDS:
                rows = self.reader()
                self._seed(rows)
                self._cache = (time.monotonic(), rows)
        return rows

    def _seed(self, rows: list[dict[str, Any]]) -> None:
        """Each Maxwell dossier gets its project folder once."""
        names = {f["name"] for f in self.folders.list(KIND)}
        for row in rows:
            if row["kind"] == "dossier" and row["title"] not in names:
                self.folders.create(KIND, row["title"], by="maxwell")

    def movable(self, ref: str) -> bool:
        return any(i["ref"] == ref and i["kind"] != "dossier" for i in self.items())

    def view(self) -> dict[str, Any]:
        rows = self.items()
        return {**view(rows, self.folders.list(KIND), self.folders.items(KIND)), "connected": self.reader is not None}

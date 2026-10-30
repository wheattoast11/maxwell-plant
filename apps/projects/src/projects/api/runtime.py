"""Everything one Projects server holds: settings, the notes and the PlantCraft clients.

Who reads plant data: the pages read with the person's own token, so PlantCraft's permissions
decide what each person sees. The app key (``PLANTCRAFT_APP_KEY``) is for what the app does on
its own, in the background; this app has no background work, so it only reports whether it has
one.
"""

from __future__ import annotations

from typing import Any

import httpx
from plantcraft_sdk.auth import TokenVerifier
from plantcraft_sdk.client import PlantCraftClient
from plantcraft_sdk.server.platform import PlatformRuntime
from plantcraft_sdk.server.store import Database

from projects import APP_ID, __version__
from projects.config import Settings
from projects.notes.service import NoteService
from projects.notes.store import NoteStore
from projects.portfolio.maxwell_db import MaxwellDb
from projects.portfolio.service import Portfolio
from projects.suite import Suite


class Runtime(PlatformRuntime):
    def __init__(
        self,
        settings: Settings,
        *,
        verifier: TokenVerifier | None = None,
        service_client: PlantCraftClient | None = None,
        http_client: httpx.Client | None = None,
    ):
        self.settings = settings
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        self.db = Database(settings.database_path, version=__version__)
        # What the app sends to PlantCraft on its own goes through suite/ only.
        self.suite = Suite(lambda: self.service_client)
        self.notes = NoteService(NoteStore(self.db), self.suite)
        self.portfolio = Portfolio(MaxwellDb(settings.maxwell_dsn) if settings.maxwell_dsn else None)
        self.connect(
            APP_ID,
            settings,
            verifier=verifier,
            service_client=service_client,
            http_client=http_client,
        )

    def start(self) -> None:
        """Background work starts here (none in this app)."""

    def shutdown(self) -> None:
        self.close_platform()

    def status(self) -> dict[str, Any]:
        return {"service_key": self.has_service_key, "notes": len(self.notes.list())}

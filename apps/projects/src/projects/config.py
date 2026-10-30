"""Settings, all from the environment, each with a safe default.

Secrets (the app key) are never logged or stored by Projects.

| Variable | Default | Meaning |
|---|---|---|
| ``PLANTCRAFT_URL`` | ``http://127.0.0.1:8060`` | PlantCraft API v1, as this server reaches it |
| ``PLANTCRAFT_PUBLIC_URL`` | empty (same origin) | PlantCraft as the browser reaches it (sign-in page) |
| ``PLANTCRAFT_APP_KEY`` | empty | App key: what the app reads and publishes on its own |
| ``PLANTCRAFT_APP_KEY_FILE`` | empty | File holding the app key (a Docker secret) |
| ``PROJECTS_DATA_DIR`` | ``var`` | Folder of the SQLite database |
| ``PROJECTS_ROOT_PATH`` | ``/projects`` | Path prefix of the interface and API |
| ``PROJECTS_MAXWELL_DSN_FILE`` | empty | File holding the DSN of role maxwell_projects on the Maxwell portal database (empty: no portfolio) |
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from plantcraft_sdk.server.settings import AppSettings, env_text

from projects import APP_ID


@dataclass
class Settings(AppSettings):
    APP_ID = APP_ID

    root_path: str = "/projects"
    maxwell_dsn: str = ""

    @classmethod
    def from_environment(cls) -> Settings:
        return cls(**cls.common(APP_ID, "/projects"), maxwell_dsn=_secret_file("PROJECTS_MAXWELL_DSN_FILE"))


def _secret_file(name: str) -> str:
    """A secret kept in the file the variable names; empty when unset or unreadable."""
    path = env_text(name)
    try:
        return Path(path).expanduser().read_text(encoding="utf-8").strip() if path else ""
    except OSError:
        return ""

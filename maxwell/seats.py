"""The three seats of the Maxwell workspace: Tej, Nick and Raul.

Running it again changes nothing: a seat keeps its password once one is written.
"""

from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path

from processcraft.api.runtime import PROJECT_ROOT
from processcraft.auth.tokens import _write_private
from processcraft.config import load_scenario
from processcraft.platform.workspace import Workspace

SCENARIO = PROJECT_ROOT / "scenarios" / "maxwell.json"
PROFILE = {"affiliation": "internal", "organization": "Intuition Labs"}

# sub is the auth.users.id of teammaxwell-<username>@terminals.tech on Supabase terminals-tech.
SEATS = (
    {"username": "tej", "display_name": "Tej Desai", "role": "Piezoelectrics", "level": "admin",
     "job_title": "Founder · piezoelectrics", "sub": "23006b19-4317-487b-a969-9bdab0edcd15"},
    {"username": "nick", "display_name": "Nick Reding", "role": "Engineering", "level": "editor",
     "job_title": "", "sub": "7523c6de-60e1-4e59-8868-cc593eee27d8"},
    {"username": "raul", "display_name": "Raul Flores", "role": "Discovery", "level": "editor",
     "job_title": "", "sub": "3609e836-ba9b-4459-b37a-6bf7a0f9476e"},
)


def email(username: str) -> str:
    return f"teammaxwell-{username}@terminals.tech"


def db_path(scenario: Path = SCENARIO) -> Path:
    return Path(load_scenario(scenario, project_root=PROJECT_ROOT).storage.sqlite_path)


def directory_secrets_file(database: Path) -> Path:
    """Where the server reads the sign-in secret (processcraft/api/runtime.py, same rule)."""
    configured = os.environ.get("PLANTCRAFT_DIRECTORY_SECRETS_FILE", "").strip()
    return Path(configured) if configured else database.with_name("directory-secrets.json")


def ensure_seats(workspace: Workspace, secrets_dir: Path) -> list[dict[str, str]]:
    secrets_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    users, report = workspace.users, []
    for seat in SEATS:
        name = seat["username"]
        users.upsert_user(name, seat["display_name"], seat["role"])
        users.set_profile(name, {**PROFILE, "job_title": seat["job_title"], "email": email(name)})
        users.set_access(name, seat["level"])
        secret = secrets_dir / f"{name}.password"
        password = secrets.token_urlsafe(18)
        created = _write_private(secret, (password + "\n").encode(), exclusive=True)
        if created:
            users.set_password(name, password)
        report.append({"username": name, "level": seat["level"],
                       "password": "written" if created else "kept", "file": str(secret)})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=SCENARIO)
    args = parser.parse_args(argv)
    database = db_path(args.scenario)
    database.parent.mkdir(parents=True, exist_ok=True)
    for row in ensure_seats(Workspace(database), database.parent / "seats"):
        print(f"{row['username']:<5} {row['level']:<7} password {row['password']:<7} {row['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

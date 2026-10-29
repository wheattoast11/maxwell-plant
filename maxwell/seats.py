"""The three seats of the Maxwell workspace: Tej, Nick and Raul.

Running it again changes nothing: a seat keeps its password once one is written.
"""

from __future__ import annotations

import argparse
import os
import secrets
from pathlib import Path

from processcraft.config import load_scenario
from processcraft.platform.workspace import Workspace

ROOT = Path(__file__).resolve().parent.parent
SCENARIO = ROOT / "scenarios" / "maxwell.json"

SEATS = (
    {
        "username": "tej",
        "display_name": "Tej Desai",
        "role": "Piezoelectrics",
        "level": "admin",
        "profile": {
            "job_title": "Founder · piezoelectrics",
            "affiliation": "internal",
            "organization": "Intuition Labs",
            "email": "teammaxwell-tej@terminals.tech",
        },
    },
    {
        "username": "nick",
        "display_name": "Nick Reding",
        "role": "Engineering",
        "level": "editor",
        "profile": {
            "affiliation": "internal",
            "organization": "Intuition Labs",
            "email": "teammaxwell-nick@terminals.tech",
        },
    },
    {
        "username": "raul",
        "display_name": "Raul Flores",
        "role": "Discovery",
        "level": "editor",
        "profile": {
            "affiliation": "internal",
            "organization": "Intuition Labs",
            "email": "teammaxwell-raul@terminals.tech",
        },
    },
)


def ensure_seats(workspace: Workspace, secrets_dir: Path) -> list[dict[str, str]]:
    secrets_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    report = []
    for seat in SEATS:
        users = workspace.users
        users.upsert_user(seat["username"], seat["display_name"], seat["role"])
        users.set_profile(seat["username"], seat["profile"])
        if users.get_user(seat["username"]).get("access_level") != seat["level"]:
            users.set_access(seat["username"], seat["level"])
        secret = secrets_dir / f"{seat['username']}.password"
        created = not secret.exists()
        if created:
            password = secrets.token_urlsafe(18)
            fd = os.open(secret, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w") as handle:
                handle.write(password + "\n")
            users.set_password(seat["username"], password)
        report.append({"username": seat["username"], "level": seat["level"],
                       "password": "written" if created else "kept", "file": str(secret)})
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=SCENARIO)
    args = parser.parse_args(argv)
    scenario = load_scenario(args.scenario, project_root=ROOT)
    db_path = Path(scenario.storage.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    for row in ensure_seats(Workspace(db_path), db_path.parent / "seats"):
        print(f"{row['username']:<5} {row['level']:<7} password {row['password']:<7} {row['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Sign in to the Maxwell workspace with the terminals-tech Supabase account (maxwell/oidc.md)."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from maxwell.seats import SCENARIO, SEATS, db_path, directory_secrets_file
from processcraft.directory.settings import (
    DirectorySecrets,
    DirectorySettingsStore,
    check_settings,
)
from processcraft.platform.workspace import Workspace

ISSUER = "https://zkdfziipgtswwlkpkyvv.supabase.co/auth/v1"


def directory_payload(client_id: str, public_url: str, issuer: str = ISSUER) -> dict[str, Any]:
    return {
        "oidc": {
            "enabled": True,
            "label": "terminals.tech",
            "issuer": issuer,
            "client_id": client_id,
            "scopes": "openid email profile",
            "username_claim": "email",
            "groups_claim": "sub",
            "display_name_claim": "name",
            "email_claim": "email",
            "public_url": public_url,
        },
        "rules": [
            {"match": seat["sub"], "level": seat["level"]} for seat in SEATS
        ],
        "unmatched": "deny",
        "local_passwords": True,
    }


def apply(
    workspace: Workspace,
    secrets_file: Path,
    *,
    client_id: str,
    client_secret: str,
    public_url: str,
    issuer: str = ISSUER,
) -> list[dict[str, str]]:
    """Saves the settings and secret, and binds each seat to its Supabase id (drops its password)."""

    settings = check_settings(directory_payload(client_id, public_url, issuer))
    DirectorySettingsStore(workspace.db).save(settings, "maxwell.oidc")
    DirectorySecrets(secrets_file).set("oidc_client_secret", client_secret)
    rows = []
    for seat in SEATS:
        username = seat["username"]
        try:
            workspace.users.set_identity(username, "oidc", seat["sub"])
        except ValueError:
            raise SystemExit(f"seat {username} missing: run python -m maxwell.seats first") from None
        rows.append({"username": username, "sub": seat["sub"], "level": seat["level"]})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=SCENARIO)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret-file", type=Path, required=True)
    parser.add_argument("--public-url", required=True)
    args = parser.parse_args(argv)
    database = db_path(args.scenario)
    rows = apply(
        Workspace(database),
        directory_secrets_file(database),
        client_id=args.client_id,
        client_secret=args.client_secret_file.read_text().strip(),
        public_url=args.public_url,
    )
    for row in rows:
        print(f"{row['username']:<5} {row['level']:<7} oidc {row['sub']}")
    print(f"redirect_uri {args.public_url.rstrip('/')}/api/sso/oidc/callback")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

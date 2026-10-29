"""The three seats sign in through a stub shaped like the live Supabase issuer (maxwell/oidc.md)."""

from __future__ import annotations

import json
import secrets
import time
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from fastapi.testclient import TestClient

from maxwell.oidc import ISSUER, apply, directory_payload
from maxwell.seats import SEATS, email, ensure_seats
from processcraft.api.app import create_app
from processcraft.api.runtime import PROJECT_ROOT as ROOT
from processcraft.directory import oidc
from tests.directory_fakes import b64

CLIENT_ID = "9d1c6f0e-0000-4000-8000-00000000c11e"
CLIENT_SECRET = "stub-client-secret"
ADMIN_PASSWORD = "tej-installation-password"


class _Reply:
    def __init__(self, status: int, body: Any):
        self.status_code = status
        self._body = body

    def json(self) -> Any:
        return self._body


class SupabaseStub:
    """Discovery and keys copied in shape from the live issuer; ES256 ID tokens."""

    def __init__(self) -> None:
        self.key = ec.generate_private_key(ec.SECP256R1())
        self.kid = "48e4587f-b2d5-4a0a-bee5-14f5f4589fc3"
        self.codes: dict[str, dict[str, Any]] = {}

    def sign_in(self, authorization_url: str, user: dict[str, Any]) -> tuple[str, str]:
        parts = urlsplit(authorization_url)
        assert f"{parts.scheme}://{parts.netloc}{parts.path}" == f"{ISSUER}/oauth/authorize"
        query = {k: v[0] for k, v in parse_qs(parts.query).items()}
        assert query["client_id"] == CLIENT_ID and query["code_challenge_method"] == "S256"
        assert query["scope"] == "openid email profile"
        code = secrets.token_urlsafe(16)
        self.codes[code] = {"user": user, **query}
        return code, query["state"]

    def get(self, url: str, **_: Any) -> _Reply:
        if url == f"{ISSUER}/.well-known/openid-configuration":
            return _Reply(200, {
                "issuer": ISSUER,
                "authorization_endpoint": f"{ISSUER}/oauth/authorize",
                "token_endpoint": f"{ISSUER}/oauth/token",
                "jwks_uri": f"{ISSUER}/.well-known/jwks.json",
                "userinfo_endpoint": f"{ISSUER}/oauth/userinfo",
                "id_token_signing_alg_values_supported": ["RS256", "HS256", "ES256"],
                "token_endpoint_auth_methods_supported": ["client_secret_basic", "client_secret_post", "none"],
                "code_challenge_methods_supported": ["S256", "plain"],
            })  # fmt: skip
        if url == f"{ISSUER}/.well-known/jwks.json":
            n = self.key.public_key().public_numbers()
            return _Reply(200, {"keys": [{
                "alg": "ES256", "crv": "P-256", "kid": self.kid, "kty": "EC", "use": "sig",
                "key_ops": ["verify"], "x": b64(n.x.to_bytes(32, "big")), "y": b64(n.y.to_bytes(32, "big")),
            }]})  # fmt: skip
        if url == f"{ISSUER}/oauth/userinfo":
            return _Reply(401, {})
        return _Reply(404, {})

    def post(self, url: str, data: dict[str, Any], auth: Any = None, **_: Any) -> _Reply:
        grant = self.codes.pop(data.get("code"), None)
        if url != f"{ISSUER}/oauth/token" or grant is None or auth != (CLIENT_ID, CLIENT_SECRET):
            return _Reply(400, {"error": "invalid_grant"})
        digest = hashes.Hash(hashes.SHA256())
        digest.update(data["code_verifier"].encode("ascii"))
        if b64(digest.finalize()) != grant["code_challenge"] or data["redirect_uri"] != grant["redirect_uri"]:
            return _Reply(400, {"error": "invalid_grant"})
        now = int(time.time())
        claims = {"iss": ISSUER, "aud": CLIENT_ID, "iat": now, "exp": now + 3600, "auth_time": now,
                  "nonce": grant["nonce"], "email_verified": True, **grant["user"]}  # fmt: skip
        return _Reply(200, {"access_token": "a", "token_type": "bearer", "id_token": self.id_token(claims)})

    def id_token(self, claims: dict[str, Any]) -> str:
        head = b64(json.dumps({"alg": "ES256", "kid": self.kid, "typ": "JWT"}).encode())
        body = b64(json.dumps(claims).encode())
        r, s = decode_dss_signature(self.key.sign(f"{head}.{body}".encode(), ec.ECDSA(hashes.SHA256())))
        return f"{head}.{body}.{b64(r.to_bytes(32, 'big') + s.to_bytes(32, 'big'))}"


@pytest.fixture()
def app(tmp_path, monkeypatch):
    oidc._cache.clear()
    scenario = json.loads((ROOT / "scenarios" / "maxwell.json").read_text())
    scenario["storage"]["sqlite_path"] = str(tmp_path / "workspace.sqlite3")
    scenario["source"]["path"] = str(ROOT / scenario["source"]["path"])
    (tmp_path / "scenario.json").write_text(json.dumps(scenario))
    (tmp_path / "admin").write_text(ADMIN_PASSWORD)
    for name, value in {
        "PLANTCRAFT_SCENARIO": str(tmp_path / "scenario.json"),
        "PLANTCRAFT_PREWARM_HISTORY": "false",
        "PLANTCRAFT_DEMO_USERS": "0",
        "PLANTCRAFT_BASIC_AUTH_ENABLED": "1",
        "PLANTCRAFT_BASIC_AUTH_USERNAME": "tej",
        "PLANTCRAFT_BASIC_AUTH_PASSWORD_FILE": str(tmp_path / "admin"),
    }.items():
        monkeypatch.setenv(name, value)
    application = create_app()
    rt = application.state.runtime
    ensure_seats(rt.workspace, tmp_path / "seats")
    application.state.stub = rt.directory.oidc_http = SupabaseStub()
    yield application
    oidc._cache.clear()


def _bind(app, tmp_path) -> None:
    apply(app.state.runtime.workspace, tmp_path / "directory-secrets.json", client_id=CLIENT_ID,
          client_secret=CLIENT_SECRET, public_url="http://testserver")  # fmt: skip


def _sso(app, user: dict[str, Any]):
    client = TestClient(app)
    start = client.get("/api/sso/oidc/start", follow_redirects=False)
    assert start.status_code == 303
    if start.headers["location"].startswith("/login"):
        return client, start
    code, state = app.state.stub.sign_in(start.headers["location"], user)
    return client, client.get(f"/api/sso/oidc/callback?code={code}&state={state}", follow_redirects=False)


def _seat(name: str) -> dict[str, Any]:
    return {"sub": next(s["sub"] for s in SEATS if s["username"] == name), "email": email(name)}


def test_the_payload_passes_the_forks_own_settings_check():
    from processcraft.directory.settings import check_settings

    settings = check_settings(directory_payload(CLIENT_ID, "http://127.0.0.1:8765"))
    assert settings.oidc.ready and settings.oidc.issuer == ISSUER and settings.unmatched == "deny"
    assert settings.oidc.redirect_uri == "http://127.0.0.1:8765/api/sso/oidc/callback"


def test_sso_is_closed_until_applied(app):
    _, reply = _sso(app, _seat("nick"))
    assert reply.headers["location"] == "/login?sso=failed"


@pytest.mark.parametrize(("name", "level"), [("tej", "admin"), ("nick", "editor"), ("raul", "editor")])
def test_each_seat_signs_in_as_itself(app, tmp_path, name, level):
    _bind(app, tmp_path)
    client, reply = _sso(app, _seat(name))
    assert reply.status_code == 303 and reply.headers["location"] == "/", reply.headers
    assert client.get("/api/session").json()["username"] == name
    user = app.state.runtime.workspace.users.get_user(name)
    assert user["auth_source"] == "oidc" and user["access_level"] == level
    assert user["profile"]["email"] == email(name)
    assert app.state.runtime.workspace.users.get_user(f"teammaxwell-{name}") is None


def test_another_supabase_user_is_refused(app, tmp_path):
    _bind(app, tmp_path)
    _, reply = _sso(app, {"sub": "11111111-2222-4333-8444-555555555555", "email": "someone@terminals.tech"})
    assert reply.headers["location"] == "/login?sso=failed"
    assert app.state.runtime.workspace.users.get_user("someone") is None


def test_a_token_from_another_key_is_refused(app, tmp_path):
    _bind(app, tmp_path)
    app.state.stub.key = ec.generate_private_key(ec.SECP256R1())
    oidc._cache.clear()
    real = app.state.stub.get
    app.state.stub.get = lambda url, **kw: (
        _Reply(200, {"keys": []}) if url.endswith("jwks.json") else real(url, **kw)
    )
    _, reply = _sso(app, _seat("nick"))
    assert reply.headers["location"] == "/login?sso=failed"


def test_the_installation_password_still_opens_tej(app, tmp_path):
    _bind(app, tmp_path)
    reply = TestClient(app).post("/api/login", json={"username": "tej", "password": ADMIN_PASSWORD})
    assert reply.status_code == 200 and reply.json()["username"] == "tej"

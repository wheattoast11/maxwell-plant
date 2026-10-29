from processcraft.platform.workspace import Workspace

from maxwell.seats import SEATS, ensure_seats


def test_seats_sign_in_and_a_second_run_keeps_passwords(tmp_path, monkeypatch):
    monkeypatch.setenv("PLANTCRAFT_DEMO_USERS", "0")
    workspace = Workspace(tmp_path / "workspace.sqlite3")
    first = ensure_seats(workspace, tmp_path / "seats")
    passwords = {s["username"]: (tmp_path / "seats" / f"{s['username']}.password").read_text().strip() for s in SEATS}
    second = ensure_seats(workspace, tmp_path / "seats")

    assert [r["password"] for r in first] == ["written"] * 3
    assert [r["password"] for r in second] == ["kept"] * 3
    for seat in SEATS:
        name = seat["username"]
        assert workspace.users.verify_password(name, passwords[name])
        assert not workspace.users.verify_password(name, passwords[name] + "x")
        assert workspace.users.get_user(name)["access_level"] == seat["level"]
        assert (tmp_path / "seats" / f"{name}.password").stat().st_mode & 0o777 == 0o600

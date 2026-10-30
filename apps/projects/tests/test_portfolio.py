from projects.portfolio.maxwell_db import TABLES, slug_for
from projects.portfolio.service import Portfolio
from tests.conftest import client_for

IRO2 = "IrO₂ crystal structure prediction"


def row(kind, id, title, project=None, status="active", steps=0, done=0):
    return {"kind": kind, "id": id, "title": title, "status": status, "dossier_id": project,
            "updated_at": f"2026-10-{10 + len(id)}", "steps": steps, "done": done}


class FakeDb:
    """The three calls MaxwellDb makes, over in-memory rows."""

    def __init__(self):
        self.projects = [{"slug": "iro2", "title": IRO2, "updated_at": "2026-07-16", "dossier": "active"}]
        self.items = [
            row("whiteboard", "w1", "IrO2 digest probe", "iro2"),
            row("whiteboard", "w2", "IrO2 old run", "iro2", status="archived"),
            row("whiteboard", "w3", "design exploration"),
            row("whiteboard", "w4", "design exploration"),
            row("whiteboard", "w5", "riff drive", status="archived"),
            row("canvas", "c1", "IrO2 interface bench (rehearsal)"),
            row("canvas", "c2", "suppression cell"),
            row("tasks", "t1", "Tracker", steps=9, done=2),
        ]

    def read(self):
        return self.projects, self.items

    def file(self, refs, slug):
        for ref in refs:
            kind, _, rid = ref.partition(":")
            if kind not in TABLES:
                raise ValueError(ref)
            for r in self.items:
                if (r["kind"], r["id"]) == (kind, rid):
                    r["dossier_id"] = slug
        return len(refs)

    def create(self, title, by):
        slug = slug_for(title)
        self.projects.append({"slug": slug, "title": title, "updated_at": "2026-10-29", "dossier": None})
        return slug


def test_one_list_reads_the_shared_project_key():
    v = Portfolio(FakeDb()).view()
    [iro2] = v["projects"]
    assert (iro2["id"], iro2["dossier"], iro2["archived"]) == ("iro2", "active", 1)
    assert [i["ref"] for i in iro2["items"]] == ["whiteboard:w1"]
    loose = {g["title"]: g for g in v["loose"]}
    assert loose["design exploration"]["refs"] == ["whiteboard:w3", "whiteboard:w4"]
    assert loose["IrO2 interface bench (rehearsal)"]["suggest"] == "iro2"
    assert loose["suppression cell"]["suggest"] is None
    assert v["hidden"] == 1


def test_filing_and_starting_a_project_write_the_key(runtime, fake):
    db = FakeDb()
    runtime.portfolio = Portfolio(db)
    client = client_for(runtime, fake)
    assert client.post("api/portfolio/file", json={"refs": ["canvas:c1"], "project": "iro2"}).status_code == 200
    assert next(r for r in db.items if r["id"] == "c1")["dossier_id"] == "iro2"
    made = client.post("api/portfolio/projects", json={"title": "Mill 2 deflagration", "refs": ["tasks:t1", "canvas:c2"]})
    assert made.status_code == 201
    slug = made.json()["created"]
    assert slug.startswith("mill-2-deflagration-")
    mill = next(p for p in made.json()["projects"] if p["id"] == slug)
    assert {i["ref"] for i in mill["items"]} == {"tasks:t1", "canvas:c2"} and (mill["steps"], mill["done"]) == (9, 2)
    out = client.post("api/portfolio/file", json={"refs": ["whiteboard:w1"], "project": None}).json()
    assert "whiteboard:w1" in {g["ref"] for g in out["loose"]}
    assert client.post("api/portfolio/file", json={"refs": ["canvas:c1"], "project": "nope"}).status_code == 422
    assert client.post("api/portfolio/file", json={"refs": ["dossier:iro2"], "project": "iro2"}).status_code == 422


def test_without_a_dsn_the_portfolio_says_so(runtime, fake):
    body = client_for(runtime, fake).get("api/portfolio").json()
    assert body == {"projects": [], "loose": [], "hidden": 0, "connected": False}


def test_slugs_fit_the_registry_check():
    import re
    for title in (IRO2, "Mill 2 / deflagration!", "—"):
        assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", slug_for(title))

from plantcraft_sdk.server.folders import FolderStore

from projects.portfolio.service import KIND, Portfolio
from projects.portfolio.sources import item
from tests.conftest import client_for

IRO2 = "IrO₂ crystal structure prediction"
ROWS = [
    item("dossier", {"id": "iro2", "title": IRO2, "status": "active"}),
    item("whiteboard", {"id": "w1", "title": "IrO2 digest probe", "status": "active", "project": "iro2"}),
    item("whiteboard", {"id": "w2", "title": "IrO2 old run", "status": "archived", "project": "iro2"}),
    item("whiteboard", {"id": "w3", "title": "design exploration", "status": "active"}),
    item("whiteboard", {"id": "w4", "title": "design exploration", "status": "active"}),
    item("whiteboard", {"id": "w5", "title": "riff drive", "status": "archived"}),
    item("canvas", {"id": "c1", "title": "IrO2 interface bench (rehearsal)"}),
    item("canvas", {"id": "c2", "title": "suppression cell"}),
    item("tasks", {"id": "t1", "title": "Tracker", "steps": 9, "step": 2}),
]


def portfolio(runtime):
    runtime.portfolio = Portfolio(FolderStore(runtime.db, kinds=(KIND,)), lambda: ROWS)
    return runtime.portfolio


def test_one_list_puts_linked_boards_in_their_project_and_groups_repeated_titles(runtime):
    v = portfolio(runtime).view()
    [iro2] = v["projects"]
    assert iro2["title"] == IRO2 and iro2["origin"] == "maxwell" and iro2["archived"] == 1
    assert [i["ref"] for i in iro2["items"]] == ["whiteboard:w1"] and iro2["items"][0]["linked"]
    loose = {g["title"]: g for g in v["loose"]}
    assert loose["design exploration"]["refs"] == ["whiteboard:w3", "whiteboard:w4"]
    assert loose["IrO2 interface bench (rehearsal)"]["suggest"] == iro2["id"]
    assert loose["suppression cell"]["suggest"] is None
    assert v["hidden"] == 1


def test_moves_go_through_the_folders_routes(runtime, fake):
    p = portfolio(runtime)
    client = client_for(runtime, fake)
    iro2 = client.get("api/portfolio").json()["projects"][0]["id"]
    assert client.put("api/folders/item/items/canvas:c1", json={"folder_id": iro2}).status_code == 200
    made = client.post("api/folders/item", json={"name": "Mill 2 deflagration"}).json()
    assert client.put("api/folders/item/items/tasks:t1", json={"folder_id": made["folder_id"]}).status_code == 200
    assert client.put("api/folders/item/items/dossier:iro2", json={"folder_id": made["folder_id"]}).status_code == 404
    v = client.get("api/portfolio").json()
    by_title = {pr["title"]: pr for pr in v["projects"]}
    assert {i["ref"] for i in by_title[IRO2]["items"]} == {"whiteboard:w1", "canvas:c1"}
    assert by_title["Mill 2 deflagration"]["origin"] == "here"
    assert (by_title["Mill 2 deflagration"]["steps"], by_title["Mill 2 deflagration"]["done"]) == (9, 2)
    assert p.folders.list(KIND)[0]["name"] in {IRO2, "Mill 2 deflagration"}


def test_without_a_dsn_the_portfolio_says_so(runtime, fake):
    body = client_for(runtime, fake).get("api/portfolio").json()
    assert body == {"projects": [], "loose": [], "hidden": 0, "connected": False}

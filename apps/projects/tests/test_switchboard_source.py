import hashlib
import json
from pathlib import Path

import pytest

FOLDER = Path(__file__).resolve().parent.parent / "frontend" / "src" / "switchboard"
PINS = json.loads((FOLDER / "SOURCE.json").read_text())["files"]


@pytest.mark.parametrize("name", sorted(PINS))
def test_copied_switchboard_file_matches_its_pin(name):
    assert hashlib.sha256((FOLDER / name).read_bytes()).hexdigest() == PINS[name]

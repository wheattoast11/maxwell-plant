import pytest

from projects.workpiece import Workpiece, address, advance, contains, couple, decode, settle


def test_address_round_trips_and_containment_is_prefix():
    plant, mill = address("plant", (3,)), address("equipment", (3, 7, 12))
    assert decode(mill) == ("equipment", (3, 7, 12))
    assert contains(plant, mill) and not contains(address("plant", (4,)), mill)
    assert mill < 2**64
    with pytest.raises(ValueError):
        address("plant", (0,))


def test_heavier_piece_settles_slower_and_never_overshoots():
    light, heavy = Workpiece("notebook", (1,), target=1.0), Workpiece("board", (1,), target=1.0, signed=8)
    vl = vh = 0.0
    peak = 0.0
    for _ in range(200):
        _, vl = settle(light, 0.05, velocity=vl)
        _, vh = settle(heavy, 0.05, velocity=vh)
        peak = max(peak, light.state, heavy.state)
    assert light.state > heavy.state
    assert peak <= 1.0 + 1e-9


def test_event_lightens_and_link_moves_the_lighter_piece():
    w = Workpiece("equipment", (2,), criticality=3)
    assert w.mass(activity=1.0, lightening=0.5) == pytest.approx(2.0)
    assert w.mass(activity=0.0, lightening=0.5) == pytest.approx(4.0)
    note, pump = Workpiece("notebook", (2, 1)), Workpiece("equipment", (2,), criticality=3)
    dv_note, dv_pump = couple(note, pump, 1.0)
    assert abs(dv_note) > abs(dv_pump)


def test_escapement_ticks_only_on_evidence():
    w = Workpiece("project", (1,), steps=2)
    assert not advance(w, False) and w.step == 0
    assert advance(w, True) and advance(w, True) and not advance(w, True)
    assert w.rest_mass == 3.0 and w.glyph()["advanced"] == 2

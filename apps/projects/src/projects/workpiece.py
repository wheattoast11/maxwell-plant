"""maxwell.workpiece/v1: the one object every workspace item is; the UI reads only its numbers."""

from __future__ import annotations

import math
from dataclasses import dataclass

KINDS = (
    "plant", "project", "board", "equipment", "instrument", "run",
    "desk", "calendar", "notebook", "storage", "util", "person",
)
DIGIT_BITS, DEPTH, KIND_SHIFT = 6, 10, 60


def address(kind: str, path: tuple[int, ...]) -> int:
    """Kind in the top 4 bits, then up to ten base-64 digits (1..63; 0 ends the path)."""
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}")
    if len(path) > DEPTH or any(not 1 <= d <= 63 for d in path):
        raise ValueError("path is up to 10 digits in 1..63")
    value = KINDS.index(kind) << KIND_SHIFT
    for i, digit in enumerate(path):
        value |= digit << (KIND_SHIFT - DIGIT_BITS * (i + 1))
    return value


def decode(addr: int) -> tuple[str, tuple[int, ...]]:
    path = []
    for i in range(DEPTH):
        digit = (addr >> (KIND_SHIFT - DIGIT_BITS * (i + 1))) & 63
        if digit == 0:
            break
        path.append(digit)
    return KINDS[addr >> KIND_SHIFT], tuple(path)


def contains(outer: int, inner: int) -> bool:
    """Containment is a path prefix, whatever the kinds."""
    depth = len(decode(outer)[1])
    mask = ((1 << (DIGIT_BITS * depth)) - 1) << (KIND_SHIFT - DIGIT_BITS * depth)
    return (outer ^ inner) & mask == 0


@dataclass
class Workpiece:
    kind: str
    path: tuple[int, ...]
    state: float = 0.0
    target: float = 0.0
    steps: int = 1
    step: int = 0
    signed: int = 0
    links: int = 0
    criticality: int = 0

    @property
    def addr(self) -> int:
        return address(self.kind, self.path)

    @property
    def rest_mass(self) -> float:
        """m0: one, plus every signature, live link and criticality step that would have to be undone."""
        return 1.0 + self.signed + self.links + self.criticality

    def mass(self, activity: float = 0.0, lightening: float = 1.0) -> float:
        """m*(t) = m0 (1 - (1 - lightening) a): during an event the procedure gets lighter to reach."""
        a = min(max(activity, 0.0), 1.0)
        return self.rest_mass * (1.0 - (1.0 - lightening) * a)

    @property
    def deviation(self) -> float:
        return self.target - self.state

    def glyph(self) -> dict:
        """The gear the UI draws: teeth are procedure steps, rings are depth, spin is deviation over mass."""
        last = self.path[-1] if self.path else 1
        return {
            "kind": self.kind,
            "teeth": max(self.steps, 3),
            "advanced": self.step,
            "rings": len(self.path),
            "phase": (last * 0.6180339887) % 1.0,
            "spin": self.deviation / self.rest_mass,
        }


def settle(
    w: Workpiece, dt: float, stiffness: float = 1.0, velocity: float = 0.0,
    activity: float = 0.0, lightening: float = 1.0,
) -> tuple[float, float]:
    """One step of the procedure spring at critical damping: heavy pieces settle slower, none overshoot."""
    m = w.mass(activity, lightening)
    damping = 2.0 * math.sqrt(stiffness * m)
    velocity += (stiffness * w.deviation - damping * velocity) / m * dt
    w.state += velocity * dt
    return w.state, velocity


def couple(a: Workpiece, b: Workpiece, impulse: float) -> tuple[float, float]:
    """Linking exchanges one impulse through the reduced mass: the lighter piece moves to the heavier."""
    mu = a.rest_mass * b.rest_mass / (a.rest_mass + b.rest_mass)
    return impulse * mu / a.rest_mass, -impulse * mu / b.rest_mass


def advance(w: Workpiece, evidence: bool) -> bool:
    """The escapement: a step ticks only on evidence, and each tick adds a signature."""
    if not evidence or w.step >= w.steps:
        return False
    w.step += 1
    w.signed += 1
    return True

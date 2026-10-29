# Maxwell workspace

One object, `maxwell.workpiece/v1` (`apps/projects/src/projects/workpiece.py`). Calendar, notebook, desk, util, equipment, storage, instrument, run, board, project, plant and person are all workpieces. The screen draws only what the numbers say.

## The object

| field | computes | screen |
|---|---|---|
| `addr` | 64 bits: 4-bit kind + ten base-64 digits | where it sits; containment is a path prefix |
| `steps`, `step` | the procedure it is aligned to, and how far it has advanced | gear teeth; filled teeth are done |
| `target - state` | deviation from the procedure | the gear turns only while deviation is non-zero |
| `m0 = 1 + signed + links + criticality` | what would have to be undone to move it | size, drag inertia, settle time |
| `m*(t) = m0 (1 - (1 - λ) a)` | mass during an event (`a` = event activity) | in an event the procedure is lighter to reach |
| `μ = m1 m2 / (m1 + m2)` | one link exchanges one impulse | the lighter piece moves to the heavier one (`research_worker/src/kernel/world/genesis/coupler.ts:225`) |
| `advance(evidence)` | the escapement: a step ticks only on evidence, and each tick adds a signature | heavier after every signature |

Settling is a critically damped spring at the piece's own mass, so heavy pieces move slowly and nothing overshoots its target.

## Intent decides what is shown

| intent | kinds on the desk |
|---|---|
| Investigate | plant, project, board, equipment, instrument, run, notebook, storage |
| Size | project, board, equipment, util, storage, run |
| Watch | plant, equipment, instrument, desk, calendar |
| Plan | desk, calendar, project, person, notebook |

Everything else docks small at the edge. An intent is a filter over kinds, not a separate screen. The intake form's fields seed the pieces (process: board, lever: constraint, leap: instrument, files: storage, one real run: run).

## Owners

| part | owner |
|---|---|
| the object and its laws | `apps/projects/src/projects/workpiece.py` + `apps/projects/tests/test_workpiece.py` |
| suite shell, Desk, calendar feeds, to-dos | PlantCraft `ui/src`, `processcraft/desk` |
| plant tree, historian, simulator | PlantCraft `processcraft/assets`, `apps/historian`, `simulator` |
| board glyphs, obligations, seal | kit `maxwell-switchboard` |
| springs, gestures, momentum | kit `maxwell-plasma`, `maxwell/web/lib/canvas/gesture.ts` |
| projects and their views | `apps/projects` |
| the moving sketch | https://claude.ai/artifact/43GJeHsZp3X5LmG6JN1uCe |

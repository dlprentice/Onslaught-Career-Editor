# Coast / friction release measurement plan (M1.6)

Status: **scaffold landed** (`tools/battleengine_coast_friction_measurement.py`);
live dual-accept pending.

## Scope

Measure path-speed decay after control release (walker/jet coast). Metric:
**release half-life** (time for speed to fall to ≤50% of hold cruise).

## Harness

| Item | Path |
|------|------|
| Analysis | `tools/battleengine_coast_friction_measurement.py` |
| Tests | `tools/battleengine_coast_friction_measurement_test.py` |
| npm | `npm run test:battleengine-coast-friction-measurement` |

Live protocol can reuse forward/jet pair release phases already collected;
dedicated coast dual-accept may share those release series once envelopes are
stable.

## Non-claims

- Source `mWalkFriction=0.9` is **not** Core authority.
- Scaffold/synthetic half-lives do not authorize Core friction constants.

# Camera look rate measurement plan (M3.1 candidate)

Status: **scaffold landed** (`tools/battleengine_camera_look_measurement.py`);
live dual-accept pending.

## Scope

Measure steady yaw (and optional pitch) look rates under receipt-bound copied
runtime holds, then (later) accept a public contract → translation policy →
Core constants. Free-camera Q-yaw/pitch **patch** proofs elsewhere are control
canaries only; they are **not** rebuild Core authority for player look.

## Harness

| Item | Path |
|------|------|
| Analysis | `tools/battleengine_camera_look_measurement.py` |
| Offline tests | `tools/battleengine_camera_look_measurement_test.py` |
| npm gate | `npm run test:battleengine-camera-look-measurement` |

Rate sources:

1. **orientation** — differentiate polled yaw/pitch radians (camera or body).
2. **yaw_axis_store** — absolute hypothesized `BattleEngine+0x278` store (same
   static hypothesis as walker turn dual-accept); useful when orientation
   differentiate is near-zero during pure Look hold.

## Non-claims

- Scaffold / synthetic fixtures do not authorize Core constants.
- Free-camera patch canaries do not authorize Core look rates.
- Body turn dual-accept (`WalkerLookYawRateMilliRadPerTick=3`) remains the
  current Core look-rate authority for **body** yaw only; camera presentation
  rates stay open until dual-accept.

## Next live steps

1. Bind Look axes under the existing receipt-bound pair runner.
2. Sample camera orientation **or** body yaw-axis under dual-attempt protocol.
3. Dual-accept → v1 JSON contract → translation policy → Core (if distinct from body turn).

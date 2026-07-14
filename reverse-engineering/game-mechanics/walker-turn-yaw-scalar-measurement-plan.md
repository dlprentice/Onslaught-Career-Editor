# Walker turn/yaw scalar measurement plan (M1.3)

Status: **in progress — harness scaffold landed; live dual-accept pending**  
Last updated: 2026-07-14  
Harness: `tools/battleengine_turn_yaw_measurement.py`  
Tests: `tools/battleengine_turn_yaw_measurement_test.py`

## Claim target

Scalar **walker turn/yaw rate** response in retail units (radians per second),
via exactly two accepted **copied-runtime** attempts, then a public contract and
a separate retail→Core translation policy **before** any Core turn constant.

## Evidence classes

| Class | Status |
|-------|--------|
| Source hypothesis | `mGroundTurnRate` default 1.5 (config quick-reference) — not Core authority |
| Steam static | `CGeneralVolume__ApplyYawInputByWeaponClass` updates axis near `+0x278`; jet `Turn` yaw/roll velocity near main-part `+0x278/+0x27c` |
| Copied-runtime | **Not yet** dual-accepted |
| Rebuild contract | Blocked until dual-accept + translation policy |

## Harness (landed)

Offline-capable pure analysis:

- `heading_from_velocity_xz` / `unwrap_delta` / `phase_yaw_rates`
- `analyze_turn_attempt` (baseline dominate, response/release latency)
- `materialize_turn_pair_envelope` → scaffold schema
  `battleengine-walker-turn-yaw-scalar-response.v0-scaffold` (explicit non-claims;
  **not** a live dual-accept contract)

## Live measurement remaining work

1. Bind turn input on safe-copy options (A/D or LEFT/RIGHT — confirm with
   defaultoptions / AppCore options path).
2. Sample heading (velocity-derived while moving, and/or orientation / yaw-axis
   store at hypothesized `BattleEngine+0x278`) on the existing receipt-bound
   observer cadence.
3. Run `run-two` style pair under `local-proofs/wt/` with lab hygiene strip.
4. Publish v1 contract only after two accepts; then translation policy; then Core.

## Non-claims

- No Core `TurnRate` / yaw constant from source defaults alone.
- Scaffold envelope from synthetic fixtures is not retail proof.
- Free-camera Q-yaw patch proofs are a different subsystem and do not close M1.3.

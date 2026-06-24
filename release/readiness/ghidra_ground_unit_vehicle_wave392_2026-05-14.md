# GroundUnit / GroundVehicle Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra metadata correction for the GroundUnit, GroundVehicle, CGroundVehicleGuide, and CMCGroundVehicle cluster. It updates saved names, signatures, comments, and tags for thirteen targets after dry run, apply, read-back exports, and focused validation.

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime gameplay behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/ground-unit-vehicle-wave392/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Corrected

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047c730` | `CGroundUnit__Init` | PASS | Called by `CGroundVehicle__Init`; initializes ground-unit state, thruster-linked nodes, movement/profile fields, and collision setup context. |
| `0x0047c8e0` | `CGroundUnit__CreateCollisionSphere` | PASS | Creates radius-derived collision sphere state and adds collision context for ground units. |
| `0x0047c970` | `CGroundUnit__UpdateLinkedEffectsByHeightClearance` | PASS | `CGroundUnit` RTTI vtable slot `66`; supersedes the older over-specific Cannon helper owner label. |
| `0x0047ce80` | `CGroundUnit__MarkDestroyedAndResetState` | PASS | `CGroundUnit` RTTI vtable slot `50`; calls unit destruction cleanup and clears the local reset/state field on success, superseding the older Cannon-local label. |
| `0x0047cea0` | `CGroundUnit__ClearLinkedThingFlagsAndResetCounter` | PASS | Walks the ground-unit linked set and clears associated state fields, superseding the older broad `CUnitAI` label. |
| `0x0047cfd0` | `CGroundVehicle__Init` | PASS | Calls `CGroundUnit__Init`, resolves the `WheelMotion` token, creates guide/component/controller state, and installs ground-vehicle context. |
| `0x0047d590` | `CGroundVehicleGuide__Constructor` | PASS | Called by `CGroundVehicle__Init`; installs the `CGroundVehicleGuide` vtable and allocates guide-owned buffers. |
| `0x0047d650` | `CGroundVehicleGuide__ScalarDeletingDestructor` | PASS | `CGroundVehicleGuide` RTTI vtable slot `1`; calls the destructor body and conditionally frees. |
| `0x0047d6d0` | `CGroundVehicleGuide__Destructor` | PASS | Restores guide/base cleanup state and releases owned linked objects. |
| `0x00496a50` | `CMCGroundVehicle__Constructor` | PASS | Called by `CGroundVehicle__Init`; installs the `CMCGroundVehicle` vtable and initializes controller fields. |
| `0x00496a80` | `CMCGroundVehicle__ScalarDeletingDestructor` | PASS | `CMCGroundVehicle` RTTI vtable slot `1`; calls the destructor body and conditionally frees. |
| `0x00496aa0` | `CMCGroundVehicle__Destructor` | PASS | Restores the controller vtable/base cleanup state and clears target ownership. |
| `0x0050ed10` | `CGroundUnit__Constructor` | PASS | Installs `CGroundUnit` primary/secondary vtables after the `CActor` constructor path. |

## Commands Run

```powershell
py -3 tools\ghidra_ground_unit_vehicle_wave392_probe_test.py
cmd.exe /c npm run test:ghidra-ground-unit-vehicle-wave392
py -3 -m py_compile tools\ghidra_ground_unit_vehicle_wave392_probe.py tools\ghidra_ground_unit_vehicle_wave392_probe_test.py
cmd.exe /c npm run test:ghidra-cannon-activation-signature-correction
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Result: PASS.

Important output:

- Focused probe unit tests passed with `2/2`.
- Package-script probe status was `PASS` with `13` targets, `16` metadata rows, `16` tag rows, and `0` failures.
- Python compile check passed.
- The refreshed Cannon activation wrapper probe passed after updating it to the current `CGroundUnit` helper names.
- Static re-audit queue probe status was `PASS`.

Headless dry/apply results:

- Dry run: `updated=0 skipped=13 renamed=0 would_rename=10 missing=0 bad=0`.
- Apply: `updated=13 skipped=0 renamed=10 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `16` metadata rows.
- `16` decompile exports.
- `58` xref rows.
- `16` tag rows.
- `4` vtable type rows.
- `512` vtable slot rows.

The refreshed queue reports `6027` functions, `1486` commented functions, `4541` commentless functions, `1916` undefined signatures, and `1886` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1486/6027 = 24.66%`; strict clean-signature `1424/6027 = 23.63%`.

Actual live Ghidra project backup verification passed at `G:\GhidraBackups\BEA_20260513_230202_post_wave392_ground_unit_vehicle_verified` with `19` files, `154504071` bytes, and `HashDiffCount=0`.

## What Is Proven

- The saved Ghidra project now records the checked GroundUnit, GroundVehicle, CGroundVehicleGuide, and CMCGroundVehicle names, signatures, comments, and tags with metadata, decompile, xref, tag, RTTI/vtable, and focused probe read-back.
- The saved Ghidra project now records `0x0047c970` and `0x0047ce80` as `CGroundUnit` helpers rather than over-specific Cannon-local helpers.
- The saved Ghidra project now records `0x0047cea0` as `CGroundUnit__ClearLinkedThingFlagsAndResetCounter` rather than the older broad `CUnitAI` label.
- The focused proof script validates saved metadata, tags, selected decompile tokens, RTTI/vtable context, xref context, and overclaim boundaries.

## What Is Not Proven

- This does not prove runtime ground-unit or ground-vehicle movement, guide, wheel-motion, collision, destruction, or component behavior.
- This does not prove exact Stuart-source method identity for every corrected target.
- This does not recover concrete class layouts, local variable names, local types, or structure definitions.
- This does not prove complete GroundUnit / GroundVehicle system coverage.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra metadata correction evidence. It should be treated as static retail-binary evidence and as a correction to stale docs/probes, not as runtime proof or source-complete gameplay implementation.

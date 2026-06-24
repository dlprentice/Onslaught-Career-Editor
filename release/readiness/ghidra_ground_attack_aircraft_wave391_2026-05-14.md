# GroundAttackAircraft / GroundAttackAI / GroundAttackGuide Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra metadata correction for the GroundAttackAircraft, CGroundAttackAI, and CGroundAttackGuide cluster. It updates saved names, signatures, comments, and tags for nine targets after dry run, apply, read-back exports, and focused validation.

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime gameplay behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/ground-attack-aircraft-wave391/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Corrected

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047bab0` | `CGroundAttackAI__InitState` | PASS | Called after the `CGroundAttackAI` allocation/vtable install in `CGroundAttackAircraft__Init`; clears `+0x60`, randomizes the `+0x64` timer/float, and closes the bay. |
| `0x0047bbf0` | `CGroundAttackAircraft__Init` | PASS | Function table `0x005e2bf0` slot `0`; delegates to `CAirUnit__Init`, allocates/installs `CMCGroundAttack`, `CGroundAttackAI`, and `CGroundAttackGuide`, then initializes default animation/state fields. |
| `0x0047bd70` | `CGroundAttackAI__ScalarDeletingDestructor` | PASS | `CGroundAttackAI` RTTI vtable `0x005dbd4c` slot `1` scalar-deleting destructor wrapper. |
| `0x0047bd90` | `CGroundAttackAI__Destructor` | PASS | Restores the `CUnitAI` base vtable and removes tracked handles before monitor shutdown. |
| `0x0047be30` | `CGroundAttackGuide__ScalarDeletingDestructor` | PASS | `CGroundAttackGuide` RTTI vtable `0x005dbd20` slot `1` scalar-deleting destructor wrapper; corrects the stale GillMHead label. |
| `0x0047be50` | `CGroundAttackGuide__Destructor` | PASS | Removes the linked reader/set field at `+0x2c` before monitor shutdown; corrects the stale GillMHead label. |
| `0x0047bfa0` | `CGroundAttackAircraft__OpenBay` | PASS | If bay state `+0x27c` is idle or closing, sets state `2` and plays the open animation token. |
| `0x0047bff0` | `CGroundAttackAircraft__CloseBay` | PASS | If bay state `+0x27c` is open or opening, sets state `3` and plays the close animation token. |
| `0x0047c040` | `CGroundAttackAircraft__AdvanceCloseShootAnimationState` | PASS | Function table `0x005e2bf0` slot `50`; advances open/shoot/close/idle animation state and writes bay state `+0x27c`; corrects the older broad `CUnitAI` label. |

## Commands Run

```powershell
py -3 tools\ghidra_ground_attack_aircraft_wave391_probe_test.py
cmd.exe /c npm run test:ghidra-ground-attack-aircraft-wave391
py -3 -m py_compile tools\ghidra_ground_attack_aircraft_wave391_probe.py tools\ghidra_ground_attack_aircraft_wave391_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Result: PASS.

Important output:

- Focused probe unit tests passed with `2/2`.
- Package-script probe status was `PASS` with `9` targets, `9` metadata rows, `9` tag rows, and `0` failures.
- Python compile check passed. A separate mistaken `py_compile` invocation included the Java Ghidra script and failed as expected because Java is not Python; the corrected Python-only compile passed.
- Static re-audit queue probe status was `PASS`.

Headless dry/apply results:

- Dry run: `updated=0 skipped=9 renamed=0 would_rename=7 missing=0 bad=0`.
- Apply: `updated=9 skipped=0 renamed=7 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `9` metadata rows.
- `9` decompile exports.
- `11` xref rows.
- `9` tag rows.
- `2` vtable type rows.
- `192` vtable slot rows.
- `80` pointer-table rows.

The refreshed queue reports `6027` functions, `1475` commented functions, `4552` commentless functions, `1919` undefined signatures, and `1894` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1475/6027 = 24.47%`; strict clean-signature `1413/6027 = 23.44%`.

## What Is Proven

- The saved Ghidra project now records the checked GroundAttackAircraft init/bay-state helpers and adjacent CGroundAttackAI / CGroundAttackGuide destructor paths with RTTI, vtable, pointer-table, xref, tag, signature, and comment read-back.
- The saved Ghidra project now records `0x0047bbf0` as `CGroundAttackAircraft__Init`, superseding the older constructor label.
- The saved Ghidra project now records `0x0047be30` and `0x0047be50` as `CGroundAttackGuide` destructor paths, superseding the stale GillMHead labels.
- The saved Ghidra project now records `0x0047c040` as `CGroundAttackAircraft__AdvanceCloseShootAnimationState`, superseding the older broad `CUnitAI` label.
- The focused proof script validates the saved metadata, tags, selected decompile tokens, vtable/RTTI context, pointer-table context, xref context, and overclaim boundaries.

## What Is Not Proven

- This does not prove runtime ground-attack aircraft bay animation, targeting, AI, guide, weapon, or destruction behavior.
- This does not prove exact Stuart-source method identity. `GroundAttackAircraft.cpp` is still missing from the available Stuart source corpus in this repo.
- This does not recover concrete class layouts, local variable names, local types, or structure definitions.
- This does not prove complete GroundAttackAircraft / CGroundAttackAI / CGroundAttackGuide system coverage.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra metadata correction evidence. It should be treated as static retail-binary evidence and as a correction to stale docs/probes, not as runtime proof or source-complete gameplay implementation.

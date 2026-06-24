# Firing Animation Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra metadata correction for three adjacent firing-animation and cleanup helpers. It updates saved signatures, comments, and tags after dry run, apply, read-back exports, and focused validation.

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime gameplay behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/firing-animation-wave393/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Corrected

| Address | Current saved name | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047d3b0` | `CMonitor__TryQueuePrefireAnimation` | PASS | `CGroundVehicle vtable slots 86 and 87` context: slot `86` points here. The body calls `CUnit__UpdateDeployStateAndChargeEffects`, checks gate fields, validates the `prefire` animation token, and dispatches vfunc `+0xf0` when an animation index exists. |
| `0x0047d420` | `CUnitAI__QueueFiringOrPostfireAnimation` | PASS | `CGroundVehicle vtable slots 86 and 87` context: slot `87` points here. The body calls `CUnitAI__FinalizeSpawnAndAdvanceState`, chooses `firing` or `postfire`, validates the animation index, and dispatches vfunc `+0xf0`. |
| `0x0047d670` | `CUnitAI__FreeOwnedObjects_10_18` | PASS | Unwind-target cleanup helper that frees owned object pointers at `+0x18` and `+0x10` through `OID__FreeObject`; the read-back does not claim slot clearing. |

## Commands Run

```powershell
py -3 tools\ghidra_firing_animation_wave393_probe_test.py
cmd.exe /c npm run test:ghidra-firing-animation-wave393
py -3 -m py_compile tools\ghidra_firing_animation_wave393_probe.py tools\ghidra_firing_animation_wave393_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\release_curated_manifest.py
py -3 tools\release_curated_manifest.py --check
py -3 tools\release_profile_snapshot.py
py -3 tools\release_profile_snapshot.py --check
cmd.exe /c npm run test:public-allowlist
cmd.exe /c npm run test:md-links
cmd.exe /c npm run test:doc-commands
py -3 tools\docsync_check.py
cmd.exe /c npm run test:repo-hygiene
```

Result: PASS.

Important output:

- Focused probe unit tests passed with `3/3`.
- Package-script probe status was `PASS` with `3` targets and `0` failures.
- Python compile check passed.
- Static re-audit queue probe status was `PASS`.
- Curated release manifest selected `2140` files and public allowlist checked `2140` rows.
- Release profile counts were `R0=2202 R2=0 R3=2 R4=18188`.
- Markdown links passed.
- Doc command check passed with `3129` documented npm command references checked.
- Docsync and repo hygiene passed.

Headless dry/apply results:

- Dry run: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply: `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `6` metadata rows.
- `6` decompile exports.
- `10` xref rows.
- `6` tag rows.
- `128` `CGroundVehicle` vtable slot rows.
- `726` instruction rows.

The refreshed queue reports `6027` functions, `1489` commented functions, `4538` commentless functions, `1916` undefined signatures, and `1883` `param_N` signatures. Current confirmation proxies are telemetry only: comment-backed `1489/6027 = 24.71%`; strict clean-signature `1427/6027 = 23.68%`.

Actual live Ghidra project backup verification passed at `G:\GhidraBackups\BEA_20260513_235110_post_wave393_firing_animation_verified` with `19` files, `154635143` bytes, and `HashDiffCount=0`.

## What Is Proven

- The saved Ghidra project now records hardened signatures, comments, and tags for `0x0047d3b0`, `0x0047d420`, and `0x0047d670`.
- The saved Ghidra project now records `0x0047d3b0` and `0x0047d420` as `CGroundVehicle` vtable slot `86` / `87` animation helpers with `prefire`, `firing`, `postfire`, `FindAnimationIndex`, and vfunc `+0xf0` read-back evidence.
- The saved Ghidra project now records `0x0047d670` as a cleanup helper that frees `+0x18` and `+0x10`; it does not claim slot clearing.
- The focused proof script validates saved metadata, tags, selected decompile tokens, vtable context, xref context, instruction tokens, and overclaim boundaries.

## What Is Not Proven

- This does not prove runtime animation behavior.
- This does not prove exact Stuart-source method identity for every corrected target.
- This does not recover concrete class layouts, local variable names, local types, or structure definitions.
- This does not prove complete GroundVehicle or UnitAI coverage.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra metadata correction evidence. It should be treated as static retail-binary evidence and as a correction to stale docs/probes, not as runtime gameplay evidence or source-complete gameplay implementation.

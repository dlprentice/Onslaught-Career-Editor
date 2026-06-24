# Terrain Tail Ghidra Correction - 2026-05-14

Status: public-safe evidence

Source branch: `wip/sandbox`

Recorded at: 2026-05-14

## Scope

This wave records a serialized saved-Ghidra correction/hardening pass for five adjacent hazard, UnitAI, and heightfield-tail helpers:

- `0x0047e6e0` `CHazard__VFunc02_CleanupWorldSoundAndLinkedState`
- `0x0047e870` `CUnitAI__ResetWorkGrid1024AndFlags`
- `0x0047e8a0` `CUnitAI__FreeOwnedObjects_24_1028`
- `0x0047ef20` `CHeightField__RecomputeGridExtentsAndHeightRange`
- `0x0047f750` `CHeightField__Load`

The main owner correction is `0x0047ef20`: the prior saved `CDXBattleLine__RecomputeGridExtentsAndHeightRange` label was narrowed to heightfield ownership because the body walks heightfield sample-grid dimensions, sample rows, threshold state, grid extents, and height min/max sentinels. CDXBattleLine callers still consume this helper.

It does not mutate `BEA.exe`, launch the game, patch the installed Steam copy, include raw decompile excerpts, or prove runtime terrain behavior.

## Private Evidence Policy

Ignored local evidence remains under `subagents/ghidra-static-reaudit/terrain-tail-wave396/current/`. This report does not include decompiled source excerpts, private absolute paths, screenshots, frame data, copied executables, copied saves, raw private JSON, or Ghidra project files.

## Functions Hardened

| Address | Saved name after Wave396 | Result | Selected evidence |
| --- | --- | --- | --- |
| `0x0047e6e0` | `CHazard__VFunc02_CleanupWorldSoundAndLinkedState` | PASS | Corrected the address-suffixed vfunc label to a bounded cleanup name. Read-back shows sound-sample cleanup, linked-state cleanup at the `+0x80` family, world occupancy-grid removal, and base cleanup dispatch. |
| `0x0047e870` | `CUnitAI__ResetWorkGrid1024AndFlags` | PASS | Corrected the return/receiver signature. Read-back clears `+0x20/+0x24`, zeroes `1024` dwords rooted at `+0x28`, clears `+0x1028`, and returns the receiver. |
| `0x0047e8a0` | `CUnitAI__FreeOwnedObjects_24_1028` | PASS | Corrected the receiver signature. Read-back frees and clears owned pointers at `+0x24` and `+0x1028`. |
| `0x0047ef20` | `CHeightField__RecomputeGridExtentsAndHeightRange` | PASS | Corrected the older `CDXBattleLine` owner label to heightfield ownership. Read-back uses `+0x10bc/+0x10c0` dimensions, `+0x20` sample rows, `+0x1034` threshold context, and height min/max sentinels. |
| `0x0047f750` | `CHeightField__Load` | PASS | Corrected the undefined saved signature to thiscall with a chunk-reader argument. Read-back validates `0x13dc`, calls `CHeightField__InitColorGradient`, allocates `0xa2000` bytes, and reads `9x9` tile blocks. |

## Commands Run

```powershell
py -3 tools\ghidra_terrain_tail_wave396_probe_test.py
py -3 -m py_compile tools\ghidra_terrain_tail_wave396_probe.py tools\ghidra_terrain_tail_wave396_probe_test.py
```

Headless dry/apply results:

- Dry run: `updated=0 skipped=5 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply: `updated=5 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Apply log reported `REPORT: Save succeeded`.

Read-back results:

- `5` metadata rows.
- `5` decompile exports.
- `7` xref rows.
- `5` tag rows.
- `1305` instruction rows.

Additional focused, release, docs, backup, and hygiene validation is recorded in the campaign evidence ledger for the final committed wave.

## What Is Proven

- The saved Ghidra project now records the Wave396 names, signatures, comments, and tags for the five selected terrain-tail targets.
- The saved `0x0047ef20` owner label now matches the heightfield body evidence while preserving CDXBattleLine caller context.
- The saved `0x0047f750` signature is no longer undefined and now records the chunk-reader argument seen in the retail read-back.
- The static retail read-back evidence ties the tranche to hazard cleanup, UnitAI grid/owned-object cleanup, heightfield extent recomputation, and heightfield loading.

## What Is Not Proven

- This does not prove runtime terrain behavior.
- This does not prove runtime hazard behavior.
- This does not prove runtime UnitAI behavior.
- This does not prove exact concrete struct layouts, local variable names, local types, or all class fields.
- This does not mutate or patch `BEA.exe`.
- This does not prove rebuild parity.

## Release Posture

GREEN for public-safe saved-Ghidra correction evidence after focused dry/apply/read-back. Treat this as static retail-binary evidence and source-parity support where available, not as runtime behavior evidence or complete source-level gameplay implementation.

# BattleEngine Weapon Slot0 Raw Boundary - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe read-only raw disassembly boundary probe, not retail identity or runtime proof

## Objective

Continue the construction-side weapon callback investigation from `release/readiness/battleengine_weapon_construction_candidate_2026-05-09.md`.

This pass asks a narrower static question: do the current ignored raw disassembly exports show a stable outer slot-0 stub at `0x00506930`, its inner body at `0x005069f0`, and the checked return/post-return boundary without mutating Ghidra or claiming exact `CWeapon::Fire` / `CBattleEngine::WeaponFired` identity?

## Inputs

- Outer raw stub disassembly: `subagents/battleengine-weapon-construction-candidates/current/vtable/slot0_00506930_function_disasm.tsv`
- Inner raw body disassembly: `subagents/battleengine-weapon-construction-candidates/current/vtable/slot0_005069f0_body_disasm.tsv`
- Probe: `tools/battleengine_weapon_slot0_boundary_probe.py`
- Probe test: `tools/battleengine_weapon_slot0_boundary_probe_test.py`

## Commands

```powershell
py -3 tools\battleengine_weapon_slot0_boundary_probe_test.py
py -3 tools\battleengine_weapon_slot0_boundary_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_slot0_boundary_probe.py tools\battleengine_weapon_slot0_boundary_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-slot0-boundary
```

## Result

```text
BattleEngine weapon slot0 boundary probe
Status: PASS
Classification: raw-slot0-boundary-candidate
Outer stub inner call: 0x005069f0
Inner terminal RET: 0x005078ab
First post-RET row: 0x005078b0
Unexpected stealth/AddProjectile tokens: 0
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| Outer stub start | `0x00506930` is present in the checked raw export. |
| Outer stub shape | The checked outer stub carries the current prologue shape, a `0x1389` event/tag compare, a call to `0x005069f0`, and observed `RET 0x4` exits at `0x005069a3` and `0x005069ed`. |
| Inner body start | `0x005069f0` starts the checked inner body export. |
| Inner helper calls | The checked inner body reaches projectile helper-family calls including `CWorldPhysicsManager__CreateProjectile`, `CEngine__SetProjectileTargetReader`, `CEngine__CanSpawnBurstForResolvedEntry`, `CEngine__MoveBurstReaderToCooldownSet`, and `CEngine__RandomizeBurstOffsetsAndAccumulateRange`. |
| Inner exit boundary | The checked body includes branch-exit targets `0x0050787d`, `0x00507891`, and `0x00507893`, terminal `RET` at `0x005078ab`, and first post-return row `0x005078b0`. |
| Stealth/AddProjectile tokens | The checked raw boundary rows contain no direct `CBattleEngine__AddProjectile` / `0x00406560` helper addresses and no tracked stealth-adjacent offset tokens `0x4ac`, `0x5d4`, `0x5d8`, or `0x5dc`. |

The ignored JSON report is written to `subagents/battleengine-weapon-construction-candidates/current/weapon-slot0-boundary.json`.

## What This Proves

- Current read-only raw disassembly exports expose an outer weapon vtable slot-0 stub at `0x00506930`.
- The outer stub calls an inner raw body at `0x005069f0`.
- The checked inner body reaches the same projectile creation/target helper-family calls identified by the construction-candidate wave.
- The checked inner body has terminal `RET` at `0x005078ab`, with first post-return row `0x005078b0`.
- The checked raw boundary rows do not contain direct `CBattleEngine__AddProjectile` / `0x00406560` helper addresses or tracked stealth-adjacent offset tokens.

## What This Does Not Prove

- This does not create, rename, or mutate a Ghidra function boundary.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove retail weapon fire never clears stealth.
- This does not rule out an indirect, virtual-dispatch, callback, inlined, or runtime-only stealth reset elsewhere.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not patch or launch `BEA.exe` and does not inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. The useful new fact is a tighter raw boundary for the current construction-side projectile-body candidate: slot-0 raw code starts at `0x00506930`, calls inner body `0x005069f0`, and the checked inner body returns at `0x005078ab` before a separate post-return row at `0x005078b0`.

Future static work should either read back this candidate through a non-mutating Ghidra function-boundary/export pass if available, or continue searching indirect weapon callback/caller identity. Runtime cloak activation and fire-while-cloaked behavior still require a separate copied-profile proof with a verified cloak-active baseline.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, function names, call target names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.

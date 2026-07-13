# BattleEngine Weapon Construction Candidate - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe read-only Ghidra construction/vtable triage, not retail identity or runtime proof

## Objective

Continue narrowing the remaining `weapon_fire_breaks_stealth` source-only anchor from a construction-side path after direct `CBattleEngine__AddProjectile` xrefs proved too narrow.

This pass asks a bounded static question: can current read-only Ghidra exports connect weapon creation to a stronger projectile-emitting raw-code candidate, without mutating Ghidra or claiming exact `CWeapon::Fire` / `CBattleEngine::WeaponFired` identity?

## Inputs

- Function-name export: `subagents/battleengine-function-name-scan/current/functions_all.tsv`
- Read-only construction decompile exports under `subagents/battleengine-weapon-construction-candidates/current/decompile/`
- Read-only vtable dump: `subagents/battleengine-weapon-construction-candidates/current/vtable/equipment_vtable_005dfc94.tsv`
- Read-only raw slot-0 body disassembly: `subagents/battleengine-weapon-construction-candidates/current/vtable/slot0_005069f0_body_disasm.tsv`
- Probe: `tools/battleengine_weapon_construction_candidate_probe.py`
- Probe test: `tools/battleengine_weapon_construction_candidate_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-weapon-construction-candidates/current/decompile/addresses.txt subagents/battleengine-weapon-construction-candidates/current/decompile 40
tools/run_ghidra_headless_postscript.sh DumpPointerTable.java 0x005dfc94 32 subagents/battleengine-weapon-construction-candidates/current/vtable/equipment_vtable_005dfc94.tsv
tools/run_ghidra_headless_postscript.sh DumpDisassemblyRange.java 0x00506930 0x00506970 subagents/battleengine-weapon-construction-candidates/current/vtable/slot0_00506930_disasm.tsv
tools/run_ghidra_headless_postscript.sh DumpDisassemblyRange.java 0x005069f0 0x005078b0 subagents/battleengine-weapon-construction-candidates/current/vtable/slot0_005069f0_body_disasm.tsv
```

Probe validation:

```powershell
py -3 tools\battleengine_weapon_construction_candidate_probe_test.py
py -3 tools\battleengine_weapon_construction_candidate_probe.py --check
py -3 -m py_compile tools\battleengine_weapon_construction_candidate_probe.py tools\battleengine_weapon_construction_candidate_probe_test.py
cmd.exe /c npm run test:battleengine-weapon-construction-candidate
```

## Result

```text
BattleEngine weapon construction candidate probe
Status: PASS
Classification: construction-vtable-slot0-projectile-body-candidate
Slot0 raw address: 0x00506930
Slot0 call targets observed: 28
Unexpected stealth/AddProjectile tokens: 0
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| Weapon creation | `CWorldPhysicsManager__CreateWeaponByIndex` at `0x0050f6d0` allocates `0xb0` bytes and calls `CEquipment__ctor_like_00505e00`. |
| Constructor | `CEquipment__ctor_like_00505e00` installs vtable pointer `0x005dfc94`. |
| Vtable slot 0 | `0x005dfc94[0] -> 0x00506930`, currently `MISSING` as a Ghidra function export target. |
| Vtable slot 1 | `0x005dfc94[1] -> 0x00505f70`, the already known destructor-like `CWeapon__VFunc_01_00505f70`. |
| Raw slot-0 body | The checked raw body reaches projectile helper-family calls including `CWorldPhysicsManager__CreateProjectile`, `CEngine__SetProjectileTargetReader`, `CEngine__CanSpawnBurstForResolvedEntry`, `CEngine__MoveBurstReaderToCooldownSet`, and `CEngine__RandomizeBurstOffsetsAndAccumulateRange`. |
| Stealth/AddProjectile tokens | The checked raw body range contains no direct `CBattleEngine__AddProjectile` / `0x00406560` helper addresses and no tracked stealth-adjacent offset tokens `0x4ac`, `0x5d4`, `0x5d8`, or `0x5dc`. |

The ignored JSON report is written to `subagents/battleengine-weapon-construction-candidates/current/weapon-construction-candidate.json`.

## What This Proves

- Current read-only construction exports connect `CWorldPhysicsManager__CreateWeaponByIndex` to `CEquipment__ctor_like_00505e00`.
- The constructor installs vtable pointer `0x005dfc94`.
- Vtable slot 0 points at raw code `0x00506930`, and slot 1 points at the already known destructor-like `CWeapon` vfunc.
- The raw slot-0 body reaches projectile creation and projectile-target helper calls, making it a stronger construction-side projectile body candidate than the earlier RTTI-adjacent table attempt.
- The checked raw slot-0 body range does not contain direct `CBattleEngine__AddProjectile` / `0x00406560` helper addresses or tracked stealth-adjacent offset tokens.

## What This Does Not Prove

- This does not rename `0x00506930` or prove final function boundaries.
- This does not prove exact source `CWeapon::Fire` or `CBattleEngine::WeaponFired` identity.
- This does not prove retail weapon fire never clears stealth.
- This does not rule out an indirect, virtual-dispatch, callback, inlined, or runtime-only stealth reset elsewhere.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, launch the game, or inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. The useful new fact is a better static candidate path: current weapon construction evidence leads to vtable slot-0 raw code at `0x00506930`, whose body reaches projectile creation/set-target helper calls without showing the currently tracked stealth-reset tokens.

Future static work should either define/read back a Ghidra function boundary for `0x00506930` and its internal `0x005069f0` body without mutation overclaim, or pivot to the copied-profile runtime proof once a cloak-active baseline is available.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, function names, call target names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.

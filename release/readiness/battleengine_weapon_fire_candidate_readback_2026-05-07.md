# BattleEngine Weapon-Fire Candidate Read-Back - 2026-05-07

Status: public-safe read-only Ghidra/source provenance evidence, not runtime proof

## Objective

Check whether the most obvious currently named retail `CWeapon` candidates close the missing source boundary behind `weapon->Fire()`.

This pass follows the prior source-path evidence:

- player fire input reaches `CBattleEngine::FireWeapon()`,
- `CBattleEngine::FireWeapon()` delegates to the walker or jet part,
- the walker/jet part calls `weapon->Fire()`,
- the `references/Onslaught` submodule includes `Weapon.h` references but does not contain `Weapon.h` or `Weapon.cpp`.

## Commands

Source/submodule provenance checks:

```powershell
git ls-files -s references/Onslaught references/AYAResourceExtractor
git -C references/Onslaught status --short --branch
git -C references/Onslaught log --all --oneline -- Weapon.h Weapon.cpp
git -C references/Onslaught ls-tree -r --name-only HEAD
```

Read-only Ghidra exports:

```powershell
wsl bash -lc "cd /mnt/c/Users/david/source/Onslaught-Career-Editor-private && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-weapon-fire-candidate/current/decompile/addresses.txt subagents/battleengine-weapon-fire-candidate/current/decompile 30"
wsl bash -lc "cd /mnt/c/Users/david/source/Onslaught-Career-Editor-private && tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-weapon-fire-candidate/current/xrefs/addresses.txt subagents/battleengine-weapon-fire-candidate/current/xrefs/cweapon_type_xrefs.tsv"
wsl bash -lc "cd /mnt/c/Users/david/source/Onslaught-Career-Editor-private && tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-weapon-fire-candidate/current/xrefs/col_addresses.txt subagents/battleengine-weapon-fire-candidate/current/xrefs/cweapon_col_xrefs.tsv"
wsl bash -lc "cd /mnt/c/Users/david/source/Onslaught-Career-Editor-private && tools/run_ghidra_headless_postscript.sh DumpPointerTable.java 0x00617304 24 subagents/battleengine-weapon-fire-candidate/current/xrefs/cweapon_vtable_00617304.tsv"
wsl bash -lc "cd /mnt/c/Users/david/source/Onslaught-Career-Editor-private && tools/run_ghidra_headless_postscript.sh ResolveVtableTypeNames.java subagents/battleengine-weapon-fire-candidate/current/xrefs/vtable_candidates.txt subagents/battleengine-weapon-fire-candidate/current/xrefs/vtable_type_names.tsv"
```

The first `DumpPointerTable.java` run used the wrong argument order and failed before producing evidence. It was rerun with the script's documented `<table_addr> <entry_count> <out_tsv>` order and completed.

## Results

Source/submodule provenance:

- `references/Onslaught` is a git submodule at `792545b996365f383781c666d145ea6cbda83f3a`.
- The submodule is on `main...origin/main`.
- The checked submodule history has no `Weapon.h` or `Weapon.cpp` path.
- The checked submodule tree has no tracked `Weapon.h`, `Weapon.cpp`, or obvious weapon/projectile source file path.

Read-only Ghidra export:

```text
ExportFunctionsByAddressDecompile.java
targets=2 dumped=2 missing=0 failed=0

0x00505f70 CWeapon__VFunc_01_00505f70
0x00505f90 CWeapon__DetachFromSetAndShutdownMonitor
```

The decompile for `0x00505f70` calls `CWeapon__DetachFromSetAndShutdownMonitor(this)`. This makes the current best interpretation destructor/shutdown-like, not `CWeapon::Fire()`.

The `CWeapon` RTTI/string path produced a type/string xref and a related record xref, but resolving `0x00617304` as a vtable did not produce a trustworthy named function-slot table or demangled `CWeapon` type row. It should not be used as a fire-callback proof.

## What This Proves

- The missing `Weapon.h` / `Weapon.cpp` boundary is real in the current `references/Onslaught` submodule checkout and history checked here.
- The obvious currently named retail `CWeapon` candidates at `0x00505f70` / `0x00505f90` do not close the `weapon->Fire()` source boundary.
- `0x00505f70` should not be promoted as `CWeapon::Fire()` based on current evidence.
- The `CWeapon` RTTI string alone is not enough to recover the firing callback slot in the current Ghidra state.

## What This Does Not Prove

- This does not prove the retail binary lacks `CWeapon::Fire()`.
- This does not prove exact source-to-retail identity for `CBattleEngine::WeaponFired`.
- This does not prove runtime stealth behavior after firing while cloaked.
- This does not prove every weapon, projectile, vtable, or statement-helper path.
- This did not mutate Ghidra intentionally, apply a rename map, patch `BEA.exe`, launch the game, or inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

The highest-value next step is not promoting the currently named `CWeapon` vfunc candidate. The remaining useful options are:

- identify the actual retail weapon-fire callback through projectile-emission or callsite/xref evidence,
- recover additional source/reference material for the missing weapon implementation,
- or execute the copied-profile runtime plan at `release/readiness/battleengine_weapon_stealth_runtime_proof_plan_2026-05-07.md`.

Until then, `weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting.

## Privacy / Release Safety

This report is public-safe. Raw decompile, xref, pointer-table, and type-resolution outputs stay ignored under `subagents/battleengine-weapon-fire-candidate/`. The report includes only sanitized addresses, names, counts, command classes, and proof boundaries. It does not include binaries, private absolute paths, screenshots, frame data, copied executables, copied saves, debugger logs, Ghidra mutation logs, or raw runtime proof JSON.

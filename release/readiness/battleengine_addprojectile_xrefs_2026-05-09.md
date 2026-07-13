# BattleEngine AddProjectile Xref Triage - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe read-only Ghidra xref triage, not retail identity or runtime proof

## Objective

Narrow the remaining `weapon_fire_breaks_stealth` source-only anchor after the projectile-helper stealth scan.

This pass asks a smaller static question: do direct Ghidra xrefs to the already named `CBattleEngine__AddProjectile` helper expose another likely weapon-fire wrapper/callback, or are those direct xrefs currently confined to the known target/projectile helper?

## Inputs

- Target helper: `CBattleEngine__AddProjectile` at `0x00406fc0`
- Expected direct caller context: `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` at `0x00406560`
- Ignored read-only xref export: `subagents/battleengine-addprojectile-xrefs/current/xrefs/addprojectile_xrefs.tsv`
- Probe: `tools/battleengine_addprojectile_xref_probe.py`
- Probe test: `tools/battleengine_addprojectile_xref_probe_test.py`

## Commands

Read-only Ghidra xref export:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-addprojectile-xrefs/current/xrefs/addresses.txt subagents/battleengine-addprojectile-xrefs/current/xrefs/addprojectile_xrefs.tsv"
```

Probe validation:

```powershell
py -3 tools\battleengine_addprojectile_xref_probe_test.py
py -3 tools\battleengine_addprojectile_xref_probe.py --check
py -3 -m py_compile tools\battleengine_addprojectile_xref_probe.py tools\battleengine_addprojectile_xref_probe_test.py
cmd.exe /c npm run test:battleengine-addprojectile-xrefs
```

## Result

```text
BattleEngine AddProjectile xref probe
Status: PASS
Classification: addprojectile-xrefs-confined-to-projectile-helper
Xref rows: 4
Unexpected caller rows: 0
```

Current direct xrefs to `CBattleEngine__AddProjectile`:

| Target | From address | From function |
| --- | --- | --- |
| `0x00406fc0` | `0x004068d9` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` |
| `0x00406fc0` | `0x00406a51` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` |
| `0x00406fc0` | `0x00406aae` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` |
| `0x00406fc0` | `0x00406d06` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` |

The ignored JSON report is written to `subagents/battleengine-addprojectile-xrefs/current/addprojectile-xref-probe.json`.

## What This Proves

- The current read-only Ghidra xref export has four direct xrefs to `CBattleEngine__AddProjectile` at `0x00406fc0`.
- All four direct xrefs originate inside `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` at `0x00406560`.
- The direct `AddProjectile` caller set does not currently expose a separate retail `CWeapon::Fire` or `CBattleEngine::WeaponFired` body.

## What This Does Not Prove

- This does not identify the exact retail `CBattleEngine::WeaponFired` implementation.
- This does not prove retail weapon fire never clears stealth.
- This does not rule out an inlined, virtual-dispatch, callback, indirect, or runtime-only weapon-fire path outside direct `AddProjectile` xrefs.
- This does not prove runtime cloak activation, target-lock behavior, projectile behavior, or fire-while-cloaked behavior.
- This does not mutate Ghidra, apply a rename map, patch `BEA.exe`, launch the game, or inspect private runtime captures.
- This does not make the repository rebuildable from scratch.

## Outcome

`weapon_fire_breaks_stealth` remains source-only in aggregate source-to-binary gap accounting. The useful new fact is narrower: the direct `CBattleEngine__AddProjectile` xref set is currently confined to the already studied `0x00406560` target/projectile helper, so the remaining static search should move toward indirect weapon callback identity or a separately scoped copied-profile runtime proof with a verified cloak-active baseline.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses already present in repo evidence, function names, callsite counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, or Ghidra mutation logs.

# Ghidra BattleEngine Helper Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra name/signature/comment evidence, not final type/source/runtime proof

## Objective

Continue the saved-Ghidra static re-audit on a coherent early `CBattleEngine` helper cluster. This pass corrects two destructor labels that were visibly inverted, hardens eight helper signatures, and saves proof-boundary comments around projectile/target helper context without claiming the unresolved weapon-fired stealth reset identity.

## Inputs

- Targets:
  - `0x00405a40` `CBattleEngine__dtor_base`
  - `0x00405f60` `CBattleEngine__scalar_deleting_dtor`
  - `0x00405f80` `CBattleEngine__VFunc_02_00405f80`
  - `0x004063a0` `CBattleEngine__GetFloatAt0x118_AsDouble`
  - `0x004063b0` `CBattleEngine__UpdateWeaponEffect`
  - `0x00406460` `CBattleEngine__SwapPrimarySecondaryPartReadersForState`
  - `0x00406560` `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`
  - `0x00406fc0` `CBattleEngine__AddProjectile`
- Raw evidence root: `subagents/ghidra-static-reaudit/battleengine-helper-signature-tranche/current/`
- Signature script: `tools/ApplyBattleEngineHelperSignatureTranche.java`
- Probe: `tools/ghidra_battleengine_helper_signature_tranche_probe.py`
- Probe test: `tools/ghidra_battleengine_helper_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_battleengine_helper_signature_tranche_probe_test.py
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\battleengine-helper-signature-tranche\current\rename_map_battleengine_helpers.txt
cmd.exe /c npm run test:ghidra-battleengine-helper-signature-tranche
py -3 -m py_compile tools\ghidra_battleengine_helper_signature_tranche_probe.py tools\ghidra_battleengine_helper_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata/decompile/xref/instruction exports captured the eight selected `CBattleEngine` helper targets.
- Headless rename dry/apply corrected `0x00405a40` from the old scalar-deleting destructor label to `CBattleEngine__dtor_base` and `0x00405f60` from a generic vfunc label to `CBattleEngine__scalar_deleting_dtor`.
- Headless signature dry/apply hardened all eight selected targets.
- Headless comment dry/apply saved proof-boundary comments for all eight targets.
- Metadata, decompile, xref, instruction, and quality-snapshot read-back verified the saved project state.

## Result

```text
BattleEngine helper signature tranche: PASS
Targets: 8
Renamed targets: 2
Signature-hardened targets: 8
Stale names: 0
Stale param/undefined signatures: 0
Comment overclaims: 0
Weapon-fired stealth status: unresolved
Xref rows: 15
Instruction rows: 2888
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00405a40` | `void __fastcall CBattleEngine__dtor_base(void * this)` |
| `0x00405f60` | `void * __thiscall CBattleEngine__scalar_deleting_dtor(void * this, byte flags)` |
| `0x00405f80` | `void __fastcall CBattleEngine__VFunc_02_00405f80(void * this)` |
| `0x004063a0` | `double __fastcall CBattleEngine__GetFloatAt0x118_AsDouble(void * this)` |
| `0x004063b0` | `void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)` |
| `0x00406460` | `void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(void * this)` |
| `0x00406560` | `void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(void * this)` |
| `0x00406fc0` | `void __thiscall CBattleEngine__AddProjectile(void * this, void * target, float lifetime, int modeFlag)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `426`
- Commentless functions: `5440`
- Undefined signatures: `2076`
- `param_N` signatures: `2525`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The saved Ghidra project no longer carries the stale `CBattleEngine__scalar_deleting_dtor_00405a40` / `CBattleEngine__VFunc_01_00405f60` label split for this destructor pair.
- The selected early `CBattleEngine` helpers now have object-pointer signatures instead of stale `param_1` or `undefined` signatures.
- `CBattleEngine__AddProjectile` now has a saved `__thiscall` signature with target, lifetime, and mode-flag arguments matching the current helper call shape.
- `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` remains documented as tracked-target/projectile helper context with direct calls into `CBattleEngine__AddProjectile`.
- The comments and probe explicitly preserve the unresolved `weapon_fire_breaks_stealth` boundary.

## What This Does Not Prove

- This does not identify the exact retail implementation of source `CBattleEngine::WeaponFired`.
- This does not prove retail weapon fire clears stealth.
- This does not close `weapon_fire_breaks_stealth`.
- This does not prove runtime cloak activation or fire-while-cloaked behavior.
- This does not prove concrete `CBattleEngine` field layout, Ghidra structure types, local variable names, tags, or full static-binary completion.
- This does not prove rebuild parity.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.

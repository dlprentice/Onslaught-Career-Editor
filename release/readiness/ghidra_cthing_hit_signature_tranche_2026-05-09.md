# Ghidra CThing Hit Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra name/signature/comment evidence, not final type/source/runtime proof

## Objective

Continue the saved-Ghidra static re-audit by revisiting two older CThing hit helper labels that used misleading `DamageMask` wording. This pass corrects the saved names for those two helpers, hardens the hit-dispatch and thing-reference helper signatures that affect their decompile shape, and saves proof-boundary comments without claiming full class or collision-report layouts.

## Inputs

- Targets:
  - `0x00403ba0` `CThing__Hit_TriggerDieOnUnitOrTypeMask02100000`
  - `0x00403bf0` `CThing__Hit_TriggerDieOnTypeMask00100000`
  - `0x004fcc30` `CThing__CreateHitRefEvaluateImpulseAndDispatchHit`
  - `0x004e6640` `CThing__CreateThingRefWithSquad`
- Raw evidence root: `subagents/ghidra-static-reaudit/cthing-hit-signature-tranche/current/`
- Signature script: `tools/ApplyCThingHitSignatureTranche.java`
- Probe: `tools/ghidra_cthing_hit_signature_tranche_probe.py`
- Probe test: `tools/ghidra_cthing_hit_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_cthing_hit_signature_tranche_probe_test.py
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\cthing-hit-signature-tranche\current\rename_map_cthing_hit_signature_tranche.txt
cmd.exe /c npm run test:ghidra-cthing-hit-signature-tranche
py -3 -m py_compile tools\ghidra_cthing_hit_signature_tranche_probe.py tools\ghidra_cthing_hit_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata, decompile, xref, and instruction exports captured the selected CThing hit helper cluster.
- Headless rename dry/apply corrected `0x00403ba0` and `0x00403bf0` away from stale `DamageMask` names to type-bit helper labels.
- Headless signature dry/apply hardened all four selected targets.
- Headless comment dry/apply saved proof-boundary comments for all four targets.
- Metadata, decompile, xref, instruction, and quality-snapshot read-back verified the saved project state.

## Result

```text
CThing hit signature tranche: PASS
Targets: 4
Renamed targets: 2
Signature-hardened targets: 4
Commented targets: 4
Stale token hits: 0
Comment overclaims: 0
Xref rows: 36
Instruction rows: 324
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00403ba0` | `void __thiscall CThing__Hit_TriggerDieOnUnitOrTypeMask02100000(void * this, void * otherThing, void * collisionReport)` |
| `0x00403bf0` | `void __thiscall CThing__Hit_TriggerDieOnTypeMask00100000(void * this, void * otherThing, void * collisionReport)` |
| `0x004fcc30` | `void __thiscall CThing__CreateHitRefEvaluateImpulseAndDispatchHit(void * this, void * otherThing, void * collisionReport)` |
| `0x004e6640` | `void __thiscall CThing__CreateThingRefWithSquad(void * this, void * ownerThing, void * otherThing)` |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `430`
- Commentless functions: `5436`
- Undefined signatures: `2076`
- `param_N` signatures: `2521`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The saved Ghidra project no longer carries the stale `CThing__Hit_TriggerDieOnDamageMaskA` or `CThing__Hit_TriggerDieOnDamageMaskB` names.
- The checked hit helpers now use `otherThing` and `collisionReport` parameter names that match the current hit-dispatch shape and source-parity call form.
- `0x00403ba0` is now documented as a CThing hit helper variant gated by other-thing type bits `0x10` or `0x02100000`.
- `0x00403bf0` is now documented as a CThing hit helper variant gated by other-thing type bit `0x00100000`.
- `0x004fcc30` is now documented as the shared hit dispatcher that evaluates collision-report impulse context and dispatches into `CComplexThing__Hit`.
- `0x004e6640` now has a saved two-stack-argument `ownerThing` / `otherThing` helper signature.

## What This Does Not Prove

- This does not prove concrete `CThing`, referred-object, or `CCollisionReport` layouts.
- This does not prove exact retail type-bit labels or exact class-owner boundaries beyond the saved helper names.
- This does not add Ghidra tags, recover local variable names, or create structure types.
- This does not prove runtime collision, hit, death, or script-callback behavior.
- This does not prove exact Stuart-source method identity or rebuild parity.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.

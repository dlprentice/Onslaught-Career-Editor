# Ghidra Spline/ByteSprite Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra signature/comment evidence, not final type/source/runtime proof

## Objective

Continue the post-name-confidence signature-debt phase with a narrow CBSpline/CByteSprite tranche. This pass hardens only the targets whose current retail decompile and instruction read-back supported a conservative signature, and leaves two suspicious or thunk-like entries deferred with saved proof-boundary comments.

2026-05-10 follow-up: `release/readiness/ghidra_building_bytesprite_animation_signature_correction_2026-05-10.md` supersedes the older CByteSprite owner labels at `0x004183d0` and `0x00418430`; those entries are now saved as CBuildingNamedMesh functions. The CBSpline and `CByteSprite__Free` evidence in this note remains historical context.

## Inputs

- Hardened targets:
  - `0x00416d10` `CBSpline__ctor`
  - `0x00416da0` `CBSpline__dtor`
  - `0x00418430` `CByteSprite__scalar_deleting_dtor`
  - `0x00418480` `CByteSprite__Free`
- Deferred targets:
  - `0x00405d80` `CParticleManager__RemoveFromGlobalList`
  - `0x004183d0` `CByteSprite__dtor_base`
- Raw evidence root: `subagents/ghidra-static-reaudit/signature-debt-tranche3/current/`
- Signature script: `tools/ApplySplineByteSpriteSignatureTranche.java`
- Probe: `tools/ghidra_spline_bytesprite_signature_tranche_probe.py`
- Probe test: `tools/ghidra_spline_bytesprite_signature_tranche_probe_test.py`

## Commands

Focused validation:

```powershell
py -3 tools\ghidra_spline_bytesprite_signature_tranche_probe_test.py
py -3 tools\ghidra_spline_bytesprite_signature_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_spline_bytesprite_signature_tranche_probe.py tools\ghidra_spline_bytesprite_signature_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-spline-bytesprite-signature-tranche
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Mutation/read-back summary:

- Read-only metadata/decompile/xref/instruction exports captured all six selected targets before mutation.
- Headless signature dry/apply hardened four targets and intentionally skipped the two deferred targets.
- Headless comment dry/apply saved proof-boundary comments for all six targets.
- Metadata/decompile read-back verified the saved signatures/comments.
- The focused probe checked signature/comment boundaries, decompile tokens, xref rows, and raw instruction-address tokens without treating symbol names as instruction operands.

## Result

```text
Ghidra Spline/ByteSprite signature tranche probe
Status: PASS
Targets: 6
Hardened targets: 4
Deferred targets: 2
Xref rows: 51
Instruction rows: 246
```

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00416d10` | `void * __thiscall CBSpline__ctor(void * this, void * controlPoints, int order)` |
| `0x00416da0` | `void * __thiscall CBSpline__dtor(void * this, byte flags)` |
| `0x00418430` | `void * __thiscall CByteSprite__scalar_deleting_dtor(void * this, byte flags)` |
| `0x00418480` | `void __fastcall CByteSprite__Free(void * this)` |

Deferred entries:

| Address | Deferred reason |
| --- | --- |
| `0x00405d80` | Instruction read-back shows this saved entry as a jump thunk to `0x004cb050`; the real target signature and source/runtime identity remain separate work. |
| `0x004183d0` | The current body resets vtable-like fields and jumps/calls into an actor cleanup/constructor-like helper, so the existing `CByteSprite__dtor_base` label remains suspicious rather than signature-ready. |

Queue refresh after this pass:

- Total functions: `5866`
- Commented functions: `384`
- Commentless functions: `5482`
- Undefined signatures: `2079`
- `param_N` signatures: `2564`
- Uncertain owner names: `0`
- Address-suffixed helper names: `0`
- Address-suffixed wrapper names: `0`

## What This Proves

- The four selected CBSpline/CByteSprite targets no longer have stale `undefined ... (void)` signatures in the saved Ghidra project.
- The CBSpline constructor/destructor now carry explicit object-pointer and argument/flag shapes matching the checked decompile evidence.
- The CByteSprite scalar deleting destructor and free helper now carry explicit object-pointer, deletion-flag, and return/void shapes matching the checked decompile evidence.
- The two deferred targets now have saved comments that warn future waves not to treat the current names as complete.

## What This Does Not Prove

- This does not prove concrete CBSpline or CByteSprite class layout.
- This does not prove exact source method identity.
- This does not correct the deferred particle-manager thunk target signature.
- This does not settle the suspicious `CByteSprite__dtor_base` name or source identity.
- This does not add Ghidra tags or local-variable names.
- This does not prove runtime spline, sprite, particle, or rendering behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not close the broader signature/comment/type/tag/local/structure debt.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, signatures, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.

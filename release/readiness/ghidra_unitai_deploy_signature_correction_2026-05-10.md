# Ghidra UnitAI Deploy Signature Correction - 2026-05-10

## Summary

Wave 311 completed a saved Ghidra name/signature/comment correction tranche for `5` CUnitAI deploy/lifecycle queue targets.

The tranche corrected `0x00415140` from the address-suffixed label `CUnitAI__HandleLandedStateTransition_00415140` to `CUnitAI__HandleLandedStateTransition`, and hardened four adjacent deploy/undeploy animation helper signatures/comments.

## Corrected Targets

| Address | Saved signature |
| --- | --- |
| `0x00415140` | `void __fastcall CUnitAI__HandleLandedStateTransition(void * unitAI)` |
| `0x00415780` | `void __fastcall CUnitAI__PlayDeployingAnimationIfState0(void * unitAI)` |
| `0x004157c0` | `void __fastcall CUnitAI__PlayUndeployingAnimation(void * unitAI)` |
| `0x00415970` | `int __fastcall CUnitAI__HandleDeployUndeployAnimationCompletion(void * unitAI)` |
| `0x00415a50` | `int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void * unitAI)` |

## Validation

- Headless correction dry run: `updated=0 skipped=5 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=5 skipped=0 renamed=1 missing=0 bad=0`.
- Metadata read-back: `5/5` targets found.
- Decompile read-back: `5/5` targets dumped.
- Xref read-back: `5` rows.
- Instruction read-back: `445` rows.
- Focused probe: `PASS targets=5 renamed=1 failures=0`.
- Whole-database queue snapshot: `5868` functions, `613` commented functions, `5255` commentless functions, `2065` undefined signatures, and `2353` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove exact source identity, concrete CUnitAI layout, animation-table structure, runtime deploy/undeploy AI behavior, tag/local/type recovery, BEA launch behavior, game patching, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.

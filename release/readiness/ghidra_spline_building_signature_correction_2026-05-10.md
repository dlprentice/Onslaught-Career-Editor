# Ghidra CBSpline/Building Signature Correction - 2026-05-10

## Summary

Wave 313 completed a saved Ghidra name/signature/comment correction tranche for `9` CBSpline, Building, RepairPadAI, and render-helper queue targets.

The tranche corrected four stale lifecycle labels and hardened five existing names with concrete stack-argument signatures:

- `0x00416e30` is now `float __thiscall CBSpline__BasisFunction(void * this, int basisIndex, int order, float t)`.
- `0x00416fc0` is now `void __thiscall CBSpline__GetPoint(void * this, float * outPoint, float t)`.
- `0x00417390` is now `void __thiscall CBuilding__CreateRepairPadAI(void * this, void * init)`.
- `0x00417480` is now `CRepairPadAI__scalar_deleting_dtor`.
- `0x004174a0` is now `CRepairPadAI__dtor_body_004174a0`.
- `0x00417540` now has a one-stack-argument render-wrapper signature.
- `0x00417590` is now `CBuilding__dtor_body_00417590`.
- `0x004176a0` is now `CBuilding__scalar_deleting_dtor`.
- `0x004176c0` now has a one-stack-argument render-init signature.

## Validation

- Headless correction dry run: `updated=0 skipped=9 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=9 skipped=0 renamed=4 missing=0 bad=0`.
- Metadata read-back: `9/9` targets found.
- Decompile read-back: `9/9` targets dumped.
- Xref read-back: `15` rows.
- Instruction read-back: `855` rows.
- Focused probe: `PASS targets=9 renamed=4 failures=0`.
- Whole-database queue snapshot: `5868` functions, `627` commented functions, `5241` commentless functions, `2062` undefined signatures, and `2342` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove concrete CBSpline, CBuilding, CRepairPadAI, CThing, or render-object layouts; exact source identity; tag/local/type recovery; runtime camera/path/building/repair/render behavior; BEA launch behavior; game patching; or rebuild parity.

Stuart's source snapshot did not contain matching CBSpline/Building source files in the tracked reference tree during this pass, so the proof is based on retail Ghidra read-back, debug-path/string/xref context, and instruction/decompile evidence.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.

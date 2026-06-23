# Ghidra Building / ByteSprite Animation Signature Correction - 2026-05-10

## Summary

Wave 314 completed a saved Ghidra owner/name/signature/comment correction tranche for `14` Building, CBuildingNamedMesh, and CByteSprite animation/sprite targets.

The tranche corrected six stale owner labels:

- `0x00417870` is now `CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward`.
- `0x004178a0` is now `CBuilding__ProcessClosingAndUnshuttingAnimations`, superseding the older CUnit owner label.
- `0x00418120` is now `CBuilding__AdvanceOpenCloseAnimationState`, superseding the older CCockpit owner label.
- `0x004183d0` is now `CBuildingNamedMesh__dtor_base`, superseding the older CByteSprite deferral.
- `0x00418430` is now `CBuildingNamedMesh__scalar_deleting_dtor`, superseding the older CByteSprite scalar-deleting destructor label.
- `0x00418450` is now `CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh`, superseding the older CByteSprite vfunc label.

The tranche also hardened true CByteSprite signatures for init, load, target setup, RLE draw helpers, frame dispatch, and frame encoding from `0x00418470` through `0x004189f0`.

## Validation

- Headless correction dry run: `updated=0 skipped=14 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=14 skipped=0 renamed=6 missing=0 bad=0`.
- Metadata read-back: `14/14` targets found.
- Decompile read-back: `14/14` targets dumped.
- Xref read-back: `19` rows.
- Instruction read-back: `1358` rows.
- Caller read-back: `CDXCompass__Init` still reaches `CByteSprite__Init`, `CByteSprite__Load`, and `CByteSprite__SetTarget` with the compass `16x16`, `20` frame, `0x200` target context.
- Focused probe: `PASS`, `14` targets, `6` renamed targets, `0` failures.
- Whole-database queue snapshot: `5868` functions, `639` commented functions, `5229` commentless functions, `2052` undefined signatures, and `2339` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove exact Stuart-source method identities, concrete Building/CBuildingNamedMesh/CByteSprite class layouts, local-variable names, Ghidra tags, structure types, runtime building animation, named-mesh behavior, compass rendering, sprite palette/transparency behavior, BEA launch behavior, game patching, or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.

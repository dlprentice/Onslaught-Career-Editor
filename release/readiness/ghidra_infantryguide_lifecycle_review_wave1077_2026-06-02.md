# Ghidra InfantryGuide Lifecycle Review Wave1077 Readiness Note

Status: complete static mutation/read-back evidence
Date: 2026-06-02
Scope: `infantryguide-lifecycle-review-wave1077`

Wave1077 re-audited the CInfantryGuide / CGroundVehicleGuide guide-family vtable surface after Wave417 and recovered six previously unresolved guide-slot function boundaries. The pass created six function objects, saved conservative names/signatures/comments/tags, and made no executable-byte change, BEA launch, runtime/game-file mutation, or installed-game mutation.

Recovered boundaries:

| Address | Evidence |
| --- | --- |
| `0x0047d750 CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750` | CGroundVehicleGuide vtable `0x005dbd90` slot `3` at `0x005dbd9c` DATA-xrefs this large guidance/update body. |
| `0x0047e2d0 SharedGuide__VFunc04_SetVectorMode1_0047e2d0` | CInfantryGuide vtable `0x005dbfa8` slot `4` at `0x005dbfb8` and CGroundVehicleGuide vtable `0x005dbd90` slot `4` at `0x005dbda0` point here; body copies four raw vector lanes and returns with `RET 0x14`. |
| `0x0047e310 SharedGuide__VFunc05_SetVectorMode2_0047e310` | Shared slot `5` target for `0x005dbfbc` and `0x005dbda4`; body sets guide state mode `2`, copies four raw lanes, and returns with `RET 0x10`. |
| `0x0047e340 SharedGuide__VFunc06_SetVectorMode3_0047e340` | Shared slot `6` target for `0x005dbfc0` and `0x005dbda8`; body sets guide state mode `3`, copies four raw lanes, and returns with `RET 0x10`. |
| `0x0047e370 SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370` | Shared slot `7` target for `0x005dbfc4` and `0x005dbdac`; body checks owner state at `owner+0x13c/+0x20` and `owner+0x140/+0x94`, then copies four raw lanes. |
| `0x0047e3d0 SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0` | Shared slot `8` target for `0x005dbfc8` and `0x005dbdb0`; body copies owner lanes from `owner+0x1c` into the guide vector block and clears `owner+0x14c` lanes. |

Read-back evidence:

- Initial CInfantryGuide target exports verified `7` metadata rows, `7` tag rows, `9` xref rows, `830` function-body instruction rows, and `7` decompile rows.
- Context exports verified `18` metadata rows, `20` xref rows, `1969` function-body instruction rows, and `18` decompile rows.
- Pre-mutation vtable export verified `32` rows and showed the unresolved CInfantryGuide slots `4` through `8` plus CGroundVehicleGuide slot `3` as `NO_FUNCTION_AT_POINTER`.
- Raw unresolved-slot instruction exports verified `546` around-address instruction rows plus `526` wide rows for `0x0047d750`.
- Apply dry: `updated=6 skipped=0 created=0 would_create=6 renamed=0 would_rename=0 signature_updated=6 comment_updated=6 tag_updated=6 missing=0 bad=0`.
- Apply: `updated=6 skipped=0 created=6 would_create=0 renamed=0 would_rename=0 signature_updated=6 comment_updated=6 tag_updated=6 missing=0 bad=0`.
- Final dry: `updated=0 skipped=6 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0`.
- Post exports verified `6` metadata rows, `6` tag rows, `90` xref rows, `807` function-body instruction rows, `6` decompile rows, and `32` post vtable-slot rows.
- Post vtable export now resolves CInfantryGuide `0x005dbfa8` slots `4` through `8` and CGroundVehicleGuide `0x005dbd90` slots `3` through `8` to saved function entries.
- Queue closure is now `6260/6260 = 100.00%`, with `0` commentless functions, `0` exact-undefined signatures, `0` `param_N` signatures, `0` uncertain-owner names, and `0` legacy weak names.
- Wave911 focused re-audit progress remains `812/1408 = 57.67%`.
- Expanded static surface progress advances to `1371/1560 = 87.88%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260602-073929_post_wave1077_infantryguide_lifecycle_review_verified`, `19` files, `174754695` bytes, `DiffCount=0`.

What this proves:

- The loaded Ghidra project now has saved function objects for the six Wave1077 guide-family vtable targets.
- The saved names, signatures, comments, and tags read back for all six functions.
- The recovered shared guide slots are tied to the CInfantryGuide and CGroundVehicleGuide vtables through DATA xrefs.
- The function-quality export remains closed at 100% after the saved boundaries expanded the function-object surface.

What remains separate proof:

- Exact source method names.
- Concrete guide/vector/class layouts.
- Runtime InfantryGuide or GroundVehicleGuide targeting/movement behavior.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.

Next candidate note: continue read-only first from the remaining expanded static re-audit surface, with particular attention to other guide-family vtable gaps such as TerrainGuide slots if fresh evidence supports boundary recovery.

Probe token anchor: Wave1077; infantryguide-lifecycle-review-wave1077; 0x0047d750 CGroundVehicleGuide__VFunc03_UpdateGuidanceState_0047d750; 0x0047e2d0 SharedGuide__VFunc04_SetVectorMode1_0047e2d0; 0x0047e310 SharedGuide__VFunc05_SetVectorMode2_0047e310; 0x0047e340 SharedGuide__VFunc06_SetVectorMode3_0047e340; 0x0047e370 SharedGuide__VFunc07_SetVectorModeFromOwnerState_0047e370; 0x0047e3d0 SharedGuide__VFunc08_ResetVectorsFromOwner_0047e3d0; 0x005dbfa8; 0x005dbd90; 812/1408 = 57.67%; 1371/1560 = 87.88%; 500/500 = 100.00%; 6260/6260 = 100.00%; G:\GhidraBackups\BEA_20260602-073929_post_wave1077_infantryguide_lifecycle_review_verified; boundary recovery.

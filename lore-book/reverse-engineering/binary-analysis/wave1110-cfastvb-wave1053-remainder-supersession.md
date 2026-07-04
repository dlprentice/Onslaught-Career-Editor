# Wave1110 CFastVB Wave1053 Remainder Supersession

Status: complete static supersession accounting
Last updated: 2026-06-04
Scope: `wave1110-cfastvb-wave1053-remainder-supersession`

Wave1110 closes the remaining nine Wave1053 CFastVB rows that still appeared in the Wave1108 current focused denominator. This is no new Ghidra export, no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1110 current focused supersession accounting | `24/1179 = 2.04%` |

## Superseded Remainder Rows

These 9 rows are the remaining Wave1053 rows still present in the Wave1108 current focused candidate list after Wave1109 closed the first fifteen. Wave1053 (`cfastvb-stacklocked-transform-review-wave1053`) already re-read them with metadata, tags, xrefs, instructions, decompile, context exports, and backup evidence.

| Address | Name | Prior evidence |
| --- | --- | --- |
| `0x0059f857` | `CFastVB__DispatchOp_TransformVec4Batch_0059f857` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x0059fa5d` | `CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x0059fbeb` | `CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x0059fd51` | `CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x0059fe61` | `CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a009f` | `CFastVB__DispatchOp_TransformVec3WBatch_005a009f` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a026f` | `CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a04a0` | `CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0` | Wave1053 metadata/tag/xref/decompile read-back |
| `0x005a7617` | `CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` | Wave1053 metadata/tag/xref/decompile read-back |

Wave1053 verified `24` metadata rows, `24` tag rows, `34` xref rows, `4682` instruction rows, `24` decompile rows, `12` context metadata rows, `12` context tag rows, `49` context xref rows, `949` context instruction rows, and `12` context decompile rows. Verified Wave1053 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`.

Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Probe token anchor: Wave1110; wave1110-cfastvb-wave1053-remainder-supersession; 24/1179 = 2.04%; 9 rows; current focused candidates: 1179; Wave1053; cfastvb-stacklocked-transform-review-wave1053; 0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857; 0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles; [maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified; no new Ghidra export; no mutation.

## Boundary

This wave closes current-risk accounting for these nine rows only. It does not prove runtime math/render correctness, hidden ABI completeness, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

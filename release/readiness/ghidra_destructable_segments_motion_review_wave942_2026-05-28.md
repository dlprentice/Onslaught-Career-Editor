# Ghidra Destructable-Segments Motion Review Wave942 Readiness

Status: complete comment-only static read-back
Date: 2026-05-28
Scope: `destructable-segments-motion-review-wave942`

Wave942 re-reviewed the destructable-segments motion-controller cluster selected from the Wave911 risk-ranked continuation queue after Composer 2.5 consults and fresh serialized Ghidra exports. The pass normalized saved comments/tags for six already named functions around the destructable-segments motion controller and the adjacent CMCHiveBoss motion-controller bridge.

The mutation was comment/tag only. It made no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x00494c60` | `CDestructableSegmentsMotionController__Ctor` | `RET 0x4` confirms one explicit `segment_controller` stack argument after `this`; `CMCHiveBoss__Constructor` calls it at `0x0049709f` with `owner_hiveboss+0x178`; the nested destructable-segments motion table is `0x005dc27c`. |
| `0x00494ca0` | `CDestructableSegmentsMotionController__ScalarDeletingDestructor` | `RET 0x4`; vtable `0x005dc27c` slot `1`; calls `CDestructableSegmentsMotionController__Destructor` and conditionally frees `this` on delete flag bit 0. |
| `0x00494cc0` | `CDestructableSegmentsMotionController__Destructor` | Restores vtable `0x005dc27c`, clears `+0x08/+0x0c`, and is reached by the scalar-deleting destructor and the one-instruction JMP thunk at `0x00497130`. |
| `0x00494ce0` | `CDestructableSegmentsMotionController__ApplyRumbleTransform` | `RET 0x10`; vtable `0x005dc27c` slot `4`; calls `CMCBuggy__GetTargetValueOrFallback` and is called from `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0` at `0x00497711`. |
| `0x00497130` | `CDestructableSegmentsMotionController__DestructorThunk_00497130` | One-instruction `JMP 0x00494cc0`; caller `0x00497113` is inside `CMCHiveBoss__ScalarDeletingDestructor`. |
| `0x00497140` | `CDestructableSegmentsMotionController__CacheNamedCollisionCylinders` | `RET 0x4`; walks mesh/model count `+0x15c` and pointer table `+0x160`, caches N/S/E/W mid/top/bot in/out cylinder tokens, and is called at `0x004976f1` inside `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`, not a missing-boundary callsite. |

Context anchors:

- `0x00443fc0 CDestructableSegmentsController__Ctor`
- `0x00444660 CDestructableSegmentsController__Init`
- `0x00445010 CMCBuggy__GetTargetValueOrFallback`
- `0x0047fe30 CHiveBoss__Init`
- `0x00497090 CMCHiveBoss__Constructor`
- `0x00497110 CMCHiveBoss__ScalarDeletingDestructor`
- `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`
- Vtable anchors `0x005dc27c` and `0x005dc388`

Fresh read-back evidence:

- Pre primary exports: 6 metadata rows, 6 tag rows, 8 xref rows, 826 instruction rows, and 6 decompile rows.
- Context exports: 9 metadata rows, 9 tag rows, 10 xref rows, 1371 instruction rows, and 9 decompile rows.
- Vtable export: 24 rows across `0x005dc27c` and `0x005dc388`.
- `ApplyDestructableSegmentsMotionReviewWave942.java dry`: `SUMMARY updated=0 would_update=6 skipped=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyDestructableSegmentsMotionReviewWave942.java apply`: `SUMMARY updated=6 would_update=0 skipped=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyDestructableSegmentsMotionReviewWave942.java final dry`: `SUMMARY updated=0 would_update=0 skipped=6 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post primary exports: 6 metadata rows, 6 tag rows, 8 xref rows, 826 instruction rows, and 6 decompile rows.
- Post vtable export: 24 rows across `0x005dc27c` and `0x005dc388`.
- Queue refresh remains `6113` total functions, `6113` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`, 19 files, 173280135 bytes, `DiffCount=0`.

Progress:

- Wave911 focused re-audit progress after Wave942: `180/1408 = 12.78%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave942; `destructable-segments-motion-review-wave942`; comment-only mutation; `0x00494c60 CDestructableSegmentsMotionController__Ctor`; `0x00494ca0 CDestructableSegmentsMotionController__ScalarDeletingDestructor`; `0x00494cc0 CDestructableSegmentsMotionController__Destructor`; `0x00494ce0 CDestructableSegmentsMotionController__ApplyRumbleTransform`; `0x00497130 CDestructableSegmentsMotionController__DestructorThunk_00497130`; `0x00497140 CDestructableSegmentsMotionController__CacheNamedCollisionCylinders`; `0x00497090 CMCHiveBoss__Constructor`; `0x00497110 CMCHiveBoss__ScalarDeletingDestructor`; `0x004976d0 CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`; `0x004976f1`; `0x005dc27c`; `0x005dc388`; `180/1408 = 12.78%`; `6113/6113 = 100.00%`; `G:\GhidraBackups\BEA_20260528-040608_post_wave942_destructable_segments_motion_review_verified`.

What this proves:

- The six selected destructable-segments motion-controller rows remain present in the saved Ghidra project with coherent names, signatures, xrefs, instructions, vtable anchors, and decompile outputs.
- Stale comment wording from Waves 430-431 was normalized against later Wave432/Wave921 evidence: `0x00497090` is `CMCHiveBoss__Constructor`, `0x00497110` is `CMCHiveBoss__ScalarDeletingDestructor`, and the `0x004976f1` call belongs to `CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0`.
- `0x00497130` is preserved as a one-instruction JMP thunk to the canonical destructor body at `0x00494cc0`.

What remains unproven:

- Runtime HiveBoss rumble/cylinder behavior.
- Exact destructable-segments motion-controller and CMCHiveBoss object layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.

# Wave1131 HeightField Current-Risk Review

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1131-heightfield-current-risk-review`

Wave1131 accounts for `7 rows` from the Wave1108 current focused continuity denominator as a HeightField MAP current-risk cluster. This wave uses fresh Ghidra export evidence plus narrow tag-only normalization. Current focused accounting moves to `168/1179 = 14.25%` of the continuity denominator. The current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 1011. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x0047e870 CHeightField__ResetCoreBuffersAndFlags` | `CHeightField__Constructor` calls this reset helper at `0x00490e13`; saved comment preserves the Wave426 owner correction from stale `CUnitAI` wording and the `+0x20/+0x24/+0x1028` buffer reset evidence. |
| `0x0047e8a0 CHeightField__FreeOwnedBuffers_24_1028` | Called by `CHeightField__FreeOwnedBuffers_Thunk` and `CHeightField__ShutdownAndDestroyMixerMap`; frees `+0x24` and `+0x1028` through `OID__FreeObject`. |
| `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange` | Called by `CDXBattleLine__BuildMesh` and `CDXBattleLine__UpdateHeightmap`; saved Wave396 evidence keeps HeightField ownership while preserving battle-line caller context. |
| `0x00490e20 CHeightField__FreeOwnedBuffers_Thunk` | `0x00490a35` no-function callsite tail-calls the owned-buffer free helper as the global MAP destructor thunk. |
| `0x00490f10 CHeightField__InitAndClearMapLoadFlags` | Called by `CGame__Init`; clears the map-load flags at `+0x93e0/+0x93e4` after initializing the map/heightfield context. |
| `0x00490f40 CHeightField__ShutdownAndDestroyMixerMap` | Called by `CGame__Shutdown`; calls `CHeightField__FreeOwnedBuffers_24_1028` and tail-calls `CMixerMap__Destroy`. |
| `0x00490f50 CHeightField__TraceMapLoadRequestAndCheckLoadedFlags` | Called by `CWorld__LoadWorld`; `RET 0xc` confirms three stack arguments and the body traces `Loading map %d` before checking `+0x93e0/+0x93e4`. |

Context rows re-read: `0x00490e10 CHeightField__Constructor`, `0x00490e30 CHeightField__BuildCellMinMaxHeightTable`, `0x00491060 CHeightField__DeserializeMapAndInitResources`, `0x0047f750 CHeightField__Load`, `0x0047ea20 CHeightField__GetHeightSamplePacked16`, `0x0047eb00 CHeightField__SampleInterpolatedHeight`, and `0x00490a40 CHeightField__TraceLineAgainstHeightfield`.

Mutation status:

- Tag-only normalization.
- `40 tags` added.
- No rename.
- No signature change.
- No comment change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `7` / `7` / `9` / `220` / `7`.
- Context metadata/tag/xref/instruction/decompile exports: `7` / `7` / `30` / `703` / `7`.
- `ApplyHeightfieldCurrentRiskWave1131.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0`.
- `ApplyHeightfieldCurrentRiskWave1131.java apply`: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=40 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyHeightfieldCurrentRiskWave1131.java final dry`: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `7` / `7` / `9` / `220` / `7`.
- Pre/post metadata, instruction, and xref exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `[maintainer-local-ghidra-backup-root]\BEA_20260605-090018_post_wave1131_heightfield_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-082438_post_wave1130_dive_dropship_current_risk_review_verified`.
- Codex read-only consult recommended a later Feature/Pickup candidate; root selected the earlier uncovered HeightField cluster after live covered-set analysis.

What this proves:

- The seven target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1131-heightfield-current-risk-review`, `wave1131-readback-verified`, `current-risk-review`, `heightfield-current-risk-review`, and the per-row score tags.
- The comments, xrefs, instruction windows, and decompile rows remain coherent with prior Wave396/Wave426/Wave1009 HeightField/MAP evidence.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime terrain behavior.
- Runtime map-load behavior.
- Runtime battle-line mesh behavior.
- Runtime mixer-map shutdown behavior.
- Exact source-body identity.
- Concrete `CHeightField`, MAP singleton, mixer-map, battle-line, chunk-reader, or load-flag layouts.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

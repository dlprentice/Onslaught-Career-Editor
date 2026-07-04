# Wave1159 CMeshPart Name Pose Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1159-cmeshpart-name-pose-current-risk-review`

Wave1159 accounts for `12 CMeshPart name/load/pose current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. It uses fresh Ghidra export evidence and is a read-only review with no mutation.

Probe token anchor: Wave1159; wave1159-cmeshpart-name-pose-current-risk-review; 497/1179 = 42.15%; 12 CMeshPart name/load/pose current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 33 xref rows; 1790 instruction rows; CMeshPart__LoadOldStyle_VersionA; CMeshPart__RebuildPerVertexNormalsAndTangents; CMeshPart__PopulatePoseCacheRecursive; CMeshPart__EvaluatePoseTransformForFrame; CMesh__FindPartByNameI; [maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

Fresh exports under `subagents/ghidra-static-reaudit/wave1159-cmeshpart-name-pose-current-risk-review/`:

| Artifact | Rows |
| --- | ---: |
| `pre-metadata.tsv` | 12 |
| `pre-tags.tsv` | 12 |
| `pre-xrefs.tsv` | 33 |
| `pre-instructions.tsv` | 1790 |
| `pre-decompile/index.tsv` | 12 |

All Ghidra export logs report zero missing/failed targets and no `LockException`.

Reviewed anchors:

| Address | Function | Static role |
| --- | --- | --- |
| `0x004950f0` | `CMeshPart__AnySubPartNameStartsWithCore` | Child/subpart name predicate for `CORE` token. |
| `0x004957d0` | `CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel` | Child/subpart name predicate for `turret` / `barrel` optimization gates. |
| `0x00496250` | `CMeshPart__NameDoesNotStartWithDoor` | Door-prefix exclusion predicate. |
| `0x00496270` | `CMeshPart__HasDoorOpeningOrClosingAnimation` | DoorOpening/DoorClosing animation-token predicate. |
| `0x004aa8a0` | `CMesh__FindPartByNameI` | Case-insensitive part lookup through the mesh part table. |
| `0x004aede0` | `CMeshPart__LoadOldStyle_VersionA` | Old-style mesh part loader with `RET 0x14` five-stack-argument ABI. |
| `0x004af110` | `CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | Adjacent old-style loader with extra per-count 4-byte block. |
| `0x004b0800` | `CMeshPart__ApplyRootTransformRecursive` | Recursive root transform propagation helper. |
| `0x004b1eb0` | `CMeshPart__RebuildPerVertexNormalsAndTangents` | Per-vertex normal/tangent rebuild helper. |
| `0x004b4ba0` | `CMeshPart__PopulatePoseCacheRecursive` | Recursive pose-cache population helper. |
| `0x004b4cd0` | `CMeshPart__RefreshCachedPoseIfStale` | Pose-cache stale-timestamp refresh gate. |
| `0x004b4de0` | `CMeshPart__EvaluatePoseTransformForFrame` | Seven-argument cdecl pose transform evaluator. |

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused historical residual | `596` rows, historical-retired/non-reconstructable, `300` materialized focused rows |
| Wave911 top-500 risk-ranked subset | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `497/1179 = 42.15%` |
| Current risk candidates | `6166` |
| Current focused candidates | `1178` |
| Live regenerated current focused candidates | `1178` |
| Remaining active focused work | `682` |

This is the active current-risk denominator, not Wave911 reconstruction.

## Boundary

This review proves static retail Ghidra metadata/decompile/xref/instruction evidence for the selected mesh-part rows. It does not prove runtime mesh loading, runtime pose/cache behavior, runtime render/collision behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, visual QA, or rebuild parity.

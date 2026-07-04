# Wave1159 CMeshPart Name Pose Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1159-cmeshpart-name-pose-current-risk-review`

Wave1159 re-read twelve CMeshPart/CMesh name-predicate, old-style loader, transform, normal/tangent, and pose-cache rows from the active `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra exports. The pass made no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Probe token anchor: Wave1159; wave1159-cmeshpart-name-pose-current-risk-review; 497/1179 = 42.15%; 12 CMeshPart name/load/pose current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 682; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 33 xref rows; 1790 instruction rows; CMeshPart__LoadOldStyle_VersionA; CMeshPart__RebuildPerVertexNormalsAndTangents; CMeshPart__PopulatePoseCacheRecursive; CMeshPart__EvaluatePoseTransformForFrame; CMesh__FindPartByNameI; [maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Read-back evidence:

- Exports: `12` metadata rows, `12` tag rows, `33` xref rows, `1790` instruction rows, and `12` decompile rows.
- Representative anchors: `CMeshPart__LoadOldStyle_VersionA`, `CMeshPart__RebuildPerVertexNormalsAndTangents`, `CMeshPart__PopulatePoseCacheRecursive`, `CMeshPart__EvaluatePoseTransformForFrame`, and `CMesh__FindPartByNameI`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-004711_post_wave1159_cmeshpart_name_pose_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting after Wave1159 is `497/1179 = 42.15%`; current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`; remaining active focused work: `682`; focused threshold `15`; not Wave911 reconstruction.

What this proves:

- The twelve selected CMeshPart/CMesh rows exist in the saved Ghidra project with clean signatures, comments, tags, decompile exports, body-instruction exports, and xref evidence.
- The observed static graph ties mesh-part protected-name predicates to optimization/merge gates, old-style loaders to the CMesh load path, normal/tangent rebuilds to loader/transform paths, and pose-cache helpers to animation/collision/render callers.

What remains separate:

- Runtime mesh loading, animation, pose-cache, collision, or render behavior.
- Exact concrete `CMesh`, `CMeshPart`, material, DVertex/PVertex, pose-cache, controller, animation, and transform layouts.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Clean-room rebuild parity.

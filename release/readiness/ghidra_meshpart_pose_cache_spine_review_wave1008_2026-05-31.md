# Ghidra MeshPart Pose Cache Spine Review Wave1008 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `meshpart-pose-cache-spine-review-wave1008`

Wave1008 re-read the Wave817 MeshPart pose/cache spine as a post-Wave1007 static re-audit slice. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive` | Scalarized `RET 0x50` aggregate-stack pose-cache population helper; calls `CMeshPart__EvaluateAnimatedTransformCore`, copies the 12-dword transform and anchor/cache payload into pose-cache rows, and recurses through child count/table `+0x90/+0x94`. Direct xrefs remain the self-recursive call at `0x004b4ca1` and refresh caller `0x004b4dbc`. |
| `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale` | `RET 0x10` refresh gate using `DAT_008a9aac`, force-refresh state, pose-controller vtable callbacks, root matrix `DAT_00704db8`, first parent part from `mesh_context+0x160`, and the `0x004b4dbc` call into `CMeshPart__PopulatePoseCacheRecursive`. |
| `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame` | Seven-argument cdecl evaluator with callsites `0x00445130`, `0x004ad70a`, raw site `0x004dd1cf`, and raw site `0x004dede9`, each pushing seven dwords and cleaning with `ADD ESP, 0x1c`. It writes default anchor/transform outputs from `DAT_00704de8` and `DAT_00704db8`, calls the refresh/wrapped-frame/CMCMech paths, and can apply controller callbacks through `Vec3__SetXYZ` and `Mat34__SetRows`. |
| Context rows | `0x004b0d00 CMeshPart__InterpolateSegmentTransform`, `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`, `0x004b24d0 CMeshPart__ResolveWrappedFrameIndexAndLerp`, `0x004b5330 CMeshPart__EvaluateAnimatedTransformCore`, `0x00401ec0 Vec3__SetXYZ`, and `0x00401f10 Mat34__SetRows` still bracket the pose/interpolation/cache path. |

Read-back evidence:

- Target exports: 3 metadata rows, 3 tag rows, 8 xref rows, 467 body-instruction rows, and 3 decompile rows.
- Context exports: 6 metadata rows, 708 xref rows, 1622 body-instruction rows, and 6 decompile rows.
- Callsite export: 105 instruction rows across `0x00445130`, `0x004ad70a`, `0x004b4dbc`, `0x004dd1cf`, and `0x004dede9`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-150639_post_wave1008_meshpart_pose_cache_spine_review_verified`, 19 files, 173869959 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6223/6223 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress remains `499/1408 = 35.44%` because these rows are not Wave911 focused-candidate rows.
- Expanded static surface progress advances to `679/1478 = 45.94%`.
- Wave911 top-500 risk-ranked coverage remains `398/500 = 79.60%` because these rows are outside the Wave911 top-500 risk-ranked set.

What this proves:

- The saved Wave817 MeshPart pose/cache names, signatures, comments, and tags still match fresh static Ghidra metadata, tag, xref, instruction, decompile, and backup evidence.
- The three-row pose-cache spine remains coherently connected to the interpolation/cache context helpers and observed callsites listed above.
- No fresh evidence justified a Wave1008 rename, signature change, comment/tag mutation, boundary change, or executable-byte change.

What remains unproven:

- Runtime animation, collision, render, or cache behavior.
- Exact aggregate C types or source-level argument structures.
- Concrete MeshPart, pose-cache, mesh-context, or pose-controller layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.

# Ghidra MeshPart Pose Cache Wave817 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `meshpart-pose-cache-wave817`

Wave817 meshpart pose cache saved comments/tags/signatures for three adjacent MeshPart pose/cache rows from `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive` through `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame`. The pass corrected three stale locked no-argument signatures to observed ABI forms, made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive` | Recursive pose-cache population body. The saved signature scalarizes the observed `RET 0x50` aggregate-stack payload. The body calls `CMeshPart__EvaluateAnimatedTransformCore`, writes a 12-dword transform to the cache slot indexed by `mesh_part+0x88`, writes the anchor vec4 to the companion cache, stores scalar/cache values through the cache arrays, and recurses over children from `mesh_part+0x90/+0x94`. |
| `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale` | Cache timestamp gate using `DAT_008a9aac`, `this+0x14`, and `force_refresh`; callers push four stack dwords and the callee exits with `RET 0x10`. The body uses pose-controller vtable slots `+0x70/+0x1c/+0x18/+0x20`, seeds the root matrix from `DAT_00704db8`, calls `CMeshPart__PopulatePoseCacheRecursive` at `0x004b4dbc`, then restores `this+0x14` and writes `this+0x18`. |
| `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame` | Four observed callsites (`0x00445130`, `0x004ad70a`, `0x004dd1cf`, `0x004dede9`) push seven dwords and clean with `ADD ESP, 0x1c`. The body initializes default anchor/transform from `DAT_00704de8` and `DAT_00704db8`, chooses cached-pose refresh/copy or wrapped-frame interpolation via `CMeshPart__ResolveWrappedFrameIndexAndLerp` and `CMCMech__BuildInterpolatedPoseAndAnchor`, and can apply pose-controller transform callbacks through `Vec3__SetXYZ` and `Mat34__SetRows`. |

Read-back evidence:

- `ApplyMeshPartPoseCacheWave817.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=3 missing=0 bad=0`
- `ApplyMeshPartPoseCacheWave817.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=3 missing=0 bad=0`
- `ApplyMeshPartPoseCacheWave817.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 8 xref rows, 315 target instruction rows, 735 wide instruction rows, 600 callsite instruction rows, and 3 decompile rows.
- Queue after Wave817: 6098 total, 5605 commented, 493 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5605/6098 = 91.92%`, strict clean-signature proxy `5605/6098 = 91.92%`.
- Next raw commentless row: `0x004b7d90 CGame__PumpBinkVoiceSampleQueue`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-154905_post_wave817_meshpart_pose_cache_verified`, 19 files, 171379591 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- The saved signatures, comments, and tags were written and read back from the Ghidra project.
- The observed ABI facts (`RET 0x50`, `RET 0x10`, seven cdecl stack dwords with `ADD ESP, 0x1c`) are static retail Ghidra evidence from the exported instructions/callsites.
- The saved comments explicitly preserve the aggregate/source/runtime uncertainty boundary.

What remains unproven:

- Exact source aggregate C types.
- Concrete MeshPart/cache/controller layouts.
- Exact source-body identity.
- Runtime animation/render/collision behavior.
- BEA patching behavior.
- Rebuild parity.

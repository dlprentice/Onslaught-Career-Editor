# Ghidra Wave900+ Through Wave1008 Recheck Note

Status: PASS
Date: 2026-05-31
Scope: `ghidra-wave900-plus-through-wave1008-recheck`

Wave900-Wave1008 aggregate recheck extends the Wave900+ structural evidence gate after Wave1008 MeshPart pose-cache spine review. This is structural static evidence validation for the loaded Ghidra project and repo evidence surfaces, not runtime proof, exact source-layout proof, BEA patching proof, or rebuild parity.

Wave1008 anchor: `meshpart-pose-cache-spine-review-wave1008`; `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`; `0x004b4cd0 CMeshPart__RefreshCachedPoseIfStale`; `0x004b4de0 CMeshPart__EvaluatePoseTransformForFrame`; `0x004b0d00 CMeshPart__InterpolateSegmentTransform`; `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor`; `0x004b24d0 CMeshPart__ResolveWrappedFrameIndexAndLerp`; `0x004b5330 CMeshPart__EvaluateAnimatedTransformCore`; `0x00401ec0 Vec3__SetXYZ`; `0x00401f10 Mat34__SetRows`.

Verified recheck result:

- Readiness notes: `111`
- Covered waves: `109`
- Package probe scripts: `107`
- Evidence bases: `107`
- Backup references: `109`
- Apply scripts: `33`
- Wave982-Wave1008 direct probes: `27` total, `2` current passes, `25` classified stale-current failures, `0` disallowed evidence or unclassified failures
- Current queue closure: `6223/6223 = 100.00%`
- Wave911 focused re-audit progress: `499/1408 = 35.44%`
- Expanded static surface progress: `679/1478 = 45.94%`
- Wave911 top-500 risk-ranked coverage: `398/500 = 79.60%`
- Verified Wave1008 backup: `G:\GhidraBackups\BEA_20260531-150639_post_wave1008_meshpart_pose_cache_spine_review_verified`

The direct-probe stale-current classifications are expected because older focused probes still assert historical baton/current-doc totals that have intentionally rolled forward. The aggregate gate treats those as stale-current only when the line-level classifier finds no metadata, signature, tag, decompile, log, backup, lock, or unclassified evidence mismatch.

Boundary note: Wave1008 confirms static MeshPart pose-cache spine read-back coherence for the selected rows. Runtime animation, collision, render, or cache behavior; exact aggregate C types; concrete MeshPart/cache/controller layouts; exact source-body identity; BEA patching; and rebuild parity remain separate proof.

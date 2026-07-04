# Ghidra Mesh Animation Tail Wave816 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `mesh-animation-tail-wave816`

Wave816 mesh animation tail saved comments/tags for three adjacent CMesh/CMeshPart animation rows and corrected two stale locked no-argument signatures. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004b0cd0 CMesh__SelectModeSpecificPtr` | `void * __thiscall CMesh__SelectModeSpecificPtr(void * this)` | Reads mode field `+0x8c`; modes `1` and `3` return `this`, mode `6` returns alternate pointer `+0x124`, otherwise returns null. |
| `0x004b0d00 CMeshPart__InterpolateSegmentTransform` | `void __thiscall CMeshPart__InterpolateSegmentTransform(void * this, int frame_a, int frame_b, float frame_lerp, void * out_transform_3x4, float * out_anchor_vec4)` | Sole direct callsite `0x004b17fc` pushes five stack arguments and sets `ECX` to the part; callee ends with `RET 0x14`. The body clamps frame indices against `+0xb8`, maps through byte table `+0xc4`, reads anchor records at `+0xc8` and transform rows at `+0x10c`, and writes output transform/anchor buffers. |
| `0x004b0fb0 CMCMech__BuildInterpolatedPoseAndAnchor` | `void __thiscall CMCMech__BuildInterpolatedPoseAndAnchor(void * this, int frame_a, int frame_b, int blend_step_or_flag, void * optional_pose_controller, void * out_transform_3x4, float * out_anchor_vec4, int cache_slot, int notify_callbacks, int force_recursive_path)` | Representative callsites push nine stack dwords and the body returns with `RET 0x24`. Evidence ties it to global pose cache slots `DAT_00704cf0`/`DAT_00704d20`, anchors `DAT_00704cd0`/`DAT_00704ce0`, parent part `+0x98`, frame cache pointers/counts `+0x104`/`+0x108`/`+0x118`/`+0x11c`/`+0x120`, `CMeshPart__InterpolateSegmentTransform`, and optional pose-controller vtable callbacks `+0x70`/`+0x4`/`+0xc`/`+0x10`. |

Read-back evidence:

- `ApplyMeshAnimationTailWave816.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`
- `ApplyMeshAnimationTailWave816.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`
- `ApplyMeshAnimationTailWave816.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 56 xref rows, 567 instruction rows, 3 decompile rows, and 525 representative callsite instruction rows.
- Queue after Wave816: 6098 total, 5602 commented, 496 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5602/6098 = 91.87%`, strict clean-signature proxy `5602/6098 = 91.87%`.
- Next raw commentless row: `0x004b4ba0 CMeshPart__PopulatePoseCacheRecursive`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-151844_post_wave816_mesh_animation_tail_verified`, 19 files, 171346823 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- The saved comments and tags include `mesh-animation-tail-wave816` and `wave816-readback-verified`.
- The saved signatures match the observed `__thiscall` stack cleanup for `0x004b0d00` (`RET 0x14`) and `0x004b0fb0` (`RET 0x24`).
- The observed bodies and callsites are static retail Ghidra evidence tied to xref, instruction, decompile, callsite, and read-back exports.

What remains unproven:

- Exact concrete CMesh/CMeshPart/CMCMech/controller layouts.
- Exact source-body identity.
- Runtime animation/render/collision behavior.
- Global pose-cache lifetime beyond observed static writes.
- BEA patching behavior.
- Rebuild parity.

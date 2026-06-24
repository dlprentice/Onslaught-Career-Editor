# Ghidra CMesh LegMotion Animation Wave811 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cmesh-legmotion-animation-wave811`

Wave811 CMesh LegMotion animation saved a one-row owner/name/signature/comment/tag correction for `0x0049c2d0 CMesh__HasLegMotionAnimation`, replacing stale `CMeshPart__HasAnimationToken_623074`. The pass made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x0049c2d0` | `bool __cdecl CMesh__HasLegMotionAnimation(void * mesh)` | Loads the mesh pointer from `ESP+4`, pushes string token `0x00623074` (`LegMotion`), calls `0x004aa630 CMesh__FindAnimationIndexByName`, and returns true when the lookup result is not `-1`. |
| Caller set | Existing caller metadata | `CMeshPart__CanOptimizePart_Strict` and `CMeshPart__CanMergeInOptimizePass` pass `part+0x128`; `CMesh__HasSpecialOptimizationConstraints` passes `mesh` directly. |

Read-back evidence:

- `ApplyCMeshLegMotionAnimationWave811.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCMeshLegMotionAnimationWave811.java apply`: `updated=1 skipped=0 renamed=1 would_rename=1 signature_updated=1 comment_only_updated=1 missing=0 bad=0`
- `ApplyCMeshLegMotionAnimationWave811.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 9 xref rows, 181 instruction rows, 1 decompile row, 4 caller metadata rows, and 4 caller decompile rows.
- Queue after Wave811: 6098 total, 5586 commented, 512 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5586/6098 = 91.60%`, strict clean-signature proxy `5586/6098 = 91.60%`.
- Next raw commentless row: `0x004a25c0 CLTShell__ValidateAndRollHeapDeltas`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-125806_post_wave811_cmesh_legmotion_animation_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x0049c2d0` is named `CMesh__HasLegMotionAnimation`.
- The saved signature is `bool __cdecl CMesh__HasLegMotionAnimation(void * mesh)`.
- The saved comment and tags include `cmesh-legmotion-animation-wave811` and `wave811-readback-verified`.
- Static caller evidence supports CMesh ownership: CMeshPart predicates pass `part+0x128`, while the mesh-wide predicate passes its `mesh` argument directly.

What remains unproven:

- Exact field `+0x128` meaning.
- Concrete `CMesh` / `CMeshPart` layouts.
- Runtime mesh optimization behavior.
- Runtime animation behavior.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.

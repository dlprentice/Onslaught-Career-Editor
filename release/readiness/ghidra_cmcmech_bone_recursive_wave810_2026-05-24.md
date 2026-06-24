# Ghidra CMCMech Bone Recursive Wave810 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `cmcmech-bone-recursive-wave810`

Wave810 CMCMech bone recursive saved a comment/tag-only correction for `0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive` after serialized headless dry/apply/read-back with the `cmcmech-bone-recursive-wave810` and `wave810-readback-verified` tags. The pass made no rename, no signature change, no function-boundary change, and no executable-byte change.

The row intentionally keeps the saved `void CMCMech__UpdateBoneHierarchyRecursive(void)` signature. Static instruction and callsite evidence proves a `RET 0x54` cleaned stack contract, but the payload includes by-value vector/matrix stack aggregates that should not be forced into Ghidra's normal parameter model until shared `FVector`/`FMatrix` stack-aggregate types are recovered.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive` | Body saves `ECX` as the `CMCMech` receiver, calls `CMCMech__UpdateBone`, reads child count at `mesh_part+0x90`, reads child table at `mesh_part+0x94`, recursively calls itself at `0x0049bddf`, and exits with `RET 0x54`. |
| `0x00498ac6` | `CMCMech__Reset` callsite for one reset path; prepares a `0x10` vector payload, a `0x30` matrix payload copied with `MOVSD.REP ECX=0xc`, a child mesh part, two pose-argument dwords, and two blend floats. |
| `0x00498bad` | Second `CMCMech__Reset` callsite with the same large stack-payload shape for the alternate reset path. |
| `0x0049bddf` | Recursive callsite inside `CMCMech__UpdateBoneHierarchyRecursive`; passes the descendant mesh part from `mesh_part+0x94[index]` with the same vector/matrix/pose/blend payload shape. |
| `0x00499e30 CMCMech__UpdateBone` | Existing Wave437 callee row used by the recursive helper before descending children. |

Read-back evidence:

- `ApplyCMCMechBoneRecursiveWave810.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyCMCMechBoneRecursiveWave810.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`
- `ApplyCMCMechBoneRecursiveWave810.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `1` metadata row, `1` tag row, `3` xref rows, `261` instruction rows, `1` decompile row, `201` post-callsite instruction rows, `3` caller decompile rows, `7` context decompile rows, and `12` CMCMech vtable rows.
- Queue after Wave810: `6098` total functions, `5585` commented, `513` commentless, `0` exact-undefined signatures, `0` `param_N` signatures, comment-backed proxy `5585/6098 = 91.59%`, strict comment-plus-clean-signature proxy `5585/6098 = 91.59%`.
- Next raw commentless row: `0x0049c2d0 CMeshPart__HasAnimationToken_623074`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-123030_post_wave810_cmcmech_bone_recursive_verified`, `19` files, `171314055` bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved name remains `CMCMech__UpdateBoneHierarchyRecursive`.
- The saved signature remains `void CMCMech__UpdateBoneHierarchyRecursive(void)`.
- The saved comment and tags include `cmcmech-bone-recursive-wave810` and `wave810-readback-verified`.
- The observed recursive bone-update body, callsites, `RET 0x54`, and vector/matrix stack-payload evidence are static retail Ghidra evidence.

What remains unproven:

- Exact by-value `FVector`/`FMatrix` parameter type contract.
- Concrete `CMCMech` and `CMeshPart` layouts.
- Exact source-body identity.
- Runtime leg/bone animation behavior.
- BEA patching behavior.
- Rebuild parity.

# Ghidra Vec3 Negate Wave798 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `vec3-negate-wave798`

Wave798 Vec3 negate helper corrected the raw commentless queue head `0x004404f0 CThing__NegateVec3ToOut` to the owner-neutral `0x004404f0 Vec3__NegateToOut`. The pass saved the new name, `void __thiscall Vec3__NegateToOut(void * this, void * outVec)` signature, comment, and tags. It made no function-boundary changes and no executable-byte changes.

Static anchors:

| Address | Evidence |
| --- | --- |
| `0x004404f0 Vec3__NegateToOut` | ECX is the source Vec3, the single stack argument at `[ESP+4]` is the output Vec3 pointer, X/Y/Z are loaded from `[ECX]`, `[ECX+4]`, and `[ECX+8]`, each lane is negated with `FCHS`, and the outputs are stored to `[EAX]`, `[EAX+4]`, and `[EAX+8]` before `RET 0x4`. |
| Xref context | Post export verified 11 xref rows spanning `CDXEngine__BuildDirectionalSampleRing`, `CThing__RenderDebugVolumeOverlay`, `CMCMech__UpdateBone`, `CMCBuggy__UpdateWheel`, `CCylinder__ResolveCollisionVFunc02`, `CMeshCollisionVolume__TestSweptSphereAgainstTriangleCore`, and one no-function call site at `0x004e53ac`. |

Read-back evidence:

- `ApplyVec3NegateWave798.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyVec3NegateWave798.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyVec3NegateWave798.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 11 xref rows, 65 instruction rows, and 1 decompile row.
- Queue after Wave798: 6098 total, 5546 commented, 552 commentless, 0 exact-undefined signatures, 0 param_N signatures, comment-backed proxy `5546/6098 = 90.95%`, strict clean-signature proxy `5546/6098 = 90.95%`.
- Next raw commentless row is `0x00441730 CLIParams__SetField04`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-060456_post_wave798_vec3_negate_verified`, 18 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row at `0x004404f0` has the expected `Vec3__NegateToOut` name, signature, Wave798 comment, and tags.
- The old `CThing` owner was too narrow for the observed broad math/collision/render xref set.
- The queue advanced by one comment-backed and strict-clean row while signature debt stayed at zero.

What remains unproven:

- Concrete Vec3 type/layout recovery beyond the observed three-float access pattern.
- Exact source identity.
- Runtime math, collision, or render behavior.
- BEA patching behavior.
- Rebuild parity.

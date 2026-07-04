# Ghidra MeshPart Tail Wave815 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `meshpart-tail-wave815`

Wave815 meshpart tail saved comments/tags for `0x004adf80 CMesh__ClearField08`, corrected `0x004ae640 CMeshPart__FreeOwnedResourcePointers_004ae640` to `0x004ae640 CMeshPart__FreeOwnedResourcePointers`, and corrected the old-style loader signatures for `0x004aede0 CMeshPart__LoadOldStyle_VersionA` and `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock`. The pass used the `meshpart-tail-wave815` and `wave815-readback-verified` tags, made one rename, corrected two stale locked no-argument signatures, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004adf80 CMesh__ClearField08` | `void __thiscall CMesh__ClearField08(void * this)` | Clears field `+0x08` on the 0x24-byte CMesh embedded resource/material record; `CMesh__InitStatic` calls it after allocation, and `CMesh__Load` / `CMesh__Deserialize` pass it to vector-constructor setup paired with `CMesh__ReleaseEmbeddedResources`. |
| `0x004ae640 CMeshPart__FreeOwnedResourcePointers` | `void __thiscall CMeshPart__FreeOwnedResourcePointers(void * this)` | Shared free body reached by `0x004a51f0 CMeshPart__FreeResources` tail jump and `CMeshPart__CreatePolyBucket` failure cleanup; frees observed resource fields including `+0x104`, `+0x108`, `+0x94`, `+0x134`, frame table `+0x84` count `+0xb4`, triangle pointer `+0x80`, polybucket `+0x100`, helper `+0xfc`, and vtable-owned field `+0x138`. |
| `0x004aede0 CMeshPart__LoadOldStyle_VersionA` | `int __thiscall CMeshPart__LoadOldStyle_VersionA(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)` | `CMesh__Load` callsite `0x004a8f05` sets `ECX=ESI` and pushes five stack arguments; the epilogue uses `RET 0x14`. Body evidence reads 0x60-byte records, negates loaded Z, clamps material indexes, initializes six material slots, builds triangle vertex pointers, and calls `CMeshPart__RebuildPerVertexNormalsAndTangents(this, 1)`. |
| `0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock` | `int __thiscall CMeshPart__LoadOldStyle_VersionB_WithExtraBlock(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)` | `CMesh__Load` callsite `0x004a8f49` uses the same five-stack-argument ABI and the epilogue at `0x004af462` uses `RET 0x14`. VersionB adds an extra per-count 4-byte block tied to part offset `+0xb8` before following the same transform/triangle rebuild path. |

Read-back evidence:

- `ApplyMeshPartTailWave815.java dry`: `updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- `ApplyMeshPartTailWave815.java apply`: `updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=2 comment_only_updated=4 missing=0 bad=0`
- `ApplyMeshPartTailWave815.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 8 xref rows, 420 instruction rows, 4 decompile rows, 5 caller metadata rows, 5 caller decompile rows, 344 callsite instruction rows, and 161 epilogue instruction rows.
- Queue after Wave815: 6098 total functions, 5599 commented, 499 commentless, 0 exact-undefined signatures, 0 `param_N` signatures, comment-backed proxy `5599/6098 = 91.82%`, strict clean-signature proxy `5599/6098 = 91.82%`.
- Next raw commentless row: `0x004b0cd0 CMesh__SelectModeSpecificPtr`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-144421_post_wave815_meshpart_tail_verified`, 19 files, 171346823 bytes, `DiffCount=0`.

What this proves:

- The four target rows exist in the saved Ghidra project.
- The saved metadata/comments/tags include `meshpart-tail-wave815` and `wave815-readback-verified`.
- The two old-style loader rows use the observed `__thiscall` receiver plus five stack arguments proven by callsites and `RET 0x14`.
- The static evidence is bounded to the retail Ghidra metadata, decompile, xref, instruction, callsite, epilogue, queue, and backup artifacts.

What remains unproven:

- Exact concrete CMesh/CMeshPart layouts.
- Exact old mesh-format schema.
- Exact source-body identity.
- Extra-block field meaning beyond the observed `+0xb8` count path.
- Runtime mesh loading, render, collision, or asset behavior.
- BEA patching behavior.
- Rebuild parity.

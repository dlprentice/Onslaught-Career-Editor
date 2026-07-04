# Ghidra Particle CPDSimpleSprite Runtime Transform Review Wave1031

Status: complete static review with one saved correction
Date: 2026-06-01
Scope: `particle-cpdsimplesprite-runtime-transform-review-wave1031`

Wave1031 re-read the particle descriptor / CPDSimpleSprite runtime transform cluster from the Wave911 residual surface. The pass saved one Ghidra correction: `0x004f5b70 CParticleDescriptor__SetIndexedParam` is now `0x004f5b70 CTokenArchive__BindIndexedFieldPointer`. The pass made no function-boundary change and no executable-byte change.

Primary targets:

| Address | Saved state after Wave1031 | Fresh evidence |
| --- | --- | --- |
| `0x004c0150 CParticle__ApplyParentTransformOrStoreLink` | `void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)` | Still matches the Wave476 parent-link/transform helper shape; nonzero `link_parent_only` stores the parent pointer at particle `+0x58`, otherwise the body composes basis/position fields through the parent transform and adds parent position. |
| `0x004c0940 CPDSimpleSprite__SetUVFromTileIndex` | `void __thiscall CPDSimpleSprite__SetUVFromTileIndex(void * this, int tile_index, uint tile_grid_selector, int unused_context)` | Still computes atlas UVs at `+0xb8..+0xc4` from a packed tile index/grid selector, with full-UV fallback when texture/frame state is absent. |
| `0x004c5280 CPDSimpleSprite__CopyTransformMatrix` | `void __thiscall CPDSimpleSprite__CopyTransformMatrix(void * this, void * out_matrix, void * unused_context)` | Still copies observed CPDSimpleSprite matrix/basis fields to the caller output block; exact fourth-column/source layout remains unresolved. |
| `0x004f5b70 CTokenArchive__BindIndexedFieldPointer` | `void __thiscall CTokenArchive__BindIndexedFieldPointer(void * this, int slot_index, void * field_ptr)` | Corrected from `CParticleDescriptor__SetIndexedParam`: body stores `field_ptr` into the TokenArchive slot table at `this+0x0c+(slot_index*4)` and returns with `RET 0x8`; all 15 exported xref windows load `ECX` with the archive receiver and push descriptor field addresses before the call. |
| `0x004c5410 CParticleDescriptor__Update` | `int __thiscall CParticleDescriptor__Update(void * this, void * particle)` | Still matches the Wave461 update vtable entry: copies parent visibility/transform state, creates effect/list state, and can allocate a fallback particle. |

Context evidence covered `0x004c5730 CParticleDescriptor__Load`, `0x004c0c70 CPDSimpleSprite__EvalExpressionNode`, `0x004c07f0 CPDSimpleSprite__WriteTokenFields`, `0x004cc870 CParticleSet__dtor_base`, `0x004cdba0 CParticleManager__LinkNodeByOffset3C40`, `0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40`, `0x004f5b80 CTokenArchive__RegisterReferenceFixup`, and `0x004f5ba0 CTokenArchive__ResolveReferences`.

Evidence counts:

- Pre-mutation primary exports: 5 metadata rows, 5 tag rows, 19 xref rows, 539 body-instruction rows, and 5 decompile rows.
- Context exports: 6 metadata rows, 6 tag rows, 21 xref rows, 667 body-instruction rows, and 6 decompile rows.
- Setter xref-window export: 15 call sites, 255 around-instruction rows, missing=0.
- TokenArchive adjacent context: 2 metadata rows, 83 body-instruction rows, and 2 decompile rows.
- Mutation logs: dry `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 tags_added=7 missing=0 bad=0`; apply `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 tags_added=7 missing=0 bad=0`; final dry `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post-mutation exports: 5 metadata rows, 5 tag rows, 19 xref rows, 539 body-instruction rows, and 5 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1031: `626/1408 = 44.46%`; expanded static surface progress: `855/1493 = 57.27%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- `0x004f5b70` is saved in Ghidra as `CTokenArchive__BindIndexedFieldPointer` with a bounded `void __thiscall ... (void * this, int slot_index, void * field_ptr)` signature.
- The current static evidence supports TokenArchive ownership: `CParticleDescriptor__Load` at `0x004c57d4` / `0x004c57e9` and thirteen adjacent token-load call sites push descriptor field addresses, push a parsed slot index, load `ECX` with the TokenArchive receiver, and call `0x004f5b70`.
- The adjacent `0x004f5b80 CTokenArchive__RegisterReferenceFixup` writes into the same `this+0x0c+(slot_index*4)` table shape, supporting the corrected owner boundary.

What remains unproven:

- Exact source symbol/name beyond the conservative binder label.
- Concrete token-slot enum semantics and full TokenArchive/descriptor layouts.
- Runtime particle parsing, linking, rendering, or transform behavior.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1031; particle-cpdsimplesprite-runtime-transform-review-wave1031; 0x004f5b70 CTokenArchive__BindIndexedFieldPointer; 0x004c0150 CParticle__ApplyParentTransformOrStoreLink; 0x004c0940 CPDSimpleSprite__SetUVFromTileIndex; 0x004c5280 CPDSimpleSprite__CopyTransformMatrix; 0x004c5410 CParticleDescriptor__Update; 0x004f5b80 CTokenArchive__RegisterReferenceFixup; 626/1408 = 44.46%; 855/1493 = 57.27%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-040508_post_wave1031_particle_cpdsimplesprite_runtime_transform_review_verified; one rename/signature/comment correction.

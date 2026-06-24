# Ghidra Particle Descriptor Token Spine Review Wave1007 Readiness Note

Status: complete read-only static read-back evidence
Date: 2026-05-31
Scope: `particle-descriptor-token-spine-review-wave1007`

Wave1007 re-read the Wave461 particle descriptor/token writer spine as a post-Wave994 static re-audit slice. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x004c07f0 CPDSimpleSprite__WriteTokenFields` | CPDSimpleSprite vtable slot 7 row at `0x005ddf7c`; writes simple-sprite token fields through `CTokenArchive__Write*`. |
| `0x004c1970 CPDEmitter__WriteTokenFields` | CPDEmitter vtable slot 7 row at `0x005ddf14`; writes emitter token fields `0x1a` through `0x28`. |
| `0x004c2220 CPDSelector__WriteTokenFields` | CPDSelector vtable slot 7 row at `0x005dde44`; writes selector pointer/int token fields. |
| `0x004c2400 CPDColourRange__WriteTokenFields` | CPDColourRange vtable slot 7 row at `0x005ddddc`; writes colour-range float/int token fields. |
| `0x004c2ca0 CPDShape__WriteTokenFields` | CPDShape vtable slot 7 row at `0x005ddd0c`; writes shape token fields. |
| `0x004c3440 CPDTrail__WriteTokenFields` | CPDTrail vtable slot 7 row at `0x005ddca4`; writes trail token fields. |
| `0x004c4920 CPDFunction__WriteTokenFields` | CPDFunction vtable slot 7 row at `0x005ddbd4`; writes function-curve token fields. |
| `0x004c49b0 CPDMesh__dtor_base` / `0x004c4ae0 CPDMesh__scalar_deleting_dtor` | CPDMesh destructor pair; scalar-deleting wrapper calls the base dtor and conditionally frees through `CDXMemoryManager__Free`. |
| `0x004c4c70 CPDMesh__WriteTokenFields` | CPDMesh vtable slot 7 row at `0x005ddb58`; writes mesh descriptor token fields. |
| `0x004c53b0 CPDFoR__WriteTokenFields` | CPDFoR vtable slot 7 row at `0x005ddfe4`; writes frame-of-reference pointer fields. |
| `0x004c5410 CParticleDescriptor__Update` | CPDFoR vtable slot 10 row at `0x005ddff0`; decompile still calls `CParticleManager__CreateEffect` and `CParticleManager__AllocateParticle`. |
| `0x004c5730 CParticleDescriptor__Load` | CPDFoR vtable slot 32 row at `0x005de048`; loops `CTokenArchive__ReadNextToken`, calls `CParticleDescriptor__SetIndexedParam`, and registers reference fixups. |
| `0x004c59e0 CPDPMesh__WriteTokenFields` | CPDPMesh vtable slot 7 row at `0x005de04c`; writes particle-mesh token fields. |

Read-back evidence:

- Target exports: 14 metadata rows, 14 tag rows, 14 xref rows, 1133 body-instruction rows, and 14 decompile rows.
- Context exports: 7 metadata rows, 7 decompile rows, and 2370 body-instruction rows.
- Vtable/RTTI exports: 480 slot rows and 10 type rows covering CPDMesh, CPDFunction, CPDTrail, CPDShape, CPDColourRange, CPDSelector, CPDEmitter, CPDSimpleSprite, CPDFoR, and CPDPMesh.
- Verified backup: `G:\GhidraBackups\BEA_20260531-143106_post_wave1007_particle_descriptor_token_spine_review_verified`, 19 files, 173869959 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Queue closure remains `6223/6223 = 100.00%` with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Wave911 focused re-audit progress advances to `499/1408 = 35.44%`.
- Expanded static surface progress advances to `676/1478 = 45.74%`.
- Wave911 top-500 risk-ranked coverage advances to `398/500 = 79.60%`.

What this proves:

- The saved Ghidra project still has bounded Wave461 names/signatures/comments/tags for the particle descriptor token-writer spine.
- The selected slot-7 token writers remain attached to the CPD RTTI/vtable family named above.
- `CParticleDescriptor__Update` and `CParticleDescriptor__Load` still bridge the token spine into particle-manager allocation/effect creation and indexed/reference-fixup token handling.

What remains unproven:

- Runtime particle loading, update, rendering, or effect behavior.
- Exact source virtual names.
- Concrete particle descriptor, token archive, particle, effect-handle, or CPD subclass layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.

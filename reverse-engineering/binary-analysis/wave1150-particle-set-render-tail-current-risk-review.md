# Wave1150 Particle Set Render Tail Current-Risk Review

Wave1150 (`wave1150-particle-set-render-tail-current-risk-review`) accounts for `11 current-risk rows` from the Wave1108 current focused denominator as a particle set/render tail current-risk review. It is a fresh Ghidra read-only review with no mutation and no Codex subagent.

Probe token anchor: Wave1150; wave1150-particle-set-render-tail-current-risk-review; 355/1179 = 30.11%; 11 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; current risk candidates: 6166; particle set/render tail current-risk review; fresh Ghidra export; particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CParticle__ApplyParentTransformOrStoreLink; CPDSimpleSprite__VFunc_10_004c14f0; CPDSimpleSprite__VFunc_23_004c8040; CParticleSet__shared_scalar_deleting_dtor; CPDSelector__DispatchChildVFunc20; CParticleSet__InitType11; CParticleSet__InitType12; CParticleSet__InitType13; CParticleSet__FindByNameAndTrackLinkSlot; CParticleSet__LoadParticleSetFile; CParticleManager__UnlinkNodeByOffset3C40; [maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x004c0150` | `CParticle__ApplyParentTransformOrStoreLink` | Parent-transform/link helper reached from raw particle descriptor allocation/update caller `0x004c524f`; stores parent at `particle+0x58` or composes child basis/position through parent transform block `+0xa0`. |
| `0x004c14f0` | `CPDSimpleSprite__VFunc_10_004c14f0` | Simple-sprite vtable slot 10 per-particle update path; writes expression-driven particle state around `+0x74`, optional `+0x50`, descriptor `+0x80` nested dispatch, and frame accumulator `+0x78`. |
| `0x004c8040` | `CPDSimpleSprite__VFunc_23_004c8040` | Simple-sprite vtable slot 23 wrapper that calls `CPDSimpleSprite__InitNoiseTableOnce` and conditionally dispatches `CPDSimpleSprite__ProcessAndRenderSpriteList` when descriptor `+0x6c` is nonzero. |
| `0x004ccb40` | `CParticleSet__shared_scalar_deleting_dtor` | Shared scalar-deleting destructor wrapper used by observed particle-set type vtables; calls `CParticleSet__dtor_base`, frees `this` when flags bit 0 is set, and returns `this`. |
| `0x004ccc50` | `CPDSelector__DispatchChildVFunc20` | Selector child-dispatch helper that walks four descriptor pointer slots at `+0x5c..+0x68` and dispatches each non-null child vfunc `+0x20` with the caller context. |
| `0x004cd290` | `CParticleSet__InitType11` | Type-11 ParticleSet init helper called by `CParticleSet__CreateByType`; clears base/type fields, installs the CPDMesh-flavored vtable, and seeds defaults including `+0x64=100` and `+0x74=1`. |
| `0x004cd2d0` | `CParticleSet__InitType12` | Type-12 ParticleSet init helper called by `CParticleSet__CreateByType`; clears base fields, installs vtable `0x005ddfc8`, and zeroes observed type-local defaults around `+0x5c/+0x60/+0x64`. |
| `0x004cd3c0` | `CParticleSet__InitType13` | Type-13 ParticleSet init helper called by `CParticleSet__CreateByType`; clears extended fields, installs vtable `0x005de030`, and seeds constants including `1.0`, `0.5`, `5.0`, `10`, `180.0`, and `360.0`. |
| `0x004cd7a0` | `CParticleSet__FindByNameAndTrackLinkSlot` | Sorted particle-set/effect name lookup; callers pass `&DAT_0082b400`, the body stores the current link slot in `DAT_0082b3f8`, walks nodes through `+0x38`, compares names with `stricmp`, and returns with `RET 0x4`. |
| `0x004cda60` | `CParticleSet__LoadParticleSetFile` | High-level loader selecting `MainSet.par` for modes `0/2` and `Frontend.par` otherwise, opening a stack `CDXMemBuffer`, calling `CParticleSet__LoadFromArchive`, then closing/destroying the buffer and freeing the filename. |
| `0x004cdbe0` | `CParticleManager__UnlinkNodeByOffset3C40` | Manager/list unlink helper paired with the `+0x3c/+0x40` link fields; called from `CParticleManager__UnlinkNodeFromActiveList` and clears node links after updating owner head/tail fields. |

Fresh primary exports verified `11` metadata rows, `11` tag rows, `67` xref rows, `565` body-instruction rows, and `11` decompile rows. The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence for the selected rows only. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

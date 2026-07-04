# Wave1150 Particle Set Render Tail Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1150-particle-set-render-tail-current-risk-review`

Wave1150 re-read eleven particle set/render tail current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, runtime-file mutation, or Codex subagent.

Probe token anchor: Wave1150; wave1150-particle-set-render-tail-current-risk-review; 355/1179 = 30.11%; 11 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 824; current risk candidates: 6166; particle set/render tail current-risk review; fresh Ghidra export; particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CParticle__ApplyParentTransformOrStoreLink; CPDSimpleSprite__VFunc_10_004c14f0; CPDSimpleSprite__VFunc_23_004c8040; CParticleSet__shared_scalar_deleting_dtor; CPDSelector__DispatchChildVFunc20; CParticleSet__InitType11; CParticleSet__InitType12; CParticleSet__InitType13; CParticleSet__FindByNameAndTrackLinkSlot; CParticleSet__LoadParticleSetFile; CParticleManager__UnlinkNodeByOffset3C40; [maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `11` rows, `targets=11 found=11 missing=0`.
- `pre-tags.tsv`: `11` rows, `missing=0`.
- `pre-xrefs.tsv`: `67` rows.
- `pre-instructions.tsv`: `565` instruction rows, `targets=11 missing=0`.
- `pre-decompile/index.tsv`: `11` rows, `targets=11 dumped=11 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x004c0150 CParticle__ApplyParentTransformOrStoreLink` | Parent-transform/link helper reached from raw particle descriptor allocation/update context; either stores the parent link or composes the child position/basis through parent transform block `+0xa0`. |
| `0x004c14f0 CPDSimpleSprite__VFunc_10_004c14f0` | Simple-sprite vtable slot 10 per-particle update path that writes expression-driven state around `+0x74`, optional `+0x50`, descriptor `+0x80` nested dispatch, and frame accumulator `+0x78`. |
| `0x004c8040 CPDSimpleSprite__VFunc_23_004c8040` | Simple-sprite vtable slot 23 wrapper that initializes the noise table and conditionally dispatches `CPDSimpleSprite__ProcessAndRenderSpriteList`. |
| `0x004ccb40 CParticleSet__shared_scalar_deleting_dtor` | Shared scalar-deleting destructor wrapper used by observed particle-set type vtables; calls `CParticleSet__dtor_base` and frees `this` when flags bit 0 is set. |
| `0x004ccc50 CPDSelector__DispatchChildVFunc20` | Selector child-dispatch helper that walks four descriptor pointer slots at `+0x5c..+0x68` and dispatches each non-null child vfunc `+0x20`. |
| `0x004cd290 CParticleSet__InitType11` | Type-11 ParticleSet init helper called by `CParticleSet__CreateByType`; clears base/type fields, installs the CPDMesh-flavored vtable, and seeds defaults including `+0x64=100` and `+0x74=1`. |
| `0x004cd2d0 CParticleSet__InitType12` | Type-12 ParticleSet init helper called by `CParticleSet__CreateByType`; clears base fields, installs vtable `0x005ddfc8`, and zeroes observed type-local defaults. |
| `0x004cd3c0 CParticleSet__InitType13` | Type-13 ParticleSet init helper called by `CParticleSet__CreateByType`; clears extended fields, installs vtable `0x005de030`, and seeds scalar constants including `1.0`, `0.5`, `5.0`, `10`, `180.0`, and `360.0`. |
| `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot` | Sorted particle-set/effect name lookup; stores the current link slot in `DAT_0082b3f8`, walks nodes through `+0x38`, compares names with `stricmp`, and returns with `RET 0x4`. |
| `0x004cda60 CParticleSet__LoadParticleSetFile` | High-level loader selecting `MainSet.par` for modes `0/2` and `Frontend.par` otherwise, opening a stack `CDXMemBuffer`, calling `CParticleSet__LoadFromArchive`, and cleaning up. |
| `0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40` | Manager/list unlink helper paired with the `+0x3c/+0x40` link fields; called from `CParticleManager__UnlinkNodeFromActiveList` and clears node links after updating owner head/tail fields. |

Accounting after Wave1150:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `355/1179 = 30.11%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 824.

This is static Ghidra evidence only. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

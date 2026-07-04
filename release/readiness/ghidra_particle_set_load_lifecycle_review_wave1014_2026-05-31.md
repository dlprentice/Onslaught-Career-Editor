# Ghidra ParticleSet Load Lifecycle Review Wave1014

Status: PASS read-only static read-back evidence
Date: 2026-05-31
Scope: `particle-set-load-lifecycle-review-wave1014`

Wave1014 re-read the ParticleSet load/factory/lifecycle spine and the ParticleManager active-list link/unlink bridge with fresh Ghidra headless exports. The pass made no Ghidra mutation, no rename, no signature change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Evidence |
| --- | --- |
| `0x004cc020 CParticleSet__CreateByType` | Called by `CParticleSet__LoadFromArchive`; dispatches type-specific allocation/init paths and calls `CParticleSet__Init`. |
| `0x004cc850 CParticleSet__Init` | Called repeatedly by the factory for type setup; saved base initializer signature/comment remain coherent. |
| `0x004ccb40 CParticleSet__shared_scalar_deleting_dtor` | DATA refs from particle-set vtables plus call into `CParticleSet__dtor_base`. |
| `0x004ccc50 CPDSelector__DispatchChildVFunc20` | DATA-backed selector vtable row retained as bounded descriptor dispatch evidence. |
| `0x004cd290 CParticleSet__InitType11` | Factory type-11 init helper called from `CParticleSet__CreateByType`. |
| `0x004cd2d0 CParticleSet__InitType12` | Factory type-12 init helper called from `CParticleSet__CreateByType`. |
| `0x004cd3c0 CParticleSet__InitType13` | Factory type-13 init helper called from `CParticleSet__CreateByType`. |
| `0x004cd7a0 CParticleSet__FindByNameAndTrackLinkSlot` | Broad resolver xrefs from world-physics, BattleEngine, render/resource, frontend, and object-effect contexts; no rename was justified. |
| `0x004cd7f0 CParticleSet__LoadFromArchive` | Called by `CParticleSet__LoadParticleSetFile` and calls `CParticleSet__CreateByType`. |
| `0x004cda60 CParticleSet__LoadParticleSetFile` | Called by `CFrontEnd__LoadSharedResources` and `CGame__LoadResources`; selects `MainSet.par` or `Frontend.par` and uses a stack-local `CDXMemBuffer`. |
| `0x004cdba0 CParticleManager__LinkNodeByOffset3C40` | Called from `CParticleManager__AppendNodeToActiveList` when linking into owner head/tail fields. |
| `0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40` | Called from `CParticleManager__UnlinkNodeFromActiveList` when unlinking/clearing node links. |

Read-back evidence:

- Target exports verified `13` metadata rows, `13` tag rows, `79` xref rows, `997` body-instruction rows, and `13` decompile rows.
- Context exports verified `16` metadata rows, `54` xref rows, `1206` body-instruction rows, and `16` decompile rows.
- Context rows covered particle parent transform/application, ParticleManager init/shutdown/update/allocation/destruction, ParticleDescriptor update/load, `CDXMemBuffer__OpenReadMode11`, `CDXMemBuffer__Close_Thunk`, `CDXMemBuffer__dtor_base_Thunk`, and `CDXMemBuffer__ctor`.
- Export-contract function-quality closure remains `6238/6238 = 100.00%`.
- Wave911 focused re-audit progress remains `505/1408 = 35.87%`.
- Expanded static surface progress is `729/1493 = 48.83%`.
- Wave911 top-500 risk-ranked coverage is `431/500 = 86.20%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified`, `18` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

Probe token anchor: Wave1014; particle-set-load-lifecycle-review-wave1014; 0x004cc020 CParticleSet__CreateByType; 0x004cc850 CParticleSet__Init; 0x004ccb40 CParticleSet__shared_scalar_deleting_dtor; 0x004ccc50 CPDSelector__DispatchChildVFunc20; 0x004cd290 CParticleSet__InitType11; 0x004cd2d0 CParticleSet__InitType12; 0x004cd3c0 CParticleSet__InitType13; 0x004cd7f0 CParticleSet__LoadFromArchive; 0x004cda60 CParticleSet__LoadParticleSetFile; 0x004cdbe0 CParticleManager__UnlinkNodeByOffset3C40; 505/1408 = 35.87%; 729/1493 = 48.83%; 431/500 = 86.20%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260531-191245_post_wave1014_particle_set_load_lifecycle_review_verified; no mutation.

Boundary note: this proves static read-back coherence for the selected ParticleSet/ParticleManager lifecycle rows only. Runtime particle/effect loading, `.par` schema behavior, runtime render/effect behavior, exact source-body identity, concrete ParticleSet/ParticleManager/descriptor/CDXMemBuffer layouts, BEA patching, and rebuild parity remain separate proof.

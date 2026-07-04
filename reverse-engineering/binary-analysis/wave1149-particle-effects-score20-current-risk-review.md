# Wave1149 Particle Effects Score20 Current-Risk Review

Wave1149 (`wave1149-particle-effects-score20-current-risk-review`) accounts for `15 current-risk rows` from the Wave1108 current focused denominator as a particle/effects score20 current-risk review. It is a fresh Ghidra read-only review with no mutation and no Codex subagent.

Probe token anchor: Wave1149; wave1149-particle-effects-score20-current-risk-review; 344/1179 = 29.18%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; current risk candidates: 6166; particle/effects score20 current-risk review; fresh Ghidra export; particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CEngine__ConfigureParticleBurstForDistance; CParticleDescriptor__Update; CParticleDescriptor__Load; CEngine__ComputeSpriteTintByDistance; CParticleManager__SetParticleResource; CParticleManager__CleanupHandles; ParticleEffectLink__SetHandleStateAndClear; CParticleManager__InterpolatePositions; CParticleManager__CreateEffect; CParticleManager__UpdateParticleAndRecycleIfDead; CParticleManager__ProjectPointToTerrainWithRadiusClamp; CParticleManager__ComputeMinCameraDistanceSqForParticle; CParticleManager__DestroyParticleList; CParticleSet__CreateByType; CParticleSet__Init; [maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x004c35d0` | `CEngine__ConfigureParticleBurstForDistance` | Resource-count and slot initialization bridge from simple-sprite burst/tint context into `CParticleManager__SetParticleResource`. |
| `0x004c5410` | `CParticleDescriptor__Update` | Descriptor update vtable entry that creates effect/list state through `CParticleManager__CreateEffect` and can allocate fallback particles. |
| `0x004c5730` | `CParticleDescriptor__Load` | TokenArchive parser loop using `CTokenArchive__ReadNextToken`, texture/indexed-parameter/reference-fixup cases, and terminator token `5`. |
| `0x004c8060` | `CEngine__ComputeSpriteTintByDistance` | Sprite tint/alpha computation from expression colour curves and distance/age fade context. |
| `0x004caed0` | `CParticleManager__SetParticleResource` | Replaces particle `+0x88` resource block through the same vfunc `+0x38` cleanup guard used by `CParticle__Destroy`. |
| `0x004caf60` | `CParticleManager__CleanupHandles` | Walks `DAT_0082b3e4`, advances handle state `+0xb4`, and frees inactive handles. |
| `0x004cb0b0` | `ParticleEffectLink__SetHandleStateAndClear` | Owner-neutral link-cell helper with broad CUnit/BattleEngine/Mine/projectile/raw-cleanup fan-in. |
| `0x004cb300` | `CParticleManager__InterpolatePositions` | Interpolates active effect-handle positions from `DAT_0082b3e8`, including the `10000.0` sentinel path. |
| `0x004cb3d0` | `CParticleManager__CreateEffect` | Allocates particles and optional `0xb8` effect handles, writes spawn vectors, links `DAT_0082b3e4`, and stores flags. |
| `0x004cb920` | `CParticleManager__UpdateParticleAndRecycleIfDead` | Wave994-corrected manager-plus-particle update/recycle helper. |
| `0x004cba30` | `CParticleManager__ProjectPointToTerrainWithRadiusClamp` | Static-shadow terrain-height sample and radius-clamped output point helper. |
| `0x004cba90` | `CParticleManager__ComputeMinCameraDistanceSqForParticle` | Minimum camera-distance-squared helper with multiplayer camera handling and attached-handle offset. |
| `0x004cbff0` | `CParticleManager__DestroyParticleList` | Head-linked particle-list destruction through vfunc slot 0 delete flag `1`. |
| `0x004cc020` | `CParticleSet__CreateByType` | Sorted name lookup/type-id factory, type-specific allocation/vtable/default setup, name copy, and `DAT_0082b450` update. |
| `0x004cc850` | `CParticleSet__Init` | Base particle-set field clear and vtable install helper. |

Fresh primary exports verified `15` metadata rows, `15` tag rows, `118` xref rows, `1891` body-instruction rows, and `15` decompile rows. The verified Ghidra project backup is `[maintainer-local-ghidra-backup-root]\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence for the selected rows only. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

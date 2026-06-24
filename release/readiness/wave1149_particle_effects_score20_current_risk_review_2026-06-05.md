# Wave1149 Particle Effects Score20 Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1149-particle-effects-score20-current-risk-review`

Wave1149 re-read fifteen particle/effects score20 current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, runtime-file mutation, or Codex subagent.

Probe token anchor: Wave1149; wave1149-particle-effects-score20-current-risk-review; 344/1179 = 29.18%; 15 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 835; current risk candidates: 6166; particle/effects score20 current-risk review; fresh Ghidra export; particle descriptor update/load, engine burst/tint, particle manager handles/effects/update/distance/list, and ParticleSet factory/init helpers; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CEngine__ConfigureParticleBurstForDistance; CParticleDescriptor__Update; CParticleDescriptor__Load; CEngine__ComputeSpriteTintByDistance; CParticleManager__SetParticleResource; CParticleManager__CleanupHandles; ParticleEffectLink__SetHandleStateAndClear; CParticleManager__InterpolatePositions; CParticleManager__CreateEffect; CParticleManager__UpdateParticleAndRecycleIfDead; CParticleManager__ProjectPointToTerrainWithRadiusClamp; CParticleManager__ComputeMinCameraDistanceSqForParticle; CParticleManager__DestroyParticleList; CParticleSet__CreateByType; CParticleSet__Init; G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `15` rows, `targets=15 found=15 missing=0`.
- `pre-tags.tsv`: `15` rows, `missing=0`.
- `pre-xrefs.tsv`: `118` rows.
- `pre-instructions.tsv`: `1891` instruction rows, `targets=15 missing=0`.
- `pre-decompile/index.tsv`: `15` rows, `targets=15 dumped=15 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `G:\GhidraBackups\BEA_20260605-185756_post_wave1148_battleengine_walker_control_score20_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the tranche locally after rejecting a duplicate CFastVB scratch selection.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x004c35d0 CEngine__ConfigureParticleBurstForDistance` | Configures particle resource count at `particle+0x80`, calls `CParticleManager__SetParticleResource(count * 0x28)`, and initializes resource slots under `particle+0x88`. |
| `0x004c5410 CParticleDescriptor__Update` | Descriptor update vtable entry that copies parent visibility/transform state, creates effect/list state through `CParticleManager__CreateEffect`, and can allocate fallback particles. |
| `0x004c5730 CParticleDescriptor__Load` | TokenArchive load path with a 1000-byte temp token buffer, `CTokenArchive__ReadNextToken`, texture/indexed-parameter/reference-fixup cases, and terminator token `5`. |
| `0x004c8060 CEngine__ComputeSpriteTintByDistance` | Packed sprite tint/alpha computation from expression colour curves plus distance/age fade context. |
| `0x004caed0 CParticleManager__SetParticleResource` | Replaces the particle `+0x88` resource block with an `OID__AllocObject` allocation after vfunc `+0x38` cleanup. |
| `0x004caf60 CParticleManager__CleanupHandles` | Walks `DAT_0082b3e4`, advances handle state `+0xb4`, and frees inactive handles. |
| `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear` | Owner-neutral link-cell helper reached by CUnit, BattleEngine, Mine, projectile, raw cleanup, and particle descriptor contexts. |
| `0x004cb300 CParticleManager__InterpolatePositions` | Walks active effect handles from `DAT_0082b3e8`, handles the `10000.0` sentinel, and blends current/previous coordinates via `DAT_008a9e44`. |
| `0x004cb3d0 CParticleManager__CreateEffect` | Allocates a particle and optional `0xb8` effect handle, writes spawn vector fields, links `DAT_0082b3e4`, and stores flags. |
| `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead` | Wave994-corrected single-particle update/recycle helper with manager receiver plus one particle stack argument. |
| `0x004cba30 CParticleManager__ProjectPointToTerrainWithRadiusClamp` | Static-shadow terrain-height sample and radius-clamped output point helper. |
| `0x004cba90 CParticleManager__ComputeMinCameraDistanceSqForParticle` | Minimum camera-distance-squared helper with multiplayer camera 0/1 handling and attached-handle offset. |
| `0x004cbff0 CParticleManager__DestroyParticleList` | Destroys every node in a head-linked particle list through vfunc slot 0 delete flag `1`. |
| `0x004cc020 CParticleSet__CreateByType` | Sorted name lookup/type-id factory, type-specific allocation/vtable/default setup, name copy, and `DAT_0082b450` update. |
| `0x004cc850 CParticleSet__Init` | Base particle-set initializer that clears observed fields and installs the base vtable. |

Accounting after Wave1149:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `344/1179 = 29.18%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 835.

This is static Ghidra evidence only. Runtime particle behavior, runtime effect/render behavior, runtime particle descriptor loading, runtime ParticleSet loading, exact particle/descriptor/manager/handle/set layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

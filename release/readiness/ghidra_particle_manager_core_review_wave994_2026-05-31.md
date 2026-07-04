# Ghidra Particle Manager Core Review Wave994 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-31
Scope: `particle-manager-core-review-wave994`

Wave994 re-audited the ParticleManager core cluster after the Wave900-Wave993 recheck gate. The pass saved one Ghidra signature/comment/tag correction at `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead`, removing the stale `unused_context` parameter from the prior Wave463 signature. It made no rename, no function-boundary change, no executable-byte change, no BEA launch, runtime proof, or game-file mutation.

Reviewed targets and context:

| Address | Evidence |
| --- | --- |
| `0x004cae50 CParticle__Destroy` | Frees a particle's `+0x88` resource block, dispatches the observed particle-set vfunc `+0x38`, and clears active-list or owner-handle state. |
| `0x004caf60 CParticleManager__CleanupHandles` | Walks `DAT_0082b3e4`, advances effect-handle state `+0xb4`, and frees inactive handles. |
| `0x004cb0b0 ParticleEffectLink__SetHandleStateAndClear` | Wave477 owner-link helper context; writes linked handle state `+0xb4` and clears the link cell. |
| `0x004cb0e0 CParticleManager__Init` | Allocates and links the `0x200`-entry particle pool and increments `DAT_0082b3ec`. |
| `0x004cb1b0 CParticleManager__Shutdown` | Destroys the particle array, frees the backing allocation, releases the next manager pointer, and decrements `DAT_0082b3ec`. |
| `0x004cb210 CParticleManager__Update` | Per-frame manager update context that updates active particles and then prunes/cleans render-node and handle state. |
| `0x004cb3d0 CParticleManager__CreateEffect` | Allocates a particle/effect handle, stores spawn vector fields, and links `DAT_0082b3e4`. |
| `0x004cb5c0 CParticleManager__AllocateParticle` | Allocates or recycles a particle from the manager pool and dispatches particle-set vfunc `+0x24`. |
| `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead` | Saved Wave994 signature correction: `RET 0x4` plus the `0x004cb924` entry-frame read prove exactly one stack argument after ECX carries the manager receiver. |
| `0x004cba30 CParticleManager__ProjectPointToTerrainWithRadiusClamp` | Samples static-shadow terrain height and writes a clamped output point. |
| `0x004cba90 CParticleManager__ComputeMinCameraDistanceSqForParticle` | Computes camera-distance squared for a particle with multiplayer/single-player camera handling. |
| `0x004cbca0 CParticleManager__UpdateParticles` | Active-list walker that refreshes handle links, integrates particle state, and applies death-flag logic. |
| `0x004cbe30 CParticleManager__PruneDeadParticles` | Recounts live particles, unlinks death-flagged particles, calls `CParticle__Destroy`, and recycles nodes. |
| `0x004cbff0 CParticleManager__DestroyParticleList` | Destroys every node in a head-linked particle list through vfunc slot 0 with delete flag `1`. |

Read-back evidence:

- `ApplyParticleManagerCoreWave994.java dry`: `updated=0 skipped=1 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0`
- `ApplyParticleManagerCoreWave994.java apply`: `updated=1 skipped=0 signature_updated=1 comment_only_updated=0 tags_added=3 missing=0 bad=0`
- `ApplyParticleManagerCoreWave994.java final dry`: `updated=0 skipped=1 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`
- Post exports: `14` metadata rows, `14` tag rows, `120` xref rows, `1130` body-instruction rows, and `14` decompile rows.
- Queue after Wave994: `6222` total functions, `6222` commented, `0` commentless, `0` exact-undefined signatures, `0` `param_N`, static closure `6222/6222 = 100.00%`.
- Wave911 focused re-audit progress: `461/1408 = 32.74%`.
- Expanded static surface progress: `563/1478 = 38.09%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260531-070007_post_wave994_particle_manager_core_review_verified`, `19` files, `173869959` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed function rows exist in the saved Ghidra project with the expected names and signatures.
- `0x004cb920 CParticleManager__UpdateParticleAndRecycleIfDead` now has the saved signature `void __thiscall CParticleManager__UpdateParticleAndRecycleIfDead(void * this, void * particle)`.
- The stale third `unused_context` parameter is removed from the saved signature.
- Instruction evidence at `0x004cb924` and `0x004cba27` supports the one-stack-argument calling convention claim.
- Static xrefs and adjacent ParticleManager rows preserve the pool, update, active-list, handle-cleanup, terrain-projection, distance, and recycle context.

What remains unproven:

- Runtime particle behavior.
- Exact manager, particle, and handle layouts.
- Exact source-body identity.
- BEA patching behavior.
- Rebuild parity.

# Ghidra Particle Manager Owner Links Wave822 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `particle-manager-owner-links-wave822`

Wave822 particle manager owner links saved comments, tags, and observed ABI signatures for four raw-commentless particle/effect owner-link rows: `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks`, `0x004cb040 ParticleEffectLink__PushGlobalList`, `0x004cb080 CParticleManager__PruneDeadOwnerLinks`, and `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState`. The pass corrected the old `CWorldPhysicsManager__PushNodeGlobalList` label/signature at `0x004cb040` to an ECX-node fastcall helper. It made no function-boundary changes and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004caf30 CParticleManager__ClearParticleOwnerBacklinks` | `void __cdecl ... (void)` | Walks the global effect-handle chain at `DAT_0082b3e4` and clears observed owner activity/backlink fields at `+0xa4/+0xa8`; xrefs are game shutdown, DX particle-bundle shutdown, and frontend particle/HUD waypoint release. |
| `0x004cb040 ParticleEffectLink__PushGlobalList` | `void __fastcall ... (void * link_node)` | ECX carries `link_node`; the body stores the old `DAT_0082b3e8` head at `link_node+0` and makes `link_node` the new global effect/owner-link head. Broad xrefs span unit/object/projectile/render/effect creation paths, so the old `CWorldPhysicsManager__PushNodeGlobalList` owner and cdecl stack-argument signature were too narrow. |
| `0x004cb080 CParticleManager__PruneDeadOwnerLinks` | `void __cdecl ... (void)` | Walks the `DAT_0082b3e8` effect/owner-link chain and clears `link_node+0x4` when the linked effect handle's `+0xa4` activity flag is clear. |
| `0x004cbc60 CParticleManager__UpdateRenderNodesAndResetState` | `void __cdecl ... (void)` | Walks render nodes from `DAT_0082b404`, calls vfunc `+0x4`, invokes vfunc `+0x5c(0)` for observed type `0xb`, then restores render-state slot `0xf` through `RenderState_Set`. |

Read-back evidence:

- Accepted dry: `updated=0 skipped=4 renamed=0 would_rename=1 signature_updated=4 comment_only_updated=0 missing=0 bad=0`.
- Accepted apply: `updated=4 skipped=0 renamed=1 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 4 metadata rows, 4 tag rows, 46 xref rows, 1684 target instruction rows, 2353 helper instruction rows, 13 helper metadata rows, and 4 decompile rows.
- Queue after Wave822: 6098 total, 5626 commented, 472 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5626/6098 = 92.26%`, strict clean-signature proxy `5626/6098 = 92.26%`.
- Next raw commentless row: `0x004cd7a0 CWorldPhysicsManager__FindNodeByNameGE`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-180249_post_wave822_particle_manager_owner_links_verified`, 19 files, 171543431 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved names/signatures/comments/tags match the Wave822 script read-back.
- The evidence ties the cluster to static particle effect-handle cleanup, owner-link list insertion/pruning, render-node handoff, xrefs, instruction exports, and decompiler output.

What remains unproven:

- Exact effect-handle, link-node, render-node, and owner layouts.
- Exact source-body identity.
- Runtime particle shutdown behavior.
- Runtime particle/effect behavior.
- Runtime render behavior.
- BEA patching behavior.
- Rebuild parity.

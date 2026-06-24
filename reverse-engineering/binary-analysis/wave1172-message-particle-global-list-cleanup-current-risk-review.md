# Wave1172 Message/Particle Global-List Cleanup Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1172-message-particle-global-list-cleanup-current-risk-review`

Wave1172 accounts for `4 message/particle global-list current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Targets:

| Address | Name | Static read-back evidence |
| --- | --- | --- |
| `0x004b6f10` | `CMessage__scalar_deleting_dtor` | Scalar-deleting destructor wrapper for queued-message objects; DATA vtable xref `0x005dc6b8`; calls `CMessage__dtor_base`; frees through `CDXMemoryManager` when flags bit 0 is set. |
| `0x004b7160` | `CMessage__dtor_base` | Base destructor for queued-message objects; resets the CMessage vtable, clears fields, removes the `+0x30` active-reader cell when present, and calls `CMonitor__Shutdown`. |
| `0x004cb040` | `ParticleEffectLink__PushGlobalList` | Shared ECX-node helper that pushes an effect/owner-link node into global head `DAT_0082b3e8`; xrefs span world physics, mesh rendering, OID creation, units, projectiles, particles, destroyable segments, and spawn-point paths. |
| `0x004cb050` | `CParticleManager__RemoveFromGlobalList` | Removes a node from the global particle-manager/effect-owner linked list rooted at `0x0082b3e8`; xrefs include unit/BattleEngine destructors, particle cleanup, projectile/effect cleanup, and the `CParticleManager__RemoveFromGlobalList_Thunk` context. |

Evidence counts:

- Fresh Ghidra export verified `4` metadata rows, `4` tag rows, `90 xref rows`, `64 instruction rows`, and `4` decompile rows.
- Tags remain as saved retail evidence; `0x004cb050 CParticleManager__RemoveFromGlobalList` still has an empty tag row, so Wave1172 documents the gap instead of normalizing it.
- Verified backup: `G:\GhidraBackups\BEA_20260606-071000_post_wave1172_message_particle_global_list_cleanup_current_risk_review_verified` (`19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`).
- Current-risk accounting after Wave1172: `672/1179 = 57.00%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 507; current risk candidates: 6166; focused threshold `15`; not Wave911 reconstruction.

This wave used a Codex read-only consult as target-selection evidence, then Codex root verified the live Ghidra exports and made the final claim boundary.

Boundary: runtime message display, runtime voice/dialog behavior, runtime particle/global-list behavior, exact `CMessage` layout, exact particle/manager/link-node layout, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1172; wave1172-message-particle-global-list-cleanup-current-risk-review; 672/1179 = 57.00%; 4 message/particle global-list current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 507; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 90 xref rows; 64 instruction rows; CMessage__scalar_deleting_dtor; CMessage__dtor_base; ParticleEffectLink__PushGlobalList; CParticleManager__RemoveFromGlobalList; G:\GhidraBackups\BEA_20260606-071000_post_wave1172_message_particle_global_list_cleanup_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

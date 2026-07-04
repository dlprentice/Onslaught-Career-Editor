# Wave1172 Message/Particle Global-List Cleanup Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-06
Tag: `wave1172-message-particle-global-list-cleanup-current-risk-review`

Wave1172 accounts for `4 message/particle global-list current-risk rows`: `0x004b6f10 CMessage__scalar_deleting_dtor`, `0x004b7160 CMessage__dtor_base`, `0x004cb040 ParticleEffectLink__PushGlobalList`, and `0x004cb050 CParticleManager__RemoveFromGlobalList`.

Static dashboard anchor: Wave1172; wave1172-message-particle-global-list-cleanup-current-risk-review; `672/1179 = 57.00%`; `4 message/particle global-list current-risk rows`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 507; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; static debt `0 / 0 / 0`; `6411/6411 = 100.00%`; `90 xref rows`; `64 instruction rows`; `CMessage__scalar_deleting_dtor`; `CMessage__dtor_base`; `ParticleEffectLink__PushGlobalList`; `CParticleManager__RemoveFromGlobalList`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Read-back evidence:

- Fresh Ghidra exports: `4` metadata rows, `4` tag rows, `90 xref rows`, `64 instruction rows`, and `4` decompile rows.
- Logs report `targets=4 found=4 missing=0`, `rows=4 missing=0`, `Wrote 90 rows`, `Wrote 64 function-body instruction rows`, and `targets=4 dumped=4 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-071000_post_wave1172_message_particle_global_list_cleanup_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Current-risk accounting after Wave1172: `672/1179 = 57.00%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 507; current risk candidates: 6166; focused threshold `15`; not Wave911 reconstruction.

Mutation status: read-only review; no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Boundary: runtime message display, runtime voice/dialog behavior, runtime particle/global-list behavior, exact layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

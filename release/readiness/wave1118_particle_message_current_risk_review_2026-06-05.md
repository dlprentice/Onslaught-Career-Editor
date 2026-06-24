# Wave1118 Particle/Message Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1118-particle-message-current-risk-review`

Wave1118 re-read `13 rows` from the next Wave1108 current focused candidates: 1179, the score-26 particle/message current-risk head, with a fresh read-only Ghidra export and no mutation. Current focused accounting moves to `100/1179 = 8.48%`.

Representative anchors: `0x004729d0 CGameInterface__ctor_base`, `0x0047afc0 CGillMHeadAI__UpdateAimTransformAndTargetReader`, `0x0047b090 CGillMHeadAI__UpdateTargetBallisticArcFlags`, `0x004b6e50 CMessage__ctor_base`, `0x004cae50 CParticle__Destroy`, `0x004cb0e0 CParticleManager__Init`, `0x004cb1b0 CParticleManager__Shutdown`, `0x004cb210 CParticleManager__Update`, `0x004cb5c0 CParticleManager__AllocateParticle`, `0x004cbca0 CParticleManager__UpdateParticles`, `0x004cbe30 CParticleManager__PruneDeadParticles`, `0x004cc870 CParticleSet__dtor_base`, and `0x004cd7f0 CParticleSet__LoadFromArchive`.

Evidence:

- Fresh metadata export: `13` rows, `targets=13 found=13 missing=0`.
- Fresh tag export: `13` rows, `missing=0`.
- Fresh xref export: `34` rows.
- Fresh instruction export: `1521` rows, `targets=13 missing=0`.
- Fresh decompile export: `13` rows, `targets=13 dumped=13 missing=0 failed=0`.
- Mutation status: no mutation, no rename, no signature change, no comment/tag write, no executable-byte change.
- Backup: `G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-014214_post_wave1117_cengine_current_risk_review_verified`.

What this proves:

- The thirteen target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows are coherent with the existing bounded GameInterface, GillMHeadAI, CMessage, CParticleManager, and CParticleSet evidence.
- The current-risk accounting advances from `87/1179 = 7.38%` to `100/1179 = 8.48%` without requiring a Ghidra mutation.

What remains separate:

- Runtime particle behavior.
- Runtime message behavior.
- Runtime targeting behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

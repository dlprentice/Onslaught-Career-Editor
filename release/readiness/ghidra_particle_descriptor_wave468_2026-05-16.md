# Ghidra Particle Descriptor Wave468 Evidence

Date: 2026-05-16

## Scope

Wave468 saved Ghidra name/signature/comment/tag corrections for `5` particle descriptor and active-list targets:

`0x004c0370`, `0x004c0450`, `0x004c04c0`, `0x004c0510`, and `0x004c0560`.

Candidate `0x004c0150` was reviewed but intentionally left unchanged because the current `CUnitAI` ownership looks suspicious beside the particle/CPD region and needs a later boundary/owner review.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave468-cunitai-particle-current/`
- Apply script: `tools/ApplyParticleDescriptorWave468.java`
- Probe: `tools/ghidra_particle_descriptor_wave468_probe.py`
- Test alias: `npm run test:ghidra-particle-descriptor-wave468`
- Dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply summary: `updated=5 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `5` metadata rows, `5` tag rows, `22` xref rows, `5` decompile exports plus `index.tsv`, `1105` focused instruction rows, `13` RTTI type rows, and `416` vtable-slot rows.
- Hardened `CParticleDescriptor__PushCurrentToHistoryAndSetNow` and `CParticleDescriptor__Load12DwordsAndMarkDirty`.
- Corrected shared RTTI/vtable slot 23 to `CParticleDescriptor__DispatchTimedParticleNodes`.
- Corrected `CParticleManager__LinkNodeFront` to `CParticleManager__AppendNodeToActiveList`.
- Corrected `CEngine__RemoveNodeFromActiveList` to `CParticleManager__UnlinkNodeFromActiveList`.
- Queue after refresh: `6057` functions, `2134` commented, `3923` commentless, `1705` undefined signatures, `1580` `param_N` signatures.
- Current telemetry proxies: comment-backed `2134/6057 = 35.23%`; strict comment-plus-clean-signature `2067/6057 = 34.13%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-210736_post_wave468_particle_descriptor_verified` (`19` files, `157125511` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime particle/list behavior, exact descriptor/manager/node layouts, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

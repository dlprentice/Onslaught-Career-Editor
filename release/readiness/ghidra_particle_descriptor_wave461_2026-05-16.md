# Ghidra Particle Descriptor / Token Writer Wave461 Evidence

Date: 2026-05-16

## Scope

Wave461 saved Ghidra name/signature/comment/tag corrections for `14` particle descriptor, CPD token-writer, and CPDMesh lifecycle targets:

`0x004c07f0`, `0x004c1970`, `0x004c2220`, `0x004c2400`, `0x004c2ca0`, `0x004c3440`, `0x004c4920`, `0x004c49b0`, `0x004c4ae0`, `0x004c4c70`, `0x004c53b0`, `0x004c5410`, `0x004c5730`, and `0x004c59e0`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave461-particle-descriptor-current/`
- Apply script: `tools/ApplyParticleDescriptorWave461.java`
- Probe: `tools/ghidra_particle_descriptor_wave461_probe.py`
- Test alias: `npm run test:ghidra-particle-descriptor-wave461`
- Dry summary: `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=12 missing=0 bad=0`
- Apply summary: `updated=14 skipped=0 created=0 would_create=0 renamed=12 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=14 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `22` metadata rows, `22` tag rows, `24` xref rows, `22` decompile exports plus `index.tsv`, and `2662` focused instruction rows.
- Corrected ten vtable slot-7 token writers: `CPDSimpleSprite__WriteTokenFields`, `CPDEmitter__WriteTokenFields`, `CPDSelector__WriteTokenFields`, `CPDColourRange__WriteTokenFields`, `CPDShape__WriteTokenFields`, `CPDTrail__WriteTokenFields`, `CPDFunction__WriteTokenFields`, `CPDMesh__WriteTokenFields`, `CPDFoR__WriteTokenFields`, and `CPDPMesh__WriteTokenFields`.
- Corrected `CPDMesh__dtor_base` / `CPDMesh__scalar_deleting_dtor`, and hardened `CParticleDescriptor__Update` / `CParticleDescriptor__Load` to explicit `int __thiscall` signatures.
- Queue after refresh: `6057` functions, `2059` commented, `3998` commentless, `1725` undefined signatures, `1617` `param_N` signatures.
- Current telemetry proxies: comment-backed `2059/6057 = 33.99%`; strict comment-plus-clean-signature `1992/6057 = 32.89%`.
- Verified backup: `G:\GhidraBackups\BEA_20260516-175743_post_wave461_particle_descriptor_verified` (`19` files, `156928903` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime particle rendering/loading behavior, exact descriptor and particle layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.

# Ghidra Particle Manager / Particle Set Wave463 Evidence

Date: 2026-05-16

## Scope

Wave463 saved Ghidra signature/comment/tag corrections for `17` ParticleManager/ParticleSet targets:

`0x004cae50`, `0x004caed0`, `0x004caf60`, `0x004cb0e0`, `0x004cb1b0`, `0x004cb210`, `0x004cb300`, `0x004cb3d0`, `0x004cb5c0`, `0x004cb920`, `0x004cba30`, `0x004cba90`, `0x004cbca0`, `0x004cbe30`, `0x004cbff0`, `0x004cc020`, and `0x004cc850`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave463-particle-manager-current/`
- Apply script: `tools/ApplyParticleManagerWave463.java`
- Probe: `tools/ghidra_particle_manager_wave463_probe.py`
- Test alias: `npm run test:ghidra-particle-manager-wave463`
- Dry summary: `updated=0 skipped=17 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply summary: `updated=17 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=17 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `17` metadata rows, `17` tag rows, `95` xref rows, `17` decompile exports plus `index.tsv`, and `1037` focused instruction rows.
- Hardened particle resource ownership/free paths, manager pool init/shutdown/update, effect-handle cleanup/interpolation/create, allocation and recycle paths, terrain projection, camera-distance LOD helper, active-list update/prune/destruction, and the ParticleSet factory/base init.
- Queue after refresh: `6057` functions, `2090` commented, `3967` commentless, `1712` undefined signatures, `1599` `param_N` signatures.
- Current telemetry proxies: comment-backed `2090/6057 = 34.51%`; strict comment-plus-clean-signature `2026/6057 = 33.45%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-185524_post_wave463_particle_manager_verified` (`19` files, `157059975` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime particle/effect behavior, exact particle/handle/set layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.

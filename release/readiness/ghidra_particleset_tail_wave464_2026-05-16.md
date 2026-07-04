# Ghidra ParticleSet Tail Wave464 Evidence

Date: 2026-05-16

## Scope

Wave464 saved Ghidra name/signature/comment/tag corrections for `8` ParticleSet-tail and adjacent descriptor targets:

`0x004cc870`, `0x004ccb40`, `0x004ccc50`, `0x004cd290`, `0x004cd2d0`, `0x004cd3c0`, `0x004cd7f0`, and `0x004cda60`.

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave464-particleset-tail-current/`
- Apply script: `tools/ApplyParticleSetTailWave464.java`
- Probe: `tools/ghidra_particleset_tail_wave464_probe.py`
- Test alias: `npm run test:ghidra-particleset-tail-wave464`
- Dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0`
- Apply summary: `updated=8 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`
- Verify-dry summary: `updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports verified `8` metadata rows, `8` tag rows, `21` xref rows, `8` decompile exports plus `index.tsv`, and `1448` focused instruction rows.
- Corrected `CParticleSet__dtor_base`, `CParticleSet__shared_scalar_deleting_dtor`, and `CPDSelector__DispatchChildVFunc20`, and hardened ParticleSet type-11/12/13 init plus archive/file loading helpers.
- Queue after refresh: `6057` functions, `2098` commented, `3959` commentless, `1707` undefined signatures, `1596` `param_N` signatures.
- Current telemetry proxies: comment-backed `2098/6057 = 34.64%`; strict comment-plus-clean-signature `2031/6057 = 33.53%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260516-192025_post_wave464_particleset_tail_verified` (`19` files, `157092743` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`).

## Boundary

This is static retail-binary evidence only. Runtime particle-set loading/render behavior, exact descriptor/particle-set layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.

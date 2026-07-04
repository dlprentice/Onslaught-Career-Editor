# Ghidra Particle Parent Transform Wave476 Readiness

Date: 2026-05-17

## Scope

Wave476 saved a bounded Ghidra owner/signature/comment/tag correction for:

- `0x004c0150` `CParticle__ApplyParentTransformOrStoreLink`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave476-particle-boundary-004c0150/`
- Apply script: `tools/ApplyParticleParentTransformWave476.java`
- Focused probe: `tools/ghidra_particle_parent_transform_wave476_probe.py`
- Probe test: `tools/ghidra_particle_parent_transform_wave476_probe_test.py`
- Function docs: `reverse-engineering/binary-analysis/functions/ParticleDescriptor.cpp/`

## Result

`ApplyParticleParentTransformWave476.java` reported:

- Dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Apply: `updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Saved signature:

```c
void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only);
```

Read-back verified `1` target metadata row, the expected tag row, the caller xref from raw non-function code at `0x004c524f`, the target decompile export, the caller-range allocation/push/call evidence, `RET 0x0c` callee epilogues at `0x004c016b` and `0x004c035f`, and focused probe status `PASS`.

## Boundary

This is static retail-binary evidence only. Exact particle layout, exact source identity, runtime particle behavior, raw caller boundary/name, BEA launch behavior, game patching, and rebuild parity remain unproven. The raw caller region around `0x004c51f7..0x004c5274` remains deferred and was not converted into a function in Wave476.

## Queue Snapshot

Fresh queue after Wave476:

- Function objects: `6057`
- Functions with comments: `2153`
- Commentless functions: `3904`
- Undefined signatures: `1702`
- `param_N` signatures: `1556`
- Comment-backed proxy: `2153/6057 = 35.55%`
- Strict comment-plus-clean-signature proxy: `2097/6057 = 34.62%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260517-003734_post_wave476_particle_parent_transform_verified
SourceCount 19
BackupCount 19
BackupBytes 157223815
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

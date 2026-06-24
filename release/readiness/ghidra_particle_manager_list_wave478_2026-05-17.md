# Ghidra Particle Manager List Wave478 Readiness

Date: 2026-05-17

## Scope

Wave478 saved a bounded Ghidra signature/comment/owner correction for the particle-manager global nonempty-list helpers:

- `0x004cdba0` `CParticleManager__LinkNodeByOffset3C40`
- `0x004cdbe0` `CParticleManager__UnlinkNodeByOffset3C40`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave478-engine-queue-head-004cdbe0/`
- Apply script: `tools/ApplyParticleManagerListWave478.java`
- Focused probe: `tools/ghidra_particle_manager_list_wave478_probe.py`
- Probe test: `tools/ghidra_particle_manager_list_wave478_probe_test.py`
- Function docs: `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/`

## Result

`ApplyParticleManagerListWave478.java` reported:

- Initial dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Initial apply issue: `updated=0 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=2`
- Corrected dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Corrected apply: `updated=2 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

The initial apply issue was a Ghidra `__thiscall` implicit-`this` modeling mismatch: the first script revision named the ECX owner parameter `list_owner`, so read-back displayed an implicit `this` plus `list_owner` and `node`. The corrected script models ECX as `this`; the final corrected apply/read-back artifacts are clean and the focused probe records the initial issue as handled evidence.

Saved signatures:

```c
void __thiscall CParticleManager__LinkNodeByOffset3C40(void * this, void * node);
void __thiscall CParticleManager__UnlinkNodeByOffset3C40(void * this, void * node);
```

Read-back verified metadata, tags, xrefs, post-decompile tokens, `RET 0x4` one-stack-argument epilogues, the sibling link/unlink range at `0x004cdba0..0x004cdc22`, and the active-list callsite range at `0x004c04f0..0x004c05d0`. The xrefs prove `CParticleManager__AppendNodeToActiveList` calls the link helper at `0x004c0520`, and `CParticleManager__UnlinkNodeFromActiveList` calls the unlink helper at `0x004c05b4` after pushing the manager and loading ECX with global list owner `0x0082b400`.

## Boundary

This is static retail-binary evidence only. Exact global-list type, concrete particle-manager layout, runtime particle scheduling behavior, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Queue Snapshot

Fresh queue after Wave478:

- Function objects: `6057`
- Functions with comments: `2156`
- Commentless functions: `3901`
- Undefined signatures: `1702`
- `param_N` signatures: `1554`
- Comment-backed proxy: `2156/6057 = 35.60%`
- Strict comment-plus-clean-signature proxy: `2100/6057 = 34.67%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
G:\GhidraBackups\BEA_20260517-013642_post_wave478_particle_manager_list_verified
SourceCount 19
BackupCount 19
BackupBytes 157256583
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

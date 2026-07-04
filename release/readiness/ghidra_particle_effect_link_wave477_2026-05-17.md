# Ghidra Particle Effect Link Wave477 Readiness

Date: 2026-05-17

## Scope

Wave477 saved a bounded Ghidra owner/signature/comment/tag correction for:

- `0x004cb0b0` `ParticleEffectLink__SetHandleStateAndClear`

It also refreshed stale comments that still referenced the old callee name at:

- `0x0047cea0` `CGroundUnit__ClearLinkedThingFlagsAndResetCounter`
- `0x004ba490` `CMine__VFunc02_CleanupLinkedParticleAndForward`
- `0x004f84e0` `CUnit__dtor_base`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave477-unit-finalize-linked-state-004cb0b0/`
- Apply script: `tools/ApplyParticleEffectLinkWave477.java`
- Comment refresh script: `tools/ApplyParticleEffectLinkCommentRefreshWave477.java`
- Focused probe: `tools/ghidra_particle_effect_link_wave477_probe.py`
- Probe test: `tools/ghidra_particle_effect_link_wave477_probe_test.py`
- Function docs: `reverse-engineering/binary-analysis/functions/ParticleManager.cpp/`, `reverse-engineering/binary-analysis/functions/Mine.cpp/`, and `reverse-engineering/binary-analysis/functions/Unit.cpp/`

## Result

`ApplyParticleEffectLinkWave477.java` reported:

- Dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0`
- Apply: `updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

`ApplyParticleEffectLinkCommentRefreshWave477.java` reported:

- Dry: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=3 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Saved signature:

```c
void __thiscall ParticleEffectLink__SetHandleStateAndClear(void * this, int set_state_one);
```

Read-back verified the target metadata/tag/decompile rows, refreshed comments/tags on the three dependent comments, key xrefs from Mine, CUnit, BattleEngine, raw non-function cleanup, and projectile contexts, the `RET 0x4` one-stack-argument epilogues, the `this+0x4` linked-handle read, the handle `+0xb4` state writes to `1` or `2`, the raw caller range around `0x004c570f..0x004c5725`, and focused probe status `PASS`.

## Boundary

This is static retail-binary evidence only. Exact owner-link/handle layouts, raw caller boundaries, runtime particle/effect behavior, exact source identity, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Queue Snapshot

Fresh queue after Wave477:

- Function objects: `6057`
- Functions with comments: `2154`
- Commentless functions: `3903`
- Undefined signatures: `1702`
- `param_N` signatures: `1555`
- Comment-backed proxy: `2154/6057 = 35.56%`
- Strict comment-plus-clean-signature proxy: `2098/6057 = 34.64%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260517-010555_post_wave477_particle_effect_link_verified
SourceCount 19
BackupCount 19
BackupBytes 157223815
MissingCount 0
ExtraCount 0
HashDiffCount 0
```

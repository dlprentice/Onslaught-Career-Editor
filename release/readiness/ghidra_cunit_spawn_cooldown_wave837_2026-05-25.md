# Ghidra CUnit Spawn Cooldown Wave837 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cunit-spawn-cooldown-wave837`

Wave837 CUnit Spawn Cooldown corrected `0x004fc3a0` from stale `CSpawnerThng__SetCooldownState3` metadata to `CUnit__SetSpawnCooldownState3` with signature `void __thiscall CUnit__SetSpawnCooldownState3(void * this, float cooldown_delay)`.

Evidence anchors:

| Address | Evidence |
| --- | --- |
| `0x004fc3a0 CUnit__SetSpawnCooldownState3` | Body writes state literal `3` to `this+0x168`, then writes `DAT_00672fd0 + cooldown_delay` to `this+0x16c`. |
| `0x004fc3b0` / `0x004fc3ba` | `FADD [ESP+0x4]` plus `RET 0x4` prove one explicit float argument after ECX, replacing the stale `int cooldown_ticks, float unused_scale` signature. |
| `0x004e430f CSpawnerThng__ProcessSpawnWave` | Sole code xref. Caller runs after `CWorldPhysicsManager__CreateThingByType` and spawned-object vfunc `+0x24` init, sets `ECX` to the created object, and pushes spawner config `+0x1c`. |
| CUnit neighborhood | The row sits between `0x004fc220 CUnit__SpawnComponentEffectsRecursive` and `0x004fc4e0 CUnit__UpdateTransform`, supporting bounded CUnit helper naming. |

Read-back evidence:

- `ApplyCUnitSpawnCooldownWave837.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitSpawnCooldownWave837.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitSpawnCooldownWave837.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 121 instruction-window rows, 381 deep instruction rows, 69 xref-site instruction rows, 16 context metadata rows, 16 context decompile rows, and 1 target decompile row.
- Queue after Wave837: 6098 total, 5659 commented, 439 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5659/6098 = 92.80%`, strict clean-signature proxy `5659/6098 = 92.80%`.
- Next raw commentless row: `0x004fce40 CUnitAI__CallAttachedNodeVFunc14IfPresent`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-013914_post_wave837_cunit_spawn_cooldown_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row exists at `0x004fc3a0`.
- The saved name/signature/comment/tags match the bounded CUnit spawn-cooldown interpretation.
- The stale `CSpawnerThng__SetCooldownState3` owner and phantom second parameter have been corrected in saved Ghidra metadata.
- The observed behavior is static retail Ghidra evidence tied to the callee body, sole xref from `CSpawnerThng__ProcessSpawnWave`, caller-site instructions, context decompile, and queue read-back.

What remains unproven:

- Exact Unit.cpp source-body identity.
- Exact state enum meaning.
- Concrete CUnit field names/layout.
- Runtime spawn activation/cooldown behavior.
- BEA patching behavior.
- Rebuild parity.

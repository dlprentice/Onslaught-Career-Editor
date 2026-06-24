# Ghidra Spawner Value Apply Strip Review Wave1035

Status: complete read-only static review
Date: 2026-06-01
Scope: `spawner-value-apply-strip-review-wave1035`

Wave1035 re-read the twelve numeric `CSpawner*__ApplyToSpawnerByName` helpers originally hardened by Wave339, from `0x0043a170 CSpawnerDelay__ApplyToSpawnerByName` through `0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName`. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Saved state confirmed by Wave1035 | Fresh instruction/decompile evidence |
| --- | --- | --- |
| `0x0043a170 CSpawnerDelay__ApplyToSpawnerByName` | `void __thiscall ...(void * this, char * spawnerName)` with Wave339 spawner tags. | Walks `DAT_008553f4` by `spawnerName`; writes `this+0x8` to spawner record `+0x18`. |
| `0x0043a200 CSpawnerAmount__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x0c`. |
| `0x0043a290 CSpawnerConditions__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x14`. |
| `0x0043a320 CSpawnerSquadSize__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x10`. |
| `0x0043a3b0 CSpawnerSquadDelay__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x20`. |
| `0x0043a440 CSpawnerSeekDelay__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x1c`. |
| `0x0043a4d0 CSpawnerRecall__ApplyToSpawnerByName` | Same ABI with `boolean-spawner-value` tag. | Writes constant `1` to record `+0x28`. |
| `0x0043a570 CSpawnerMinRange__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x2c`. |
| `0x0043a600 CSpawnerMaxRange__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x30`. |
| `0x0043a690 CSpawnerPreSpawnDelay__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x34`. |
| `0x0043a720 CSpawnerPostSpawnDelay__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x38`. |
| `0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName` | Same ABI and Wave339 tag family. | Writes `this+0x8` to record `+0x24`. |

Evidence counts:

- Fresh exports: `12` metadata rows, `12` tag rows, `12` DATA xref rows, `793` body-instruction rows, and `12` decompile rows.
- Xrefs remain vtable DATA refs from `0x005da68c`, `0x005da678`, `0x005da59c`, `0x005da664`, `0x005da650`, `0x005da63c`, `0x005da628`, `0x005da614`, `0x005da600`, `0x005da5ec`, `0x005da5d8`, and `0x005da5b0`.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1035: `672/1408 = 47.73%`.
- Expanded static surface progress after Wave1035: `901/1493 = 60.35%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-061824_post_wave1035_spawner_value_apply_strip_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected Wave339 numeric spawner apply rows still have coherent saved names, signatures, comments, tags, vtable DATA refs, instruction bodies, and decompile output.
- The saved record-offset comments still match fresh instruction evidence for all twelve rows.
- The rows remain a static PhysicsScript bridge from named spawner-value script objects into fields of records reachable through `DAT_008553f4`.

What remains unproven:

- Runtime PhysicsScript loading/application behavior.
- Runtime spawner behavior or mission-script outcomes.
- Concrete spawner record/value object layouts beyond observed offsets.
- Exact source-body identity and local variable names/types.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1035; spawner-value-apply-strip-review-wave1035; 0x0043a170 CSpawnerDelay__ApplyToSpawnerByName; 0x0043a4d0 CSpawnerRecall__ApplyToSpawnerByName; 0x0043a7b0 CSpawnerInfinite__ApplyToSpawnerByName; DAT_008553f4; 672/1408 = 47.73%; 901/1493 = 60.35%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-061824_post_wave1035_spawner_value_apply_strip_review_verified; no mutation.

# Ghidra Explosion Value Apply Strip Review Wave1036

Status: complete read-only static review
Date: 2026-06-01
Scope: `explosion-value-apply-strip-review-wave1036`

Wave1036 re-read thirteen `CExplosion*__ApplyToExplosionByName` helpers originally hardened by Wave340, from `0x0043afc0 CExplosionAirEffect__ApplyToExplosionByName` through `0x0043b880 CExplosionWaterSound__ApplyToExplosionByName`. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Saved state confirmed by Wave1036 | Fresh instruction/decompile evidence |
| --- | --- | --- |
| `0x0043afc0 CExplosionAirEffect__ApplyToExplosionByName` | `void __thiscall ...(void * this, char * explosionName)` with Wave340 owned-string tags. | Walks `DAT_008553f8` by `explosionName`; frees/reallocates the owned string at explosion record `+0x18` from `this+0x8`. |
| `0x0043b0b0 CExplosionGroundEffect__ApplyToExplosionByName` | Same ABI and Wave340 tag family. | Replaces owned string at record `+0x20`. |
| `0x0043b1c0 CExplosionWaterEffect__ApplyToExplosionByName` | Same ABI and Wave340 tag family. | Replaces owned string at record `+0x1c`. |
| `0x0043b2b0 CExplosionUnitEffect__ApplyToExplosionByName` | Same ABI and Wave340 tag family. | Replaces owned string at record `+0x24`. |
| `0x0043b3a0 CExplosionScalar34__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x34`. |
| `0x0043b430 CExplosionScalar38__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x38`. |
| `0x0043b4c0 CExplosionScalar3C__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x3c`. |
| `0x0043b550 CExplosionScalar44__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x44`. |
| `0x0043b5e0 CExplosionScalar48__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x48`. |
| `0x0043b670 CExplosionScalar4C__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x4c`. |
| `0x0043b700 CExplosionScalar40__ApplyToExplosionByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to record `+0x40`. |
| `0x0043b790 CExplosionSound__ApplyToExplosionByName` | Same ABI and Wave340 owned-string tag family. | Replaces owned string at record `+0x28`. |
| `0x0043b880 CExplosionWaterSound__ApplyToExplosionByName` | Same ABI and Wave340 owned-string tag family. | Replaces owned string at record `+0x2c`. |

Evidence counts:

- Fresh exports: `13` metadata rows, `13` tag rows, `13` DATA xref rows, `1050` body-instruction rows, and `13` decompile rows.
- Xrefs remain vtable DATA refs from `0x005da7cc`, `0x005da7b8`, `0x005da7a4`, `0x005da790`, `0x005da768`, `0x005da77c`, `0x005da754`, `0x005da718`, `0x005da6f0`, `0x005da704`, `0x005da740`, `0x005da72c`, and `0x005da6c8`.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1036: `685/1408 = 48.65%`.
- Expanded static surface progress after Wave1036: `914/1493 = 61.22%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-064537_post_wave1036_explosion_value_apply_strip_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected Wave340 explosion apply rows still have coherent saved names, signatures, comments, tags, vtable DATA refs, instruction bodies, and decompile output.
- The saved record-offset comments still match fresh instruction/decompile evidence for all thirteen rows.
- The rows remain a static PhysicsScript bridge from named explosion-value script objects into fields of records reachable through `DAT_008553f8`.

What remains unproven:

- Runtime PhysicsScript loading/application behavior.
- Runtime explosion behavior or mission-script outcomes.
- Concrete explosion record/value object layouts beyond observed offsets.
- Exact source-body identity and local variable names/types.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1036; explosion-value-apply-strip-review-wave1036; 0x0043afc0 CExplosionAirEffect__ApplyToExplosionByName; 0x0043b3a0 CExplosionScalar34__ApplyToExplosionByName; 0x0043b880 CExplosionWaterSound__ApplyToExplosionByName; DAT_008553f8; 685/1408 = 48.65%; 914/1493 = 61.22%; 500/500 = 100.00%; 6238/6238 = 100.00%; G:\GhidraBackups\BEA_20260601-064537_post_wave1036_explosion_value_apply_strip_review_verified; no mutation.

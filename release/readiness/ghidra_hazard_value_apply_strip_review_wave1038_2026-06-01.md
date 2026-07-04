# Ghidra Hazard Value Apply Strip Review Wave1038

Status: complete read-only static review
Date: 2026-06-01
Scope: `hazard-value-apply-strip-review-wave1038`

Wave1038 re-read four `CHazard*__ApplyToHazardByName` helpers originally hardened by Wave342, from `0x0043c1a0 CHazardScalar14__ApplyToHazardByName` through `0x0043c410 CHazardEffect__ApplyToHazardByName`. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Saved state confirmed by Wave1038 | Fresh instruction/decompile evidence |
| --- | --- | --- |
| `0x0043c1a0 CHazardScalar14__ApplyToHazardByName` | `void __thiscall ...(void * this, char * hazardName)` with Wave342 scalar tags. | Walks `DAT_00855408` by `hazardName`; writes `this+0x8` to hazard record `+0x14`. |
| `0x0043c280 CHazardScalar18__ApplyToHazardByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to hazard record `+0x18`. |
| `0x0043c320 CHazardNoise__ApplyToHazardByName` | Same ABI and `owned-string-copy` tag. | Replaces owned noise string at hazard record `+0x0c` from `this+0x8`. |
| `0x0043c410 CHazardEffect__ApplyToHazardByName` | Same ABI and `owned-string-copy` tag. | Replaces owned effect string at hazard record `+0x8` from `this+0x8`. |

Evidence counts:

- Fresh exports: `4` metadata rows, `4` tag rows, `4` DATA xref rows, `328` body-instruction rows, and `4` decompile rows.
- Xrefs remain vtable DATA refs from `0x005da8e4`, `0x005da8d0`, `0x005da8a8`, and `0x005da8bc`.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1038: `696/1408 = 49.43%`.
- Expanded static surface progress after Wave1038: `925/1493 = 61.96%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-072720_post_wave1038_hazard_value_apply_strip_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected Wave342 hazard apply rows still have coherent saved names, signatures, comments, tags, vtable DATA refs, instruction bodies, and decompile output.
- The saved record-offset comments still match fresh instruction/decompile evidence for all four rows.
- The rows remain a static PhysicsScript bridge from named hazard-value script objects into fields of records reachable through `DAT_00855408`.

What remains unproven:

- Runtime PhysicsScript loading/application behavior.
- Runtime hazard behavior or mission-script outcomes.
- Concrete hazard record/value object layouts beyond observed offsets.
- Scalar/string field semantics, exact source-body identity, and local variable names/types.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1038; hazard-value-apply-strip-review-wave1038; 0x0043c1a0 CHazardScalar14__ApplyToHazardByName; 0x0043c280 CHazardScalar18__ApplyToHazardByName; 0x0043c320 CHazardNoise__ApplyToHazardByName; 0x0043c410 CHazardEffect__ApplyToHazardByName; DAT_00855408; 696/1408 = 49.43%; 925/1493 = 61.96%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-072720_post_wave1038_hazard_value_apply_strip_review_verified; no mutation.

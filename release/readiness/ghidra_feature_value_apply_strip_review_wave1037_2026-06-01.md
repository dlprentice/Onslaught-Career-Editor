# Ghidra Feature Value Apply Strip Review Wave1037

Status: complete read-only static review
Date: 2026-06-01
Scope: `feature-value-apply-strip-review-wave1037`

Wave1037 re-read seven `CFeature*__ApplyToFeatureByName` helpers originally hardened by Wave341, from `0x0043bb30 CFeatureScalar18__ApplyToFeatureByName` through `0x0043c010 CFeatureTexture__ApplyToFeatureByName`. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Saved state confirmed by Wave1037 | Fresh instruction/decompile evidence |
| --- | --- | --- |
| `0x0043bb30 CFeatureScalar18__ApplyToFeatureByName` | `void __thiscall ...(void * this, char * featureName)` with Wave341 scalar tags. | Walks `DAT_00855404` by `featureName`; writes `this+0x8` to feature record `+0x18`. |
| `0x0043bbf0 CFeatureScalar1C__ApplyToFeatureByName` | Same ABI and `offset-backed-scalar` tag. | Writes `this+0x8` to feature record `+0x1c`. |
| `0x0043bc80 CFeatureFlag10__ApplyToFeatureByName` | Same ABI and `offset-backed-flag` tag. | Compares `this+0x8` with `0.0` and writes a derived `1/0` flag to record `+0x10`. |
| `0x0043bd40 CFeatureFlag14__ApplyToFeatureByName` | Same ABI and `offset-backed-flag` tag. | Compares `this+0x8` with `0.0` and writes a derived `1/0` flag to record `+0x14`. |
| `0x0043be10 CFeatureMesh__ApplyToFeatureByName` | Same ABI and `owned-string-copy` tag. | Replaces owned mesh string at record `+0x0` from `this+0x8`. |
| `0x0043bf00 CFeatureNoise__ApplyToFeatureByName` | Same ABI and `owned-string-copy` tag. | Replaces owned noise string at record `+0x0c` from `this+0x8`. |
| `0x0043c010 CFeatureTexture__ApplyToFeatureByName` | Same ABI and `texture-name` tag. | Finds the feature record through `DAT_00855404`, then calls `CFeatureTexture__SetTagListIndexOrMinusOne` with `this+0x8`. |

Evidence counts:

- Fresh exports: `7` metadata rows, `7` tag rows, `7` DATA xref rows, `547` body-instruction rows, and `7` decompile rows.
- Xrefs remain vtable DATA refs from `0x005da880`, `0x005da808`, `0x005da830`, `0x005da81c`, `0x005da86c`, `0x005da844`, and `0x005da858`.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1037: `692/1408 = 49.15%`.
- Expanded static surface progress after Wave1037: `921/1493 = 61.69%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-072938_post_wave1037_feature_value_apply_strip_review_verified`, `19` files, `173968263` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected Wave341 feature apply rows still have coherent saved names, signatures, comments, tags, vtable DATA refs, instruction bodies, and decompile output.
- The saved record-offset comments still match fresh instruction/decompile evidence for all seven rows.
- The rows remain a static PhysicsScript bridge from named feature-value script objects into fields of records reachable through `DAT_00855404`.

What remains unproven:

- Runtime PhysicsScript loading/application behavior.
- Runtime feature behavior or mission-script outcomes.
- Concrete feature record/value object layouts beyond observed offsets.
- Exact source-body identity and local variable names/types.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1037; feature-value-apply-strip-review-wave1037; 0x0043bb30 CFeatureScalar18__ApplyToFeatureByName; 0x0043bc80 CFeatureFlag10__ApplyToFeatureByName; 0x0043c010 CFeatureTexture__ApplyToFeatureByName; DAT_00855404; 692/1408 = 49.15%; 921/1493 = 61.69%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-072938_post_wave1037_feature_value_apply_strip_review_verified; no mutation.

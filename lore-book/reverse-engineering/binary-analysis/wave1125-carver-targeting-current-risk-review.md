# Wave1125 Carver Targeting Current-Risk Review

Status: validated static tag-normalization evidence
Date: 2026-06-05
Tag: `wave1125-carver-targeting-current-risk-review`

Wave1125 accounts for `2 rows` from the Wave1108 current focused denominator as a score-23 Carver targeting current-risk cluster, moving current focused accounting to `135/1179 = 11.45%` of current focused candidates: 1179. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

This wave used fresh Ghidra export evidence and then saved tag-only normalization. It added `22 tags` and made no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x00422db0 CCarverAI__CheckNearbyEnemies` | Called by `0x00422b90 CCarverAI__UpdateAttackAndReschedule` at `0x00422ba7`. The body scans map-who entries around the Carver owner, checks unit-like enemy/context flags and owner equality, compares a height/field threshold, and calls `CCarverAI__SetLastAttackTime` on a qualifying candidate. |
| `0x00423510 CCarverGuide__AcquireNearestTargetReader` | Called by `0x00423490 CCarverGuide__HandleEvent` at `0x004234ad`. The body clears the active-reader slot at `+0x2c`, scans mapwho around owner `+0x18` with the wider 45.0-radius path, evaluates candidate distance/flag gates, and stores the nearest accepted target reader. |

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `190` / `2`.
- Pre tag export showed both rows had empty saved tag sets.
- Dry/apply/final-dry tag-normalization summaries: `updated=0 skipped=0 tags_added=22 missing=0 bad=0`; `updated=2 skipped=0 tags_added=22 missing=0 bad=0`; `updated=0 skipped=2 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `190` / `2`.
- Post tags include `static-reaudit`, `wave1125-carver-targeting-current-risk-review`, `wave1125-readback-verified`, `retail-binary-evidence`, `tag-normalized`, `comment-hardened`, and `carver-targeting`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`, `19` files, `175737735` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`.
- Prior context: Wave915 re-read both rows, Wave965 retained both as Carver init/combat/wing context, and Wave989 re-read the CarverGuide lifecycle path including `0x00423510`.

Boundary:

This is static Ghidra evidence. It does not prove runtime Carver AI behavior, runtime CarverGuide navigation behavior, target acquisition correctness, exact `CCarverAI`, `CCarverGuide`, target-reader, mapwho, or active-reader layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

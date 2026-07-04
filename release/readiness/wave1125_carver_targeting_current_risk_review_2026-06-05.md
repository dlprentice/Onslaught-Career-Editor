# Wave1125 Carver Targeting Current-Risk Review Readiness Note

Status: complete static tag-normalization evidence
Date: 2026-06-05
Scope: `wave1125-carver-targeting-current-risk-review`

Wave1125 accounts for `2 rows` from the next Wave1108 current focused candidates: 1179, as a score-23 Carver targeting current-risk cluster. Current focused accounting moves to `135/1179 = 11.45%`; static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`. This wave used fresh Ghidra export evidence and tag-only normalization with `22 tags`.

Representative anchors: `0x00422db0 CCarverAI__CheckNearbyEnemies` and `0x00423510 CCarverGuide__AcquireNearestTargetReader`.

Mutation status:

- Tag-only normalization.
- No rename.
- No signature change.
- No comment change.
- No function-boundary change.
- No executable-byte change.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `190` / `2`.
- Pre tag export showed both rows had empty saved tag sets.
- `ApplyCarverTargetingCurrentRiskWave1125.java dry`: `updated=0 skipped=0 tags_added=22 missing=0 bad=0`.
- `ApplyCarverTargetingCurrentRiskWave1125.java apply`: `updated=2 skipped=0 tags_added=22 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyCarverTargetingCurrentRiskWave1125.java final dry`: `updated=0 skipped=2 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `2` / `2` / `2` / `190` / `2`.
- Post tags include `static-reaudit`, `wave1125-carver-targeting-current-risk-review`, `wave1125-readback-verified`, `retail-binary-evidence`, `tag-normalized`, `comment-hardened`, and `carver-targeting`.
- Xrefs: `0x00422ba7` in `CCarverAI__UpdateAttackAndReschedule` calls `0x00422db0`; `0x004234ad` in `CCarverGuide__HandleEvent` calls `0x00423510`.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`, `19` files, `175737735` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-050726_post_wave1124_repairpad_current_risk_review_verified`.
- Prior context: Wave915 re-read both rows, Wave965 retained both as Carver init/combat/wing context, and Wave989 re-read the CarverGuide lifecycle path including `0x00423510`.

What this proves:

- The two target rows still exist in the saved Ghidra project.
- Names, signatures, comments, xrefs, instruction windows, and decompile rows remain coherent with the saved static Carver targeting evidence.
- The previously empty saved tag sets were normalized and read back after apply.
- The current-risk accounting advances from `133/1179 = 11.28%` to `135/1179 = 11.45%`.

What remains separate:

- Runtime Carver AI behavior.
- Runtime CarverGuide navigation or target acquisition behavior.
- Exact `CCarverAI`, `CCarverGuide`, target-reader, mapwho, or active-reader layouts.
- Exact source-body identity, because `Carver.cpp` source is absent from the current source snapshot.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

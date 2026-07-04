# Wave1121 Mixed Score-24 Current-Risk Review Readiness Note

Status: complete static evidence with one comment-only correction
Date: 2026-06-05
Scope: `wave1121-mixed-score24-current-risk-review`

Wave1121 re-read `4 rows` from the next Wave1108 current focused candidates: 1179, the score-24 mixed current-risk head. Current focused accounting moves to `122/1179 = 10.35%`; static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Representative anchors: `0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0`, `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0`, `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830`, and `0x005019c0 VFuncSlot_09_005019c0`.

Mutation status:

- `0x005019c0 VFuncSlot_09_005019c0` received a comment-only refresh and three tags. The stale phrase claiming `0x00501a10` remained unrecovered was replaced with the Wave961 recovery fact: `0x00501a10 CVertexShader__VFunc_02_00501a10`.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.

Evidence:

- Pre-mutation metadata/tag/xref/instruction/decompile exports: `4` / `4` / `42` / `1207` / `4`.
- `ApplyMixedScore24CurrentRiskWave1121.java` dry run: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0`.
- `ApplyMixedScore24CurrentRiskWave1121.java` apply: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyMixedScore24CurrentRiskWave1121.java` final dry run: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post-mutation metadata/tag/xref/instruction/decompile exports: `4` / `4` / `42` / `1207` / `4`.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`.

What this proves:

- The four target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows are coherent after the comment refresh.
- The current-risk accounting advances from `118/1179 = 10.01%` to `122/1179 = 10.35%`.

What remains separate:

- Runtime damage behavior.
- Runtime mesh collision behavior.
- Runtime shader/frontend behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

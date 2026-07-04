# Wave1127 Mixed Score-23 Current-Risk Review Readiness Note

Status: complete static tag-only normalization evidence
Date: 2026-06-05
Scope: `wave1127-mixed-score23-current-risk-review`

Wave1127 re-read and tag-normalized `6 rows` from the Wave1108 current focused denominator as a score-23 mixed current-risk cluster: `0x00405f80 CBattleEngine__VFunc_02_00405f80`, `0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending`, `0x00479200 Geometry__SelectClosestPointOnTriangleEdges`, `0x004804c0 CHiveBoss__SetVar`, `0x004f7460 Triangulate__InsertPointOrAppendVertex`, and `0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260`.

Current focused accounting advances to `144/1179 = 12.21%` of current focused candidates: 1179. The live regenerated focused candidates: 1178; remaining active focused work: 1035. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

fresh Ghidra export evidence summary:

- Pre metadata/tag/xref/instruction/decompile exports: `6` / `6` / `35` / `741` / `6`.
- Dry/apply/final-dry summaries: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 missing=0 bad=0`; `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 missing=0 bad=0`; `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `6` / `6` / `35` / `741` / `6`.
- Pre/post instruction exports match exactly.
- Queue quality refresh reported `total_functions=6410 commented_functions=6410`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`, `19` files, `175934343` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`.

Mutation boundary:

- Tag-only normalization.
- `41 tags` added.
- No rename, signature change, comment change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, or runtime-file mutation.

Claim boundary:

This proves saved static Ghidra read-back coherence for these six function rows. Runtime behavior, exact source-body identity, concrete layout semantics, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

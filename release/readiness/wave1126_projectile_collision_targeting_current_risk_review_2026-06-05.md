# Wave1126 Projectile Collision Targeting Current-Risk Review Readiness Note

Status: complete static comment/tag normalization evidence
Date: 2026-06-05
Scope: `wave1126-projectile-collision-targeting-current-risk-review`

Wave1126 accounts for `3 rows` from the Wave1108 current focused continuity denominator as a score-23 projectile collision targeting current-risk cluster. This wave uses fresh Ghidra export evidence. Current focused accounting moves to `138/1179 = 11.70%` of current focused candidates: 1179. The live regenerated focused candidates: 1178 after the `0x00426920` comment normalization drops that row below the focused threshold; remaining active focused work: 1041. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Representative anchors: `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory`, `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance`, and `0x004daba0 CRound__FindNearbyHostileWithinProjectileRadius`.

Mutation status:

- Comment/tag normalization.
- `19 tags` added.
- Two comments updated.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `3` / `3` / `7` / `291` / `3`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `3` / `3` / `7` / `291` / `3`.
- Post tags include `static-reaudit`, `wave1126-projectile-collision-targeting-current-risk-review`, `wave1126-readback-verified`, `retail-binary-evidence`, `comment-hardened`, `tag-normalized`, `current-risk-review`, and `projectile-collision-targeting`.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`, `19` files, `175901575` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`.
- Prior context: Wave919, Wave920, Wave1059, and Wave495.

What this proves:

- The three target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows remain coherent with the saved static projectile/collision targeting evidence.
- The stale comment caveat on the two CCollisionSeekingRound rows was normalized and read back after apply.
- The current-risk continuity accounting advances from `135/1179 = 11.45%` to `138/1179 = 11.70%`.

What remains separate:

- Runtime collision behavior.
- Runtime targeting behavior.
- Runtime projectile behavior.
- Exact CCollisionSeekingRound, CRound, map/who, target, owner/context, and round-config layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

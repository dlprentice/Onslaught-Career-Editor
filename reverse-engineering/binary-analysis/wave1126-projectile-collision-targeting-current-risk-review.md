# Wave1126 Projectile Collision Targeting Current-Risk Review

Status: complete static comment/tag normalization evidence
Date: 2026-06-05
Scope: `wave1126-projectile-collision-targeting-current-risk-review`

Wave1126 accounts for `3 rows` from the Wave1108 current focused continuity denominator as a score-23 projectile collision targeting current-risk cluster. This wave uses fresh Ghidra export evidence. Current focused accounting moves to `138/1179 = 11.70%` of current focused candidates: 1179. The live regenerated focused candidates: 1178 because `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` drops below the focused threshold after its stale/provisional comment caveat is normalized; remaining active focused work: 1041. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00425c60 CCollisionSeekingRound__FilterCollisionCandidateByTrajectory` | Calls `CCollisionSeekingRound__CheckCollisionFlags`, rejects same-owner/context target candidates, checks target state flags, samples the candidate center, asks this round for movement/trajectory context, and applies a trajectory/range test. |
| `0x00426920 CCollisionSeekingRound__ComputeScaledMapCellChebyshevDistance` | Compares packed map-cell coordinates after scaling cell depths to match, then returns a Chebyshev-style max absolute delta. |
| `0x004daba0 CRound__FindNearbyHostileWithinProjectileRadius` | Existing Wave495 CRound helper evidence: scans `CMapWho` around `this+0x1c/0x20/0x24`, uses radius from round-config `this+0xf0+0x90`, rejects the current target reader at `this+0xe8`, filters candidate flags, and returns the first candidate inside radius squared. |

Prior context anchors:

- Wave919 re-read collision-seeking round lifecycle/dispatch evidence.
- Wave920 re-read CRound projectile and targeting evidence.
- Wave1059 re-read collision-seeking round tail evidence and saved the first two rows with tags.
- Wave495 corrected the CRound helper owner/signature/comment at `0x004daba0`.

Mutation status:

- Comment/tag normalization.
- `19 tags` added.
- Two comments updated to remove stale tag/provisional caveats and replace them with bounded Wave1126 static read-back comments.
- No rename.
- No signature change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `3` / `3` / `7` / `291` / `3`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=2 tags_added=19 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyProjectileCollisionTargetingCurrentRiskWave1126.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `3` / `3` / `7` / `291` / `3`.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `G:\GhidraBackups\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`, `19` files, `175901575` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-053504_post_wave1125_carver_targeting_current_risk_review_verified`.

What this proves:

- The three target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved comments, tags, xrefs, instruction windows, and decompile rows are coherent with the bounded static projectile/collision targeting evidence.
- Wave1126 removed stale comment wording on the two CCollisionSeekingRound rows and read back the normalized comments/tags.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime collision behavior.
- Runtime targeting behavior.
- Runtime projectile behavior.
- Exact `CCollisionSeekingRound`, `CRound`, map/who, target, owner/context, and round-config layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

# Wave1127 Mixed Score-23 Current-Risk Review

Status: complete static tag-only normalization evidence
Date: 2026-06-05
Scope: `wave1127-mixed-score23-current-risk-review`

Wave1127 accounts for `6 rows` from the Wave1108 current focused continuity denominator as a score-23 mixed current-risk cluster. This wave uses fresh Ghidra export evidence and tag-only normalization. Current focused accounting moves to `144/1179 = 12.21%` of current focused candidates: 1179. The live regenerated focused candidates: 1178; remaining active focused work: 1035. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Covered anchors:

| Address | Static evidence |
| --- | --- |
| `0x00405f80 CBattleEngine__VFunc_02_00405f80` | BattleEngine finalization-vfunc evidence: clears the `+0x250` linked set, stops controller vibration when present, clears the `+0x5f8` particle/effect link, then calls the CUnit vfunc-02 cleanup path. |
| `0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending` | Opening-animation callback evidence: DATA xref `0x005d9080`, state field `+0x254`, timer field `+0x25c`, `s_opening_00623ba4`, mesh animation lookup, and vcall `+0xf0`. |
| `0x00479200 Geometry__SelectClosestPointOnTriangleEdges` | Geometry/collision helper evidence: clamps projected points on all three triangle edges and writes the nearest candidate to `outClosest`. |
| `0x004804c0 CHiveBoss__SetVar` | HiveBoss config evidence: handles `hb_*` config strings for guide velocities, rotation speeds, safe distance, and minimum ground-clearance style fields before falling back to the base SetVar path. |
| `0x004f7460 Triangulate__InsertPointOrAppendVertex` | Triangulate work-object evidence: scans active triangles, calls `Triangulate__SplitTriangleAtPointAndLegalizeEdges`, or appends the XY point when no triangle accepts it. |
| `0x004f9260 SharedUnitVFunc__BuildField164TargetVectorContext_004f9260` | Shared unit-family vtable evidence: multiple unit-family DATA slots point to the body; it builds a stack-local vector/context block when `this+0x164` is present and stays bounded before `0x004f9430 CUnit__ApplyRandomDestructibleDamageBurst`. |

Mutation status:

- Tag-only normalization.
- `41 tags` added.
- No rename.
- No signature change.
- No comment change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

Evidence:

- Pre metadata/tag/xref/instruction/decompile exports: `6` / `6` / `35` / `741` / `6`.
- `ApplyMixedScore23CurrentRiskWave1127.java dry`: `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 missing=0 bad=0`.
- `ApplyMixedScore23CurrentRiskWave1127.java apply`: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplyMixedScore23CurrentRiskWave1127.java final dry`: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post metadata/tag/xref/instruction/decompile exports: `6` / `6` / `35` / `741` / `6`.
- Pre/post instruction exports match exactly.
- Queue quality refresh after the Ghidra write reported `total_functions=6410 commented_functions=6410`.
- Final backup after the queue refresh: `[maintainer-local-ghidra-backup-root]\BEA_20260605-071212_post_wave1127_mixed_score23_current_risk_review_verified`, `19` files, `175934343` bytes, `DiffCount=0`.
- Previous completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-061135_post_wave1126_projectile_collision_targeting_current_risk_review_verified`.

What this proves:

- The six target rows still exist in the saved Ghidra project with the expected names and signatures.
- The saved tags include `wave1127-mixed-score23-current-risk-review`, `wave1127-readback-verified`, `current-risk-review`, `score-23-current-risk`, and `tag-normalized`.
- The comments, xrefs, instruction windows, and decompile rows remain coherent with the bounded static evidence from prior waves.
- The Ghidra project was backed up after the write and after the queue refresh.

What remains separate:

- Runtime behavior.
- Exact source-body identity.
- Concrete layout semantics.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

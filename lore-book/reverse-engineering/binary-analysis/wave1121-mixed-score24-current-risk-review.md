# Wave1121 Mixed Score-24 Current-Risk Review

Status: validated static evidence with one comment-only Ghidra correction
Date: 2026-06-05
Tag: `wave1121-mixed-score24-current-risk-review`

Wave1121 accounts for `4 rows` from the Wave1108 current focused denominator as the score-24 mixed current-risk head, moving current focused accounting to `122/1179 = 10.35%` of current focused candidates: 1179. Static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

The wave used fresh Ghidra exports before and after mutation. Three rows were read-only coherent. One row, `0x005019c0 VFuncSlot_09_005019c0`, had a stale saved comment that still described `0x00501a10` as an unrecovered CVertexShader no-function boundary. Wave961 later recovered that slot as `0x00501a10 CVertexShader__VFunc_02_00501a10`, so Wave1121 refreshed the `0x005019c0` comment and added `wave1121-mixed-score24-current-risk-review` / `wave1121-readback-verified` tags. No rename, signature change, function-boundary change, or executable-byte change was made.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x004037a0 SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0` | Existing Wave1086 evidence remains coherent: DATA refs from shared unit-family vtables, body forwards to `CUnit__ApplyDamage`, checks `this+0xf8` / flags / `this+0x258`, dispatches vtable slot `+0x160` selector `0x19`, and returns with `RET 0x10`. |
| `0x004ac6e0 CMeshCollisionVolume__VFunc_03_004ac6e0` | Existing Wave446/Wave1098 mesh collision slot-3 evidence remains coherent: CMeshCollisionVolume vtable DATA xref `0x005d95d4`, per-part bounds refresh, swept-sphere bounds/mesh-part tests, contact candidate accumulation, and contact normal/plane resolution. |
| `0x004ad830 CMeshCollisionVolume__VFunc_04_004ad830` | Existing Wave446/Wave1098 mesh collision slot-4 evidence remains coherent: CMeshCollisionVolume vtable DATA xref `0x005d95d8`, segment endpoint construction, mesh-part line/triangle bucket helpers, `Geometry__IntersectSegmentTriangleAndStoreHit`, and transformed winning hit/normal output. |
| `0x005019c0 VFuncSlot_09_005019c0` | Wave1121 comment-only correction: the body remains the shared `XOR EAX,EAX; RET` default-false stub used by CVertexShader slots 1 and 4 plus other RTTI-backed owner rows. The refreshed comment now records that former slot-2 no-function boundary `0x00501a10` was recovered by Wave961 as `CVertexShader__VFunc_02_00501a10`. |

Evidence:

- Pre-mutation exports: `4` metadata rows, `4` tag rows, `42` xref rows, `1207` instruction rows, and `4` decompile rows.
- Apply dry run: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0`.
- Apply: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 tags_added=3 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Final dry run: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0`.
- Post-mutation exports: `4` metadata rows, `4` tag rows, `42` xref rows, `1207` instruction rows, and `4` decompile rows.
- Verified backup: `G:\GhidraBackups\BEA_20260605-033658_post_wave1121_mixed_score24_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`.

Boundary:

This is static Ghidra/source-reference evidence. It does not prove runtime damage behavior, runtime mesh collision behavior, runtime shader/frontend behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

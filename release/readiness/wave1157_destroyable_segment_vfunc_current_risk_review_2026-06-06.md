# Wave1157 Destroyable Segment VFunc Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1157-destroyable-segment-vfunc-current-risk-review`

Wave1157 re-read `12 destroyable-segment vfunc current-risk rows` with fresh Ghidra exports and made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, or runtime-file mutation.

Probe token anchor: Wave1157; wave1157-destroyable-segment-vfunc-current-risk-review; 465/1179 = 39.44%; 12 destroyable-segment vfunc current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 714; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consults used; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 694 instruction rows; CDestroyableSegment__VFunc_03_ApplyDamage; CDestroyableSegment__VFunc_08_HandleSegmentBreak; CDestroyableSegment__VFunc_10_SpawnRubbleEffects; CDestroyableCoreSegment__VFunc_03_ApplyDamage; CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex; CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields; G:\GhidraBackups\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `12` rows, `targets=12 found=12 missing=0`.
- `pre-tags.tsv`: `12` rows, `missing=0`.
- `pre-xrefs.tsv`: `23 xref rows`, including vtable DATA refs and direct break/rubble helper calls.
- `pre-instructions.tsv`: `694 instruction rows`, `targets=12 missing=0`.
- `pre-decompile/index.tsv`: `12` rows, `targets=12 dumped=12 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-235134_post_wave1157_destroyable_segment_vfunc_current_risk_review_verified`, local Ghidra project root, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Codex subagent usage: read-only consults audited candidate/accounting status and system-map coverage; Codex root selected, exported, audited, backed up, and kept the tranche read-only.

Reviewed row groups:

| Group | Static read-back evidence |
| --- | --- |
| Damage scale helpers | `CDestroyableSegment__VFunc_11_RecomputeDamageScaleFields`, `CDestroyableCoreSegment__VFunc_11_RecomputeCoreDamageScaleFields`, and `CDestroyableEndSegment__VFunc_11_RecomputeEndDamageScaleFields` keep the `this+0x34`, `scaleFactor`, `divisor`, `+0x0c`, and `+0x10` damage-scale surface bounded without assigning final field names. |
| Apply-damage helpers | Base, core, and swap slot-3 helpers subtract damage or update stage state, record last damage amount/time, clamp depleted state, and dispatch break/rubble paths where observed. |
| Break and rubble helpers | `CDestroyableSegment__VFunc_08_HandleSegmentBreak`, `CDestroyableSwapSegment__VFunc_08_HandleSegmentBreak`, and `CDestroyableSegment__VFunc_10_SpawnRubbleEffects` tie break state to child destruction, link updates, rubble/effects, landscape damage, and configured pickup paths. |
| Variant helpers | `CDestroyableCoreSegment__VFunc_07_GetCoreField48`, `CDestroyableCoreSegment__VFunc_06_CheckParentBreakGate`, and `CDestroyableSwapSegment__VFunc_04_GetDamageStageIndex` preserve the core/swap/end vtable variant map without claiming exact concrete layouts. |

Accounting after Wave1157:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%` historical-retired/non-reconstructable provenance only.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `465/1179 = 39.44%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 714.

This is static Ghidra evidence only. Runtime destructable-segment damage/break/rubble/cascade/pickup behavior, exact event payload schema, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

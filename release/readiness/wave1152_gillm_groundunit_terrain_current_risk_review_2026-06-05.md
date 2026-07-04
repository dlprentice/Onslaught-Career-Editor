# Wave1152 GillM/GroundUnit Terrain Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1152-gillm-groundunit-terrain-current-risk-review`

Wave1152 re-read five GillM/GroundUnit terrain current-risk rows with fresh Ghidra exports and made no mutation: no rename, signature change, comment change, tag change, function-boundary change, executable-byte change, BEA launch, installed-game mutation, save mutation, runtime-file mutation, or Codex subagent.

Probe token anchor: Wave1152; wave1152-gillm-groundunit-terrain-current-risk-review; 373/1179 = 31.64%; 5 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 806; current risk candidates: 6166; GillM/GroundUnit terrain current-risk review; fresh Ghidra export; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CGillM__ComputeTerrainClearanceNoiseScale; CGillM__ComputeLateralSlopeAlignment; CGroundUnit__UpdateLinkedEffectsByHeightClearance; CGroundUnit__MarkDestroyedAndResetState; CGroundUnit__ClearLinkedThingFlagsAndResetCounter; [maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Fresh evidence:

- `pre-metadata.tsv`: `5` rows, `targets=5 found=5 missing=0`.
- `pre-tags.tsv`: `5` rows, `missing=0`.
- `pre-xrefs.tsv`: `21` rows.
- `pre-instructions.tsv`: `584` instruction rows, `targets=5 missing=0`.
- `pre-decompile/index.tsv`: `5` rows, `targets=5 dumped=5 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Previous completed backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified`.
- Codex subagent usage: none for this slice; Codex root selected and audited the tranche locally.

Reviewed rows:

| Address | Static read-back |
| --- | --- |
| `0x00479f30 CGillM__ComputeTerrainClearanceNoiseScale` | GillM movement/terrain helper that samples two static-shadow heights and returns a terrain clearance/noise scalar. |
| `0x0047a0b0 CGillM__ComputeLateralSlopeAlignment` | GillM lateral terrain-alignment helper using heading field `+0x114` and heightfield-normal sampling. |
| `0x0047c970 CGroundUnit__UpdateLinkedEffectsByHeightClearance` | GroundUnit linked-effect and motion/attachment update helper keyed by height clearance. |
| `0x0047ce80 CGroundUnit__MarkDestroyedAndResetState` | GroundUnit destruction cleanup wrapper that clears `+0x25c` on success. |
| `0x0047cea0 CGroundUnit__ClearLinkedThingFlagsAndResetCounter` | GroundUnit linked-effect cleanup helper over the `+0x1d4/+0x1e4` state. |

Accounting after Wave1152:

- Static closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `373/1179 = 31.64%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 806.

This is static Ghidra evidence only. Runtime GillM movement, runtime GroundUnit effect/destruction behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

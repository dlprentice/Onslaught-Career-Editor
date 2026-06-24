# Wave1152 GillM/GroundUnit Terrain Current-Risk Review

Wave1152 (`wave1152-gillm-groundunit-terrain-current-risk-review`) accounts for `5 current-risk rows` from the Wave1108 current focused denominator as a GillM/GroundUnit terrain current-risk review. It is a fresh Ghidra read-only review with no mutation and no Codex subagent.

Probe token anchor: Wave1152; wave1152-gillm-groundunit-terrain-current-risk-review; 373/1179 = 31.64%; 5 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 806; current risk candidates: 6166; GillM/GroundUnit terrain current-risk review; fresh Ghidra export; read-only review; no mutation; no Codex subagent; 0 / 0 / 0; 6411/6411 = 100.00%; CGillM__ComputeTerrainClearanceNoiseScale; CGillM__ComputeLateralSlopeAlignment; CGroundUnit__UpdateLinkedEffectsByHeightClearance; CGroundUnit__MarkDestroyedAndResetState; CGroundUnit__ClearLinkedThingFlagsAndResetCounter; G:\GhidraBackups\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-201419_post_wave1151_mixed_score21_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Evidence

| Address | Current name | Static evidence |
| --- | --- | --- |
| `0x00479f30` | `CGillM__ComputeTerrainClearanceNoiseScale` | GillM-family movement/terrain helper reached from the CMCGillM slot-wrapper region; gates on fields including `+0x274/+0x244`, samples two static-shadow heights, and scales a terrain clearance/noise scalar. |
| `0x0047a0b0` | `CGillM__ComputeLateralSlopeAlignment` | GillM-family lateral terrain-alignment helper using heading field `+0x114`, heightfield-normal sampling, and lateral slope projection. |
| `0x0047c970` | `CGroundUnit__UpdateLinkedEffectsByHeightClearance` | CGroundUnit vtable slot 66 helper; updates linked `+0x1d4/+0x1e4` effect state, height-clearance attachment state, and calls `CUnit__UpdateMotionAttachmentsAndEffects`. |
| `0x0047ce80` | `CGroundUnit__MarkDestroyedAndResetState` | CGroundUnit vtable slot 50 helper; calls `CUnit__MarkDestroyedAndCleanupLinks`, clears `+0x25c` on success, and returns success/failure. |
| `0x0047cea0` | `CGroundUnit__ClearLinkedThingFlagsAndResetCounter` | Walks the GroundUnit linked set at `+0x1d4`, calls `ParticleEffectLink__SetHandleStateAndClear` for each owner-link cell, and clears `+0x1e4`. |

Fresh primary exports verified `5` metadata rows, `5` tag rows, `21` xref rows, `584` body-instruction rows, and `5` decompile rows. The verified Ghidra project backup is `G:\GhidraBackups\BEA_20260605-203535_post_wave1152_gillm_groundunit_terrain_current_risk_review_verified` with `19` files, `175967111` bytes, `DiffCount=0`, and `HashDiffCount=0`.

## Boundary

This wave proves static Ghidra read-back coherence for the selected GillM/GroundUnit rows only. Runtime GillM movement, runtime GroundUnit effect/destruction behavior, exact layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

# Wave1133 Feature/Pickup Current-Risk Review Readiness

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1133-feature-pickup-current-risk-review`

Wave1133 re-read six feature/pickup current-risk rows with fresh Ghidra metadata, tag, xref, instruction, and decompile exports: `0x00442710 CDestroyableSegment__SpawnConfiguredPickup`, `0x0044ca30 CFeature__Init`, `0x0044cbe0 CFeature__ShutdownAndRemoveFromWorld`, `0x0044cee0 CFeature__MaybeSpawnRandomPickupFromData`, `0x0044e300 PickupSpawn__MaybeSpawnAttachedPickupFromFrame_0044e300`, and `0x004fd230 CUnit__SpawnProfileDropPickup`.

Probe anchor: Wave1133; `wave1133-feature-pickup-current-risk-review`; `6 rows`; `184/1179 = 15.61%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995; feature/pickup spawn bridge cluster; fresh Ghidra export; read-only review; no mutation; static debt `0 / 0 / 0`; verified backup `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`; previous completed backup `G:\GhidraBackups\BEA_20260605-093432_post_wave1132_component_ai_current_risk_review_verified`.

Read-back evidence:

- Primary exports: `6` metadata rows, `6` tag rows, `22` xref rows, `681` instruction rows, and `6` decompile rows.
- Context exports: `2` metadata rows, `2` tag rows, `4` xref rows, `180` instruction rows, and `2` decompile rows.
- Context rows: `0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch` and `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`.
- Current focused accounting: `184/1179 = 15.61%`; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 995.
- Verified backup: `G:\GhidraBackups\BEA_20260605-100620_post_wave1133_feature_pickup_current_risk_review_verified`, `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Mutation status:

- No Ghidra mutation.
- No rename.
- No signature change.
- No comment change.
- No tag change.
- No function-boundary change.
- No executable-byte change.
- No BEA launch, installed-game mutation, or runtime-file mutation.

What this proves:

- The six target rows still exist in the saved Ghidra project with expected saved names and signatures.
- Fresh xrefs, instruction windows, and decompile rows still support the current feature/pickup spawn static contracts.
- The project backup was verified after the read-only evidence wave.

What remains separate:

- Runtime pickup/drop behavior.
- Runtime feature lifecycle behavior.
- Exact source-body identity and concrete layouts.
- BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity.

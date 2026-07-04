# Wave1120 Mixed Score-25 Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1120-mixed-score25-current-risk-review`

Wave1120 re-read `8 rows` from the next Wave1108 current focused candidates: 1179, the score-25 mixed current-risk head, with a fresh read-only Ghidra export and no mutation. Current focused accounting moves to `118/1179 = 10.01%`; static closure debt remains `0 / 0 / 0` for commentless / exact-undefined / `param_N`.

Representative anchors: `0x00405d80 CParticleManager__RemoveFromGlobalList_Thunk`, `0x0040dfb0 CGeneralVolume__SpawnPickupAndDispatch`, `0x004bfe00 CUnit__dtor_base_Thunk_004bfe00`, `0x004d3630 CPod__VFunc_66_UpdateMotionAndAccumulateScalar`, `0x004ef100 CUnit__VFunc64_SpawnConfiguredPickupThreeTimes`, `0x0052d3d0 CAsmInstruction__SpawnFromOpcode`, `0x0052ec60 CDataType__CreateFromType`, and `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`.

Evidence:

- Fresh metadata export: `8` rows, `targets=8 found=8 missing=0`.
- Fresh tag export: `8` rows, `missing=0`; the two older rows at `0x00405d80` and `0x0040dfb0` still have empty saved tag strings and were not tag-normalized in this read-only pass.
- Fresh xref export: `59` rows.
- Fresh instruction export: `936` rows, `targets=8 missing=0`.
- Fresh decompile export: `8` rows, `targets=8 dumped=8 missing=0 failed=0`.
- Mutation status: no mutation, no rename, no signature change, no comment/tag write, no executable-byte change.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`.

What this proves:

- The eight target rows still exist in the saved Ghidra project.
- Names, signatures, comments, xrefs, instruction windows, and decompile rows are coherent with existing bounded ParticleManager, GeneralVolume, CUnit, CPod, MissionScript datatype/opcode, and CFastVB parser evidence.
- The current-risk accounting advances from `110/1179 = 9.33%` to `118/1179 = 10.01%` without requiring a Ghidra mutation.

What remains separate:

- Runtime particle/list behavior.
- Runtime pickup/drop behavior.
- Runtime unit cleanup/pickup behavior.
- Runtime pod motion behavior.
- Runtime MissionScript behavior.
- Runtime FastVB parser/render behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

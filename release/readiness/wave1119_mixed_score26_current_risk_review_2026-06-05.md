# Wave1119 Mixed Score-26 Current-Risk Review Readiness Note

Status: complete static read-only evidence
Date: 2026-06-05
Scope: `wave1119-mixed-score26-current-risk-review`

Wave1119 re-read `10 rows` from the next Wave1108 current focused candidates: 1179, the score-26 mixed current-risk head, with a fresh read-only Ghidra export and no mutation. Current focused accounting moves to `110/1179 = 9.33%`.

Representative anchors: `0x004d05e0 CPauseMenu__dtor_base`, `0x004d0e40 CGameMenu__InitBase`, `0x004d1750 CSimpleGameMenu__dtor_base`, `0x004d3020 CEngine__SetOptionValueAndNotifyTarget`, `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader`, `0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor`, `0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0`, `0x0050ee90 CUnit__scalar_deleting_dtor`, `0x005b85c0 Math__Atan2ApproxPacked`, and `0x005b86c0 CFastVB__FastAcosApprox_Scalar`.

Evidence:

- Fresh metadata export: `10` rows, `targets=10 found=10 missing=0`.
- Fresh tag export: `10` rows, `missing=0`.
- Fresh xref export: `67` rows.
- Fresh instruction export: `1170` rows, `targets=10 missing=0`.
- Fresh decompile export: `10` rows, `targets=10 dumped=10 missing=0 failed=0`.
- Mutation status: no mutation, no rename, no signature change, no comment/tag write, no executable-byte change.
- Backup: `G:\GhidraBackups\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`.

What this proves:

- The ten target rows still exist in the saved Ghidra project.
- Names, signatures, comments, tags, xrefs, instruction windows, and decompile rows are coherent with the existing bounded PauseMenu, CEngine, RepairPadAI, SafeSide, shared Unit, CUnit, and FastVB/math evidence.
- The current-risk accounting advances from `100/1179 = 8.48%` to `110/1179 = 9.33%` without requiring a Ghidra mutation.

What remains separate:

- Runtime UI behavior.
- Runtime repair behavior.
- Runtime faction-anchor behavior.
- Runtime unit behavior.
- Runtime math behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Visual QA.
- Rebuild parity.

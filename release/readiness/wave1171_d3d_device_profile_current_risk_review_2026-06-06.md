# Wave1171 D3D Device Profile Current-Risk Readiness Note

Status: complete static read-only evidence
Date: 2026-06-06
Scope: `wave1171-d3d-device-profile-current-risk-review`

Wave1171 re-read two D3D device profile current-risk rows: `D3DDeviceProfileTable__GetAdapterRecord` and `D3DDeviceProfile__PackDeviceIndexKey`.

Fresh exports verified `2` metadata rows, `2` tag rows, `3` xref rows, `54` instruction rows, and `2` decompile rows. The pass made no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change. A Codex read-only consult returned a different message/particle candidate and was deferred; Codex root selected this D3D slice locally.

Current accounting after Wave1171:

- Static closure: `6411/6411 = 100.00%`
- Static debt: `0 / 0 / 0`
- Expanded post-100 static surface: `1560/1560 = 100.00%`
- Wave911 focused: historical-retired/non-reconstructable at `812/1408 = 57.67%`
- Wave911 top-500: `500/500 = 100.00%`
- Wave1108 current focused accounting: `668/1179 = 56.66%`
- Remaining active focused work: `511`

Verified backup: `G:\GhidraBackups\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified`, `19` files, `176065415` bytes, `DiffCount=0`, `HashDiffCount=0`.

Claim boundary: static retail Ghidra evidence only. Runtime Direct3D device/profile selection behavior, exact display/profile table layout, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1171; wave1171-d3d-device-profile-current-risk-review; 668/1179 = 56.66%; 2 D3D device profile current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 511; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult deferred; 0 / 0 / 0; 6411/6411 = 100.00%; 3 xref rows; 54 instruction rows; D3DDeviceProfileTable__GetAdapterRecord; D3DDeviceProfile__PackDeviceIndexKey; OptionsTail_Write; OptionsTail_Read; G:\GhidraBackups\BEA_20260606-064430_post_wave1171_d3d_device_profile_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

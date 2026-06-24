# Wave1197 FEPBEConfig Frontend Residual Current-Risk Review

Status: complete static read-back evidence
Date: 2026-06-06
Tag: `wave1197-fepbeconfig-frontend-residual-current-risk-review`

Wave1197 accounts for `4 FEPBEConfig/frontend residual score15-16 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It uses fresh Ghidra metadata, tag, xref, instruction, and decompile exports plus saved comment/tag normalization to make these frontend config residual rows explicit rebuild-grade static contracts.

The pass preserved existing names and signatures. It made no rename, no signature change, no function-boundary change, and no executable-byte change.

## Counted Rows

| Address | Function | Static contract |
| --- | --- | --- |
| `0x0044fa90` | `CFEPBEConfig__Init` | DATA ref `0x005dba3c`; corrected boundary at `0x0044fa90` instead of stale mid-prologue `0x0044fa93`; initializes page/config state, optional preview mesh/animation state, reads `data\WorldHeaders.dat` through `CDXMemBuffer`, traces `beconf::init() 0-5`, calls the load vfunc for each header, and ends before `CFEPBEConfig__Cleanup`. |
| `0x0044eb30` | `CFEPMultiplayerStart__SetConfigDescriptionByIndex` | Call from `CFEPMultiplayerStart__Render` at `0x0051efa8`; walks selected config list `DAT_0089d94c`, selects `config_index`, matches against global config/profile list `DAT_006602a0`, maps type ids `1..5` to frontend text ids, and falls back to `Unknown Configuration`. |
| `0x0044f530` | `CFEPBEConfig__PlayWeaponSound` | Call from `CFEPBEConfig__Render` at `0x00451044`; resolves selected config through `DAT_0089da34/DAT_0089d94c`, matches `DAT_006602a0`, uses primary weapon-name record fields `+0x40/+0x48`, shared weapon-name table `DAT_008553e8`, weapon field `+0x0f`, and fallback `Unknown Weapon`. |
| `0x0044f830` | `CFEPBEConfig__PlayWeaponSoundAlt` | Call from `CFEPBEConfig__Render` at `0x0045117f`; follows the same selected config/list path as the primary helper but uses alternate weapon-name fields `+0x50/+0x58`, shared weapon-name table `DAT_008553e8`, weapon field `+0x0f`, and fallback `Unknown Weapon`. |

## Evidence

| Item | Result |
| --- | --- |
| Pre/post rows | `4` metadata rows, `4` tag rows, `4 xref rows`, `860 instruction rows`, and `4 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0` |
| Apply | `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=52 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `G:\GhidraBackups\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `885/1179 = 75.06%`; current risk candidates: 6166; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 294; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Boundary

This wave proves static retail Ghidra read-back for the selected FEPBEConfig/frontend residuals and records their rebuild-grade static contracts. It does not prove exact source-body identity, concrete FEPBEConfig/config/list/profile/weapon/text/audio layouts, runtime frontend/config loading behavior, runtime frontend audio/text behavior, BEA patching behavior, rebuild parity, or no-noticeable-difference parity.

Codex read-only consults used; no Cursor/Composer.

Probe token anchor: Wave1197; wave1197-fepbeconfig-frontend-residual-current-risk-review; 885/1179 = 75.06%; 4 FEPBEConfig/frontend residual score15-16 current-risk rows; current focused candidates: 1142; live regenerated current focused candidates: 1142; remaining active focused work: 294; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=4 skipped=0; comment_only_updated=4; tags_added=52; final dry updated=0 skipped=4; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CFEPBEConfig__Init; CFEPMultiplayerStart__SetConfigDescriptionByIndex; CFEPBEConfig__PlayWeaponSound; CFEPBEConfig__PlayWeaponSoundAlt; 0 / 0 / 0; 6411/6411 = 100.00%; 4 xref rows; 860 instruction rows; 4 decompile rows; G:\GhidraBackups\BEA_20260606-211310_post_wave1197_fepbeconfig_frontend_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.

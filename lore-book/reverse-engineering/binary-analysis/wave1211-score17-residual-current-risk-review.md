# Wave1211 Score-17 Residual Current-Risk Review

Status: complete static read-back evidence; historical artifact committed
Date: 2026-06-07
Tag: `wave1211-score17-residual-current-risk-review`

Wave1211 accounts for `8 score-17 residual current-risk rows` from the `wave1108-current-risk-rank` continuity denominator. This is a mixed residual score-band closure wave: actor grounding, repair-pad bounds, radar warning, active-reader formation conflict resolution, squad debug/render virtual evidence, script variable fallback, D3D depth/stencil format selection, and a CRT SEH frame helper.

The Ghidra write was tag-only normalization: added Wave1211/current-risk/read-back/rebuild-grade tags with `tags_added=41`. It made no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer.

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x00402030` | `CActor__StickToGround` | Source-backed actor helper calls `CThing::StickToGround`, then copies current position/vector dwords into old-position storage (`mOldPos=mPos`). |
| `0x0040c5b0` | `CRepairPadAI__IsWithinRepairBounds` | Leaf repair-pad docking bounds helper called by `CRepairPadAI__IsCompatibleDockCandidate`; compares candidate float thresholds at `+0xf8/+0xfc` against the referenced bounds record. |
| `0x004d66b0` | `CRadarWarningReceiver__Update` | Event-4000 radar warning update loop scans `DAT_008551a0`, maintains threat entries, sets forward-threat state, schedules/reschedules events, and plays event `0x0fa2` when threat count grows. |
| `0x004e97e0` | `CGenericActiveReader__SwapWithCandidateIfFormationCloser` | Active-reader formation conflict helper compares current and cross-assigned formation errors, then swaps readers through `CGenericActiveReader__SetReader` when the candidate pairing is closer. |
| `0x004e9f00` | `CSquadNormal__VFunc_52_004e9f00` | CSquadNormal render/debug-style virtual with vtable DATA ref `0x005df1c4`; calls `CUnit__RenderWithIdentityWorldAndShadowProbe`, samples static-shadow heightfield `0x006fadc8`, and emits beam/debug-volume render evidence. |
| `0x004f45e0` | `CComplexThing__SetVar` | Source-parity fallback for unknown script variable names; `RET 0x8` preserves two stack arguments and the body prints the unknown-variable warning. |
| `0x0052a830` | `CD3DApplication__FindDepthStencilFormat` | Source-aligned D3D depth/stencil format selector called by `CD3DApplication__BuildDeviceList`; `RET 0x10` preserves adapter/device/target/out-parameter stack shape. |
| `0x005d06f0` | `CRT__InitSehFrameNoop` | Compact CRT SEH-frame setup helper called by `CDXTexture__InitCpuVendorAndSimdFlags`; instruction evidence installs a frame through `FS:[0]` while preserving the existing Wave900 name/signature boundary. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Primary pre/post exports | `8` metadata rows, `8` tag rows, `106 xref rows`, `1132 instruction rows`, and `8 decompile rows` |
| Context exports | `15` metadata rows, `15` tag rows, `217 context xref rows`, `3103 context instruction rows`, and `15 context decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 tags_removed=0 missing=0 bad=0` |
| Apply | `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=41 tags_removed=0 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 tags_removed=0 missing=0 bad=0` |
| Backup | `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Active current-risk unique-address accounting is now `1110/1179 = 94.15%`; remaining active focused work: 69. The legacy additive counter is deprecated (`1141/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Runtime actor grounding, repair-pad docking, radar warning/HUD/audio behavior, squad/formation behavior, script variable behavior, D3D runtime device-selection behavior, CRT exception behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1211; wave1211-score17-residual-current-risk-review; 1110/1179 = 94.15%; 8 score-17 residual current-risk rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 69; current risk candidates: 6166; fresh Ghidra export; tag-only normalization; tags_added=41; final dry updated=0 skipped=8; no rename; no signature change; no comment change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CActor__StickToGround; CRepairPadAI__IsWithinRepairBounds; CRadarWarningReceiver__Update; CGenericActiveReader__SwapWithCandidateIfFormationCloser; CSquadNormal__VFunc_52_004e9f00; CComplexThing__SetVar; CD3DApplication__FindDepthStencilFormat; CRT__InitSehFrameNoop; 0 / 0 / 0; 6411/6411 = 100.00%; 106 xref rows; 1132 instruction rows; 8 decompile rows; 217 context xref rows; 3103 context instruction rows; 15 context decompile rows; G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

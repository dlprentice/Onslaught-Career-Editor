# Wave1211 Score-17 Residual Current-Risk Review Readiness Note

Status: complete static read-back evidence; historical artifact committed
Date: 2026-06-07
Scope: `wave1211-score17-residual-current-risk-review`

Wave1211 tag-normalized 8 score-17 residual current-risk rows after fresh Ghidra pre/context/post exports. The pass added `wave1211-score17-residual-current-risk-review`, `wave1211-readback-verified`, `current-risk-review`, `score17-residual`, and `rebuild-grade-static-contract` tags where missing. It made no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change.

Evidence counts:

- Primary exports: `8` metadata rows, `8` tag rows, `106 xref rows`, `1132 instruction rows`, and `8 decompile rows`.
- Context exports: `15` metadata rows, `15` tag rows, `217 context xref rows`, `3103 context instruction rows`, and `15 context decompile rows`.
- Dry/apply/final dry: `tags_added=41`; apply `updated=8 skipped=0`; final dry `updated=0 skipped=8`.
- Queue refresh: `6411/6411 = 100.00%`, `0 / 0 / 0`, current risk candidates: 6166, current focused candidates: 1127, live regenerated current focused candidates: 1127.
- Active current-risk accounting: `1110/1179 = 94.15%`; remaining active focused work: 69; legacy additive counter is deprecated (`1141/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Verified backup: `G:\GhidraBackups\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`, 19 files, 176425863 bytes, `DiffCount=0`, `HashDiffCount=0`.

Measurement anchors: unique-address accounting; fresh Ghidra export; final dry updated=0 skipped=8; `static-reaudit-current-risk-ledger.json`; `static-reaudit-measurement-register.md`; `wave1108-current-risk-rank`; Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Anchors: `CActor__StickToGround`, `CRepairPadAI__IsWithinRepairBounds`, `CRadarWarningReceiver__Update`, `CGenericActiveReader__SwapWithCandidateIfFormationCloser`, `CSquadNormal__VFunc_52_004e9f00`, `CComplexThing__SetVar`, `CD3DApplication__FindDepthStencilFormat`, and `CRT__InitSehFrameNoop`.

Claim boundary: this is fresh static Ghidra evidence and tag-only normalization. Runtime actor grounding, repair-pad docking, radar warning/HUD/audio behavior, squad/formation behavior, script variable behavior, D3D runtime device-selection behavior, CRT exception behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof. Codex read-only consults used; no Cursor/Composer; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

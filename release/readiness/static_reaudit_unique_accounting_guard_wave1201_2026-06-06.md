# Static Re-Audit Unique Accounting Guard Wave1201

Status: complete accounting refresh
Date: 2026-06-06
Scope: `static-reaudit-unique-accounting-guard-wave1201`

Wave1201 (`wave1201-frontend-text-menu-current-risk-review`) uses the `wave1108-current-risk-rank` current-risk denominator, focused threshold `15`, and unique-address accounting from `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`.

Measured status:

| Track | Value |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Corrected current-risk reviewed rows | `1042/1179 = 88.38%` |
| Remaining active focused work | `137` |
| Current risk candidates | `6166` |
| Current focused candidates | `1141` |
| Live regenerated current focused candidates | `1141` |

Wave1201 accounts for `25 frontend/text/menu current-risk rows` with fresh Ghidra export evidence and read-only review. Fresh exports verified `78 xref rows`, `1264 instruction rows`, and `25 decompile rows`. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Probe token anchor: current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 137; current risk candidates: 6166; fresh Ghidra export; read-only review; TextLayout__WrapWideTextToFixedLines; CGameInterface__VFunc_03_HandleMenuControlInput; CFEPMultiplayerStart__SubObj8848__ctor; CFEPDirectory__RefreshSaveFileList; CFEPWingmen__Update; CText__GetLanguageName; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`.

Accounting boundary: the legacy additive counter is deprecated. After Wave1201 it would read `1073/1179`, but that includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-235230_post_wave1201_frontend_text_menu_current_risk_review_verified`.

Active measurement files:

- `reverse-engineering/binary-analysis/static-reaudit-current-risk-ledger.json`
- `reverse-engineering/binary-analysis/static-reaudit-progress.json`
- `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`
- `reverse-engineering/binary-analysis/mapped-systems.md`

Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Boundary: static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime frontend behavior, runtime text rendering, visual parity, exact layouts, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

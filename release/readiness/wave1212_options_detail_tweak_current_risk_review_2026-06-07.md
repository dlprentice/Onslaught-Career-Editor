# Wave1212 Options Detail/Tweak Current-Risk Review Readiness Note

Status: complete static current-risk read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Scope: `wave1212-options-detail-tweak-current-risk-review`

Wave1212 re-read `9 options/detail/tweak current-risk rows` with fresh Ghidra export evidence: `LandscapeDetail_SetLevel`, `LandscapeDetail_GetLevel`, `CTreeDetail__SetQualityLevel`, `CMouseSensitivityMenuItem__scalar_deleting_dtor`, `CMultiSample__GetSampleCountLabel`, `CReconnectInterface__VFunc_07_00527d00`, `CTweak__ctor_base`, `CTweak__dtor_base`, and `CTweak__dtor_base_thunk_004530a0`.

Evidence:

- Fresh Ghidra export: `64 xref rows`, `175 instruction rows`, and `9 decompile rows`.
- Context export: `869 context xref rows`, `1887 context instruction rows`, and `7 context decompile rows`.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`.
- Active current-risk progress uses unique-address accounting and is `1119/1179 = 94.91%`; remaining active focused work: 60.
- legacy additive counter is deprecated (`1150/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- current-risk denominator, continuity denominator, focused threshold `15`, and `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence` remain the active measured lane.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `G:\GhidraBackups\BEA_20260607-065722_post_wave1212_options_detail_tweak_current_risk_review_verified`.

Mutation status: read-only review; no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, and `wave1108-current-risk-rank`.

Boundary: this is static Ghidra evidence for rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime options-menu behavior, runtime CLI/tweak behavior, runtime device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

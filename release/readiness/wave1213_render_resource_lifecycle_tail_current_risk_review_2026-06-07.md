# Wave1213 Render Resource Lifecycle Tail Current-Risk Review Readiness Note

Status: complete static current-risk read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Scope: `wave1213-render-resource-lifecycle-tail-current-risk-review`

Wave1213 re-read `6 render-resource lifecycle tail current-risk rows` with fresh Ghidra export evidence: `CIBuffer__CreateConfigured`, `CIBuffer__LockDirect`, `CDXSurf__UnlinkNodeFromGlobalList`, `CDXBattleLine__DestructorThunk`, `CDXLandscape__Destructor`, and `CDXLandscape__ReleaseBuffers`.

Evidence:

- Fresh Ghidra export: `13 xref rows`, `152 instruction rows`, and `6 decompile rows`.
- Context export: `41 context xref rows`, `1369 context instruction rows`, and `15 context decompile rows`.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`.
- Active current-risk progress uses unique-address accounting and is `1125/1179 = 95.42%`; remaining active focused work: 54.
- legacy additive counter is deprecated (`1156/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- current-risk denominator, continuity denominator, focused threshold `15`, and `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence` remain the active measured lane.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified`.

Mutation status: read-only review; no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting paths: `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `mesh-resource-render-static-contract.md`, and `wave1108-current-risk-rank`.

Boundary: this is static Ghidra evidence for rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime terrain/HUD output, runtime lost-device behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

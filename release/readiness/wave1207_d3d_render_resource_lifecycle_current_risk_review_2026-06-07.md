# Wave1207 D3D Render Resource Lifecycle Current-Risk Review Readiness Note

Status: complete static read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Scope: `wave1207-d3d-render-resource-lifecycle-current-risk-review`

Wave1207 measured anchor: unique-address accounting governs active current-risk progress. Wave1207 (`wave1207-d3d-render-resource-lifecycle-current-risk-review`) accounts for `6 D3D/render-resource lifecycle current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This read-only review made no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; no Cursor/Composer. Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0`; active current-risk progress is `1089/1179 = 92.37%`; remaining active focused work: 90; legacy additive counter is deprecated (`1120/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `36 xref rows`, `260 instruction rows`, and `6 decompile rows`. Anchors: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`. Active measurement files: `static-reaudit-current-risk-ledger.json`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/static-reaudit-measurement-register.md`, and `reverse-engineering/binary-analysis/wave1108-current-risk-rank.md`. Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`. Static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference. Runtime Direct3D behavior, runtime shader behavior, runtime render-resource behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Read-back evidence:

- Fresh Ghidra exports: 6 metadata rows, 6 tag rows, 36 xref rows, 260 instruction rows, and 6 decompile rows.
- Reviewed rows: `CVertexShader__scalar_deleting_dtor`, `CVertexShader__VFunc_02_00501a10`, `DeviceObject__dtor_body`, `DeviceObject__scalar_deleting_dtor`, `CDXMeshVB__scalar_deleting_dtor`, and `CDXMeshVB__dtor_base`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified`, 18 files, 176425863 bytes, `DiffCount=0`, `HashDiffCount=0`.
- Active accounting source: `static-reaudit-current-risk-ledger.json`, guarded by `static-reaudit-measurement-register.md` and `tools/static_reaudit_accounting_guard.py`.

What this proves:

- The six target rows exist in the saved Ghidra project with bounded static names/signatures/comments/tags.
- The D3D/render-resource lifecycle map now has fresh read-only evidence for CVertexShader destructor/vtable-slot handling, DeviceObject base teardown, and CDXMeshVB resource release/destructor wrapping.
- The active current-risk denominator advanced to `1089/1179 = 92.37%`, with remaining active focused work: 90.

What remains separate proof:

- Runtime Direct3D behavior.
- Runtime shader behavior.
- Runtime render-resource behavior.
- Exact layouts.
- Exact source identity.
- BEA patching behavior.
- Rebuild parity.
- No-noticeable-difference parity.

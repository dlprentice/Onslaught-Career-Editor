# Wave1182 CUnitAI VFunc Residual Current-Risk Readiness Note

Status: complete read-only static current-risk review; validated locally; artifact commit recorded
Date: 2026-06-06
Scope: `wave1182-cunitai-vfunc-residual-current-risk-review`

Wave1182 re-read 8 CUnitAI/shared-unit residual vfunc rows from the active Wave1108 current-risk denominator. It made no Ghidra mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Evidence:

- Fresh Ghidra exports: `8` metadata rows, `8` tag rows, `23 xref rows`, `88 instruction rows`, and `8` decompile rows.
- Logs: metadata `targets=8 found=8 missing=0`, tags `rows=8 missing=0`, xrefs `Wrote 23 rows`, instructions `Wrote 88 function-body instruction rows`, decompile `targets=8 dumped=8 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-115151_post_wave1182_cunitai_vfunc_residual_current_risk_review_verified`, `19` files, `176098183` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Accounting: `758/1179 = 64.29%`, current focused candidates: 1178, live regenerated current focused candidates: 1178, remaining active focused work: 421, current risk candidates: 6166.

Representative anchors:

- `CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0`
- `CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0`
- `CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0`
- `CUnitAIVFunc__ReturnFloat005d9434_00428c30`
- `CUnitAIVFunc__ReturnFloat005d8cb0_00428c40`
- `CUnitAIVFunc__ReturnField164_198Present_00428c50`
- `CUnitAIVFunc__CanDeployWhenField264Null_00428c90`
- `CUnitAIVFunc__CopyVector1cToOut_00428d30`

Consult/accounting boundary:

- Codex read-only consults used.
- One consult recommended exact eight-row CUnitAI vfunc slice; Codex root final judgment accepted that slice after fresh Ghidra evidence checks.
- A second consult recommended a PhysicsScript value-list/registry/lifetime slice; that is deferred as a future candidate.
- No Cursor/Composer used.

Boundary:

- Static clean-room target: rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference.
- Not proven here: exact source virtual names, concrete CUnitAI/shared-unit layouts, runtime AI/deploy/orientation/vector behavior, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1182; wave1182-cunitai-vfunc-residual-current-risk-review; 758/1179 = 64.29%; 8 CUnitAI vfunc residual current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 421; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; one consult recommended exact eight-row CUnitAI vfunc slice; PhysicsScript value-list/registry/lifetime slice deferred as future candidate; Codex root final judgment; no Cursor/Composer; shared unit-family vtable; CUnitAI vfunc residual; Wave1086; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 88 instruction rows; CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0; CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0; CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0; CUnitAIVFunc__ReturnFloat005d9434_00428c30; CUnitAIVFunc__ReturnFloat005d8cb0_00428c40; CUnitAIVFunc__ReturnField164_198Present_00428c50; CUnitAIVFunc__CanDeployWhenField264Null_00428c90; CUnitAIVFunc__CopyVector1cToOut_00428d30; [maintainer-local-ghidra-backup-root]\BEA_20260606-115151_post_wave1182_cunitai_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

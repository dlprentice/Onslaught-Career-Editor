# Wave1182 CUnitAI VFunc Residual Current-Risk Review

Status: complete read-only static current-risk review; validated locally; artifact commit recorded
Date: 2026-06-06
Scope tag: `wave1182-cunitai-vfunc-residual-current-risk-review`

Wave1182 accounts for `8 CUnitAI vfunc residual current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with a fresh serialized Ghidra export. This was a read-only review: no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Codex read-only consults used; one consult recommended the exact eight-row CUnitAI vfunc slice and Codex root accepted it after live evidence checks. A second consult recommended a PhysicsScript value-list/registry/lifetime slice; Codex root deferred that as a future candidate instead of mixing systems in this wave. No Cursor/Composer was used.

Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `758/1179 = 64.29%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 421; focused threshold `15`; not Wave911 reconstruction.

Fresh exports verified `8` metadata rows, `8` tag rows, `23 xref rows`, `88 instruction rows`, and `8` decompile rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-115151_post_wave1182_cunitai_vfunc_residual_current_risk_review_verified`.

## Reviewed Anchors

| Address | Anchor | Static evidence shape |
| --- | --- | --- |
| `0x004284f0` | `CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0` | Loads `this+0x40` and `this+0x50`, computes `FPATAN`, negates the result, returns a float, and has three DATA refs from shared unit-family vtable-like regions. |
| `0x004287c0` | `CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0` | Uses `this+0x26c` when non-null to dispatch vtable slot `+0x6c` with `outVector`; otherwise copies a 16-byte vector from `this+0x7c`; returns `outVector`; `RET 0x4`. |
| `0x00428be0` | `CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0` | Gates on flag byte `this+0x2c` mask `0x4`, compares three floats from current/target vectors, and calls `CUnit__SmoothEulerTowardTargetAndBuildMatrix` at `0x004fa4b0` when they differ; `RET 0x10`. |
| `0x00428c30` | `CUnitAIVFunc__ReturnFloat005d9434_00428c30` | Returns the float constant/data value at `0x005d9434`; DATA refs include the shared unit-family slot-103 region. |
| `0x00428c40` | `CUnitAIVFunc__ReturnFloat005d8cb0_00428c40` | Returns the float constant/data value at `0x005d8cb0`; DATA refs include the shared unit-family slot-75 region. |
| `0x00428c50` | `CUnitAIVFunc__ReturnField164_198Present_00428c50` | Loads `this+0x164`, tests nested field `+0x198`, returns `1` if present and `0` otherwise; DATA refs include the shared unit-family slot-74 region. |
| `0x00428c90` | `CUnitAIVFunc__CanDeployWhenField264Null_00428c90` | Returns `0` when `this+0x264` is non-null; otherwise tail-jumps to `CUnit__CanDeployNow` at `0x004fc000`; DATA refs include the shared unit-family slot-114 region. |
| `0x00428d30` | `CUnitAIVFunc__CopyVector1cToOut_00428d30` | Copies the 16-byte vector at `this+0x1c` into `outVector`; `RET 0x4`; DATA refs include the shared unit-family slot-120 region. |

## Boundary

This wave strengthens the CUnitAI/shared-unit vfunc static contract needed for rebuild-grade static contracts and a future clean-room implementation aiming at no noticeable difference from the original game. It does not prove exact source virtual names, concrete CUnitAI/shared-unit layouts, runtime AI/deploy/orientation/vector behavior, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, or no-noticeable-difference parity.

Probe token anchor: Wave1182; wave1182-cunitai-vfunc-residual-current-risk-review; 758/1179 = 64.29%; 8 CUnitAI vfunc residual current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 421; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; one consult recommended exact eight-row CUnitAI vfunc slice; PhysicsScript value-list/registry/lifetime slice deferred as future candidate; Codex root final judgment; no Cursor/Composer; shared unit-family vtable; CUnitAI vfunc residual; Wave1086; 0 / 0 / 0; 6411/6411 = 100.00%; 23 xref rows; 88 instruction rows; CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0; CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0; CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0; CUnitAIVFunc__ReturnFloat005d9434_00428c30; CUnitAIVFunc__ReturnFloat005d8cb0_00428c40; CUnitAIVFunc__ReturnField164_198Present_00428c50; CUnitAIVFunc__CanDeployWhenField264Null_00428c90; CUnitAIVFunc__CopyVector1cToOut_00428d30; [maintainer-local-ghidra-backup-root]\BEA_20260606-115151_post_wave1182_cunitai_vfunc_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

# Ghidra CUnitAI Deploy State Review Wave928 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `cunitai-deploy-state-review-wave928`

Wave928 re-reviewed five Wave911 focused CUnitAI deploy/lifecycle candidates, plus one context helper from Wave525. The review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00415140 CUnitAI__HandleLandedStateTransition` | `void __fastcall CUnitAI__HandleLandedStateTransition(void * unitAI)` | DATA slot xref `0x005e2400`; decompile emits the `landed` trace once, clears `unitAI+0x12c`, dispatches vfunc slots `+0x110/+0x100` and optional `+0x148`, then sets landed flag `+0x264` to `1`. |
| `0x00415780 CUnitAI__PlayDeployingAnimationIfState0` | `void __fastcall CUnitAI__PlayDeployingAnimationIfState0(void * unitAI)` | DATA slot xref `0x005e23d4`; decompile plays `deploying` through vfunc slot `+0xf0` only when deploy state `+0x260` is `0`, then advances `+0x260` to `1`. |
| `0x004157c0 CUnitAI__PlayUndeployingAnimation` | `void __fastcall CUnitAI__PlayUndeployingAnimation(void * unitAI)` | DATA slot xref `0x005e23d8`; decompile clears field `+0x1f0`, resolves `undeploying`, and dispatches the animation index through vfunc slot `+0xf0`. |
| `0x00415970 CUnitAI__HandleDeployUndeployAnimationCompletion` | `int __fastcall CUnitAI__HandleDeployUndeployAnimationCompletion(void * unitAI)` | DATA slot xref `0x005e2378`; decompile compares current animation index with `deploying` and `undeploying`, plays `deployed` or `normal`, updates `+0x1f0` or `+0x260`, and otherwise falls back to `CUnitAI__HandleDeployAndFireAnimationCompletion`. |
| `0x00415a50 CUnitAI__CanCompleteDeployUndeployTransition` | `int __fastcall CUnitAI__CanCompleteDeployUndeployTransition(void * unitAI)` | DATA slot xref `0x005e23bc`; decompile blocks while vfunc `+0x10c` is active, then checks gates at `+0x168`, `+0x214`, and flag byte `+0x2c`. |

Context helper:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x004fdeb0 CUnitAI__HandleDeployAndFireAnimationCompletion` | `int __fastcall CUnitAI__HandleDeployAndFireAnimationCompletion(void * this)` | Context export confirms the Wave525 completion helper called from `0x00415a30 CUnitAI__HandleDeployUndeployAnimationCompletion`; decompile uses the separate `+0x244` state for deploying/undeploying/prefire/firing/postfire completion paths. |

Evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 5 xref rows, 168 instruction rows, and 5 decompile rows.
- Context export: 1 metadata row, 1 tag row, 21 xref rows, 144 instruction rows, and 1 decompile row.
- Wave911 focused re-audit progress after Wave928: `108/1408 = 7.67%`; the context helper is not counted against that progress denominator.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260527-225215_post_wave928_cunitai_deploy_state_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, slot xrefs, instruction bodies, and decompiles for these five deploy/lifecycle rows remain internally consistent with prior Wave311 bounded claims.
- `0x00415140` remains a landing lifecycle helper, not a deploy-animation helper.
- `+0x260` deploy state and context-helper `+0x244` animation-completion state remain distinct in fresh decompile evidence.

What remains unproven:

- Runtime deploy/undeploy AI timing or behavior.
- Exact `CUnitAI` field names/layout and animation table structure.
- Exact source-body identity or source method names.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

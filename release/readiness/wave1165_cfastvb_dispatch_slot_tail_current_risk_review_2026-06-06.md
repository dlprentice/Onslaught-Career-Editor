# Wave1165 CFastVB Dispatch-Slot Tail Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Scope: `wave1165-cfastvb-dispatch-slot-tail-current-risk-review`

Wave1165 accounts for `21 CFastVB dispatch-slot tail current-risk rows` from the active `wave1108-current-risk-rank` denominator. Fresh Ghidra read-back verified the saved Wave971 CFastVB dispatch-slot boundary treatment for slot offsets `0x04`, `0x08`, `0x10`, `0x20`, `0x30`, `0x34`, `0x40`, `0x44`, `0x48`, `0x58`, `0xa4`, `0xb8`, `0xbc`, `0xc0`, `0xc4`, `0xc8`, `0xcc`, `0xd0`, `0xd4`, `0xd8`, and `0xe4`.

The pass is read-only. It made no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005a77bc CFastVB__DispatchOp_SlotA4_005a77bc` | DATA xref from `CFastVB__InitDispatchOpsFromFeatureFlags` at `0x005985c2`; stack-locked `int(void)` signature preserved. |
| `0x005a923f CFastVB__DispatchOp_Slot10_005a923f` | DATA xref `0x00598658`; begins with `FEMMS`; stack-locked `int(void)` signature preserved. |
| `0x005a9abe CFastVB__DispatchOp_SlotCC_005a9abe` | DATA xref `0x005985f4`; stack-locked CFastVB dispatch-table body. |
| `0x005aa8c5 CFastVB__DispatchOp_SlotC0_005aa8c5` | DATA xref `0x005985fe`; stack-locked CFastVB dispatch-table body. |
| `0x005aac0f CFastVB__DispatchOp_SlotD8_005aac0f` | DATA xref `0x005985ea`; stack-locked CFastVB dispatch-table body. |
| `0x005aaf4d CFastVB__DispatchOp_Slot58_005aaf4d` | DATA xref `0x00598522`; stack-locked CFastVB dispatch-table body. |

Evidence:

- Fresh metadata rows: `21`
- Fresh tag rows: `21`
- Fresh xref rows: `21`
- Fresh instruction rows: `1417`
- Fresh decompile rows: `21`
- All xrefs are DATA refs from `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-040830_post_wave1165_cfastvb_dispatch_slot_tail_current_risk_review_verified`, `19` files, `176032647` bytes, `DiffCount=0`, `HashDiffCount=0`.

Accounting after Wave1165:

- Static function-quality closure remains `6411/6411 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave911 focused remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.
- Wave911 top-500 remains `500/500 = 100.00%`.
- Wave1108 current focused accounting is `604/1179 = 51.23%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 575.
- Focused threshold `15`; not Wave911 reconstruction.

Boundary:

This proves static Ghidra coherence for the saved dispatch-slot bodies and their dispatch-table DATA refs only. Exact dispatch-table slot schema, vector/quaternion/matrix layout, packed lane order, hidden MMX/SSE/register/stack ABI completeness, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1165; wave1165-cfastvb-dispatch-slot-tail-current-risk-review; 604/1179 = 51.23%; 21 CFastVB dispatch-slot tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 575; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 21 xref rows; 1417 instruction rows; CFastVB__DispatchOp_SlotA4_005a77bc; CFastVB__DispatchOp_Slot10_005a923f; CFastVB__DispatchOp_SlotCC_005a9abe; CFastVB__DispatchOp_SlotC0_005aa8c5; CFastVB__DispatchOp_SlotD8_005aac0f; CFastVB__DispatchOp_Slot58_005aaf4d; CFastVB__InitDispatchOpsFromFeatureFlags; [maintainer-local-ghidra-backup-root]\BEA_20260606-040830_post_wave1165_cfastvb_dispatch_slot_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

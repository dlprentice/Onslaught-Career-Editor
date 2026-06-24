# Ghidra CFastVB Dispatch Slot Boundary Sweep Wave971 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-28
Scope: `cfastvb-dispatch-slot-boundary-sweep-wave971`

Wave971 recovered twenty-eight previously non-function CFastVB dispatch-table targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. Mutation status: function-boundary recovery. The pass created function objects, saved conservative `int ...(void)` stack-locked signatures plus comments/tags, made no executable-byte change, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005a4fee CFastVB__DispatchOp_SlotB0_005a4fee` | DATA store `0x005985e0` into dispatch slot `+0xb0`; starts after `0x005a4feb RET 0x18`; first terminal `0x005a504f RET 0x8`. |
| `0x005a50f9 CFastVB__DispatchOp_SlotE0_005a50f9` | DATA store `0x00598630` into dispatch slot `+0xe0`; starts after `0x005a50f6 RET 0x8`; first terminal `0x005a519b RET 0x8`. |
| `0x005a5bd7 CFastVB__DispatchOp_Slot0C_005a5bd7` | DATA store `0x005984a4` into dispatch slot `+0x0c`; starts after `0x005a5bd4 RET 0x1c`; first terminal `0x005a5e06 RET 0x0c`. |
| `0x005a77bc CFastVB__DispatchOp_SlotA4_005a77bc` | DATA store `0x005985c2` into dispatch slot `+0xa4`; starts after `0x005a77b9 RET 0x10`; first terminal `0x005a7ced RET 0x14`. |
| `0x005a923f CFastVB__DispatchOp_Slot10_005a923f` | DATA store `0x00598658` into dispatch slot `+0x10`; starts after `0x005a923c RET 0x0c`; first terminal `0x005a945f RET 0x0c`. |
| `0x005aa5c0 CFastVB__DispatchOp_SlotE4_005aa5c0` | DATA store `0x00598673` into dispatch slot `+0xe4`; starts after `0x005aa5a7 RET 0x0c`; first terminal `0x005aa738 RET 0x0c`. |
| `0x005aaadd CFastVB__DispatchOp_Slot40_005aaadd` | DATA store `0x005984f8` into dispatch slot `+0x40`; starts after `0x005aaada RET 0x8`; first terminal `0x005aac0c RET 0x10`. |
| `0x005aaf4d CFastVB__DispatchOp_Slot58_005aaf4d` | DATA store `0x00598522` into dispatch slot `+0x58`; starts after `0x005aaf4a RET 0x10`; first terminal `0x005aafc5 RET 0x10`. |

Complete target set:

`0x005a4fee`, `0x005a50f9`, `0x005a5bd7`, `0x005a5e09`, `0x005a5ed8`, `0x005a5f28`, `0x005a6013`, `0x005a77bc`, `0x005a923f`, `0x005a996b`, `0x005a9987`, `0x005a9abe`, `0x005a9b2f`, `0x005a9c03`, `0x005aa5c0`, `0x005aa82d`, `0x005aa8c5`, `0x005aa90e`, `0x005aa951`, `0x005aa9fc`, `0x005aaa7e`, `0x005aaadd`, `0x005aac0f`, `0x005aac80`, `0x005aad48`, `0x005aae26`, `0x005aae69`, and `0x005aaf4d`.

Read-back evidence:

- `ApplyCFastVBDispatchSlotBoundarySweepWave971.java dry`: `updated=0 skipped=0 created=0 would_create=28 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- `ApplyCFastVBDispatchSlotBoundarySweepWave971.java apply`: `updated=28 skipped=0 created=28 would_create=0 renamed=0 would_rename=0 signature_updated=28 comment_only_updated=56 missing=0 bad=0`
- `ApplyCFastVBDispatchSlotBoundarySweepWave971.java final dry`: `updated=0 skipped=28 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Pre-evidence: 85 instruction rows from `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, 72 unique dispatch store targets, and 28 dry `would_create` rows.
- Post exports: 28 metadata rows, 28 tag rows, 28 xref rows, 1821 function-body instruction rows, and 28 decompile rows.
- Queue after Wave971: 6198 total functions, 6198 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, 0 uncertain-owner names, 0 address-suffixed helper names, and 0 address-suffixed wrapper names.
- Static closure: `6198/6198 = 100.00%`.
- Re-audit progress: Wave911 focused queue remains `344/1408 = 24.43%`; expanded static surface progress is `390/1454 = 26.82%`.
- Verified backup: `G:\GhidraBackups\BEA_20260528-181005_post_wave971_cfastvb_dispatch_slot_boundary_sweep_verified`, 19 files, 173706119 bytes, `DiffCount=0`.

What this proves:

- The 28 target addresses are saved Ghidra function entries with comments, tags, and conservative stack-locked `int ...(void)` signatures.
- The recovered rows are tied to direct DATA stores from `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`.
- Static queue closure remains complete after the recovered function objects were added.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector/quaternion/matrix layouts and packed lane order.
- Hidden MMX/SSE/register ABI completeness.
- Exact source identity.
- Runtime CPU dispatch/math/render behavior.
- BEA patching behavior.
- Rebuild parity.

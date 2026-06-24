# Wave1119 Mixed Score-26 Current-Risk Review

Status: validated static read-only evidence
Date: 2026-06-05
Tag: `wave1119-mixed-score26-current-risk-review`

Wave1119 accounts for `10 rows` from the Wave1108 current focused denominator as the score-26 mixed current-risk head, moving current focused accounting to `110/1179 = 9.33%` of current focused candidates: 1179. The wave used a fresh read-only Ghidra export and no mutation.

Reviewed anchors:

| Address | Static read-back evidence |
| --- | --- |
| `0x004d05e0 CPauseMenu__dtor_base` | Scalar-deleting destructor caller `0x004d04b3`; restores pause-menu vtable state, clears child/menu pointer sets, releases pause textures and the shared blank texture, and calls `CMonitor__Shutdown`. |
| `0x004d0e40 CGameMenu__InitBase` | `CPauseMenu__ButtonPressed` caller `0x004d0917`; compact base initializer clears `game_menu+0x04` and installs `PTR_SharedVFunc__NoOpOneArg_004014c0_005dc72c` before range/action setup. |
| `0x004d1750 CSimpleGameMenu__dtor_base` | Scalar-deleting destructor caller `0x004d1733`; releases active-reader nodes from the `+0x3c` set, clears range state, destroys the embedded `CMenuItemRange`, and shuts down the monitor base. |
| `0x004d3020 CEngine__SetOptionValueAndNotifyTarget` | Menu/game callers plus raw no-function callers; stores the option at `this+0x20`, mirrors through the `0x00662ab0` indexed global dword array, and notifies the optional target through vfunc slots `+0xe0` and `+0x154`. |
| `0x004d6d10 CRepairPadAI__VFunc_11_UpdateDockCandidateReader` | DATA xref `0x005d8e34` from CRepairPadAI vtable `0x005d8e08` slot 11; clears the active-reader cell, scans `CMapWho` with radius `8.0`, filters compatible dock candidates, and stores the accepted reader. |
| `0x004de1d0 CSafeSide__ShutdownAndUnlinkFactionAnchor` | DATA xref `0x005dcce4`; removes this object from `DAT_00855160` through `CSPtrSet__Remove` before forwarding to `CComplexThing__Shutdown`. |
| `0x004fc3c0 SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0` | Broad unit-family vtable DATA refs; checks a candidate against the `this+0x17c` list and falls back to attachment/origin and orientation-matrix copy helpers when no cached vector context applies. |
| `0x0050ee90 CUnit__scalar_deleting_dtor` | Multiple unit-family vtable DATA refs including `0x005dfd40`; calls `CUnit__dtor_base_Thunk_004bfe00`, conditionally frees `this` through `CDXMemoryManager__Free`, returns `this`, and ends with `RET 0x4`. |
| `0x005b85c0 Math__Atan2ApproxPacked` | Called by `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`; remains a packed hidden-MM0/MM1 ABI helper with intentionally retained stale EAX-style return until register contract proof exists. |
| `0x005b86c0 CFastVB__FastAcosApprox_Scalar` | Called by axis-angle extraction, quaternion normalization fallback, and spline blending paths; remains a hidden-MM0 packed/scalar helper with intentionally retained stale EAX-style return until register contract proof exists. |

Fresh export evidence:

- Metadata: `10` rows, `targets=10 found=10 missing=0`.
- Tags: `10` rows, `missing=0`.
- Xrefs: `67` rows.
- Instructions: `1170` rows, `targets=10 missing=0`.
- Decompile: `10` rows, `targets=10 dumped=10 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-021103_post_wave1118_particle_message_current_risk_review_verified`.

Boundary:

This is static read-only Ghidra/source-reference evidence. It does not prove runtime UI behavior, runtime repair behavior, runtime faction-anchor behavior, runtime unit behavior, runtime math behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

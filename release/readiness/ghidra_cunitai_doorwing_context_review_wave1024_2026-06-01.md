# Ghidra CUnitAI Door-Wing Context Review Wave1024 Readiness Note

Status: complete read-only static review
Date: 2026-06-01
Scope: `cunitai-doorwing-context-review-wave1024`

Wave1024 re-read eight CUnitAI door-wing engagement and cached-anchor context rows as primary targets after Wave929/Wave930 had used them as context. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)` | No-function parent dispatch call at `0x00445a8e`; calls open/close animation helpers and attached-node readiness forwarding. |
| `0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)` | No-function parent dispatch call at `0x00445a85`; xref to `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` keeps attached-node forwarding under CUnit ownership. |
| `0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)` | No-function parent dispatch call at `0x00445a7c`; calls `CUnitAI__EnterDoorWingOpenTrackingState` and the CUnit attached-node vfunc `+0x1c` forwarder. |
| `0x00446400 CUnitAI__EnterDoorWingOpenTrackingState` | `void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)` | Reached from long-range engagement; sets open-tracking state, calls `CUnitAI__PlayOpenAnimationIfState1Or3`, and checks attached-node readiness. |
| `0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | `void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)` | DATA vtable xref `0x005e1fb8`; resolves `0x00628ab0` (`wingunfolded`), dispatches animation vfunc `+0xf0`, writes door-wing state `+0x27c = 5`, and removes the unit from occupancy. |
| `0x00447b60 CUnitAI__HasReachedCachedAnchorPoint` | `int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)` | Call xref from `0x00448580 CDropshipAI__VFunc_09_00448580`; checks cached-anchor flag `+0x290` and compares current X/Y against cached `+0x280/+0x284`. |
| `0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint` | `void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)` | Call xref from `0x00448580`; preserves the one-stack-argument `RET 0x4` shape and calls `CUnitAI__IsCachedAnchorPointValid`. |
| `0x00447d50 CUnitAI__IsCachedAnchorPointValid` | `int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)` | Call xrefs from `0x00447a40` and `0x00447bb0`; validates anchors through CMapWho/static-shadow/occupancy context. |

Comparison and context evidence:

- Comparison exports covered `0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3`, `0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2`, `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState`, `0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta`, `0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3`, `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState`, `0x004480c0 CUnitAI__CanContinueDoorWingTransition`, `0x00448110 CUnitAI__SetDoorWingState6`, and `0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset`.
- CUnit attached-node context exports covered `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` and `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent`.
- Dispatch instruction-window export covered `0x00445a7c`, `0x00445a85`, and `0x00445a8e`, all still in `<no_function>` parent bytes. Wave1024 did not create or adjust function boundaries there.
- Vtable export covered 512 rows across `0x005e11b0` and `0x005e1e7c`, keeping `0x00445610` at `0x005e11b0` slot `94`, `0x00447fa0` at `0x005e1e7c` slot `18`, and `0x00447b10` at `0x005e1e7c` slot `79`.
- String dumps verified `0x00623bb4=open`, `0x006289e4=close`, and `0x00628ab0=wingunfolded`.

Evidence counts:

- Primary exports: 8 metadata rows, 8 tag rows, 10 xref rows, 1093 body-instruction rows, and 8 decompile rows.
- Comparison exports: 9 metadata rows, 9 tag rows, 11 xref rows, 317 body-instruction rows, and 9 decompile rows.
- CUnit attached-node context exports: 2 metadata rows, 2 tag rows, 13 xref rows, 36 body-instruction rows, and 2 decompile rows.
- Dispatch instruction-window export: 69 instruction rows.
- Vtable export: 512 rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1024: `563/1408 = 39.99%`; expanded static surface progress: `792/1493 = 53.05%`; Wave911 top-500 risk-ranked coverage: `491/500 = 98.20%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-001008_post_wave1024_cunitai_doorwing_context_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, strings, vtable slots, and decompiles for the eight promoted context rows remain internally coherent with the Wave929/Wave930 door-wing split.
- The `+0x280` evidence remains address-qualified: Wave929 comparison row `0x00445610` uses it as open/close/shoot animation state, while Wave1024 cached-anchor rows use `+0x280/+0x284` as cached coordinates.
- The broader `+0x27c` door-wing state lane remains separate from the `+0x280` open/close/shoot helper lane.
- The attached-node forwarders reached by the engagement helpers remain `CUnit__` helpers, not CUnitAI-owned functions.

What remains unproven:

- Runtime door-wing targeting, animation, movement, or cached-anchor behavior.
- Exact `CUnitAI` or `CUnit` field names/layout beyond observed address-qualified offsets.
- Exact source-body identity or source method names.
- A unified runtime FSM across the `+0x280` and `+0x27c` lanes.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

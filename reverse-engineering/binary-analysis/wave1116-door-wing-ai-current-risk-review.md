# Wave1116 Door-Wing AI Current-Risk Review

Status: complete static read-only Ghidra review
Last updated: 2026-06-05
Scope: `wave1116-door-wing-ai-current-risk-review`

Wave1116 re-read `21 rows` from the Wave1108 current focused denominator: the score-26 PhysicsRoundValue plus door-wing AI head immediately after Wave1115. This wave uses a fresh read-only Ghidra export and a verified Ghidra project backup. It made no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6410/6410 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave1108 current focused candidates | current focused candidates: 1179 |
| Wave1116 current focused review accounting | `77/1179 = 6.53%` |

## Reviewed Rows

| Address | Saved row | Fresh read-back evidence |
| --- | --- | --- |
| `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08` | `void __thiscall CPhysicsRoundValue__SetOwnedValueStringAt08(void * this, char * sourceString)` | Call xref `0x00437f5f`; frees `this+0x8` and copies `sourceString` into the owned round-value string slot. |
| `0x004453a0 CDiveBomberAI__dtor_base` | `void __fastcall CDiveBomberAI__dtor_base(void * this)` | Call xref from scalar-deleting dtor; removes tracked entries at `+0x28/+0x24/+0x0c` and calls `CMonitor__Shutdown`. |
| `0x00445460 CDiveBomberGuide__dtor_base` | `void __fastcall CDiveBomberGuide__dtor_base(void * this)` | Call xref from scalar-deleting dtor; removes tracked entry `+0x2c` and calls `CMonitor__Shutdown`. |
| `0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3` | `void __fastcall CUnitAI__PlayOpenAnimationIfState1Or3(void * unitAI)` | Close-range/open-tracking callers; checks state `+0x280` and dispatches the open animation through vfunc `+0xf0`. |
| `0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2` | `void __fastcall CUnitAI__PlayCloseAnimationIfState0Or2(void * unitAI)` | Close/long-range callers; checks state `+0x280` and dispatches the close animation through vfunc `+0xf0`. |
| `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState` | `int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)` | DATA xref `0x005e1328`; compares animation state, resolves shoot/close/open-style tokens, and updates state `+0x280`. |
| `0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_CloseRange(void * doorWingAI)` | Calls open/close helpers, updates tracking flags `+0x64/+0x68`, threshold `+0x70`, and movement vfunc `+0xf4`. |
| `0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_MidRange(void * doorWingAI)` | Samples attached target/weapon context, toggles `+0x6c`, and can dispatch movement vfunc `+0xf4`. |
| `0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange` | `double __fastcall CUnitAI__UpdateDoorWingEngagement_LongRange(void * doorWingAI)` | Evaluates target distance/state and calls `CUnitAI__EnterDoorWingOpenTrackingState` or close-animation paths. |
| `0x00446400 CUnitAI__EnterDoorWingOpenTrackingState` | `void __fastcall CUnitAI__EnterDoorWingOpenTrackingState(void * doorWingAI)` | Sets `+0x68`, randomizes threshold `+0x70`, and calls `CUnitAI__PlayOpenAnimationIfState1Or3`. |
| `0x00447060 CDropshipAI__dtor_base` | `void __fastcall CDropshipAI__dtor_base(void * this)` | Call xref from scalar-deleting dtor; removes tracked entries at `+0x28/+0x24/+0x0c` and calls `CMonitor__Shutdown`. |
| `0x00447100 CDropship__dtor_base` | `void __fastcall CDropship__dtor_base(void * this)` | DATA xref `0x005e1de0`; removes the unit from occupancy through `CWorld__RemoveUnitFromOccupancyGrid_Thunk` and calls `CAirUnit__dtor_base`. |
| `0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta` | `void __fastcall CUnitAI__SetDoorWingState2AndClampYawDelta(void * unitAI)` | DATA xref `0x005e1fb0`; validates cached anchor fields `+0x290/+0x294`, sets state `+0x27c` to `2`, and clamps yaw delta into `+0x2a0`. |
| `0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3` | `void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * unitAI)` | DATA xref `0x005e1fb4`; resolves `wingfolded`, sets state `+0x27c` to `3`, and adds the unit back to occupancy/shadow state. |
| `0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | `void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)` | DATA xref `0x005e1fb8`; resolves `wingunfolded`, sets state `+0x27c` to `5`, and removes the unit from occupancy. |
| `0x00447b60 CUnitAI__HasReachedCachedAnchorPoint` | `int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)` | Call xref from `CDropshipAI__VFunc_09_00448580`; checks cached anchor flag `+0x290` and compares current X/Y against `+0x280/+0x284`. |
| `0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint` | `void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)` | Call xref from `CDropshipAI__VFunc_09_00448580`; writes `outAnchorPoint`, seeds cached anchor fields `+0x280/+0x28c`, and calls `CUnitAI__IsCachedAnchorPointValid`. |
| `0x00447d50 CUnitAI__IsCachedAnchorPointValid` | `int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)` | Call xrefs from state/anchor helpers; queries `CMapWho`, checks collision/height context, and scans the occupancy bitmask when states are not `2` or `3`. |
| `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` | `int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)` | DATA xref `0x005e1ec4`; recognizes `dooropening`, `doorclosing`, `wingfolded`, and `wingunfolded` animation states. |
| `0x00448110 CUnitAI__SetDoorWingState6` | `void __fastcall CUnitAI__SetDoorWingState6(void * unitAI)` | Call xref from `CDropshipAI__VFunc_09_00448580`; writes state `+0x27c` to `6`. |
| `0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset` | `void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(void * unitAI)` | Call xref from `CDropshipAI__VFunc_09_00448580`; writes state `+0x27c` to `7` and mirrors yaw/offset field `+0x2a4`. |

Read-back evidence:

- Fresh read-only exports: `21` metadata rows, `21` tag rows, `25` xref rows, `2037` instruction rows, and `21` decompile rows.
- Logs report `targets=21 found=21 missing=0`, `rows=21 missing=0`, `Wrote 25 rows`, `targets=21 missing=0`, and `targets=21 dumped=21 missing=0 failed=0`.
- Verified backup: `G:\GhidraBackups\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup was `G:\GhidraBackups\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified`.

Probe token anchor: Wave1116; wave1116-door-wing-ai-current-risk-review; 77/1179 = 6.53%; 21 rows; current focused candidates: 1179; score-26 PhysicsRoundValue plus door-wing AI head; fresh read-only Ghidra export; no mutation; 0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08; 0x004453a0 CDiveBomberAI__dtor_base; 0x00445460 CDiveBomberGuide__dtor_base; 0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3; 0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2; 0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState; 0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange; 0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange; 0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange; 0x00446400 CUnitAI__EnterDoorWingOpenTrackingState; 0x00447060 CDropshipAI__dtor_base; 0x00447100 CDropship__dtor_base; 0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta; 0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3; 0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5; 0x00447b60 CUnitAI__HasReachedCachedAnchorPoint; 0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint; 0x00447d50 CUnitAI__IsCachedAnchorPointValid; 0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState; 0x00448110 CUnitAI__SetDoorWingState6; 0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset; G:\GhidraBackups\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified.

## Boundary

This wave closes current-risk accounting for these twenty-one rows only. It proves saved static Ghidra metadata/tag/xref/instruction/decompile read-back, not runtime AI behavior, runtime door-wing behavior, runtime dropship behavior, runtime PhysicsScript behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.

# Wave1116 Door-Wing AI Current-Risk Review Readiness Note

Status: complete static read-only Ghidra review
Date: 2026-06-05
Scope: `wave1116-door-wing-ai-current-risk-review`

Wave1116 accounts for `21 rows` from the Wave1108 current focused denominator as the score-26 PhysicsRoundValue plus door-wing AI head. This pass used a fresh read-only Ghidra export and verified backup. It made no mutation, no executable-byte change, no BEA launch, and no installed-game/runtime-file mutation.

Accounting after Wave1116:

- Static Ghidra function-quality closure: `6410/6410 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave1108 current focused candidates: current focused candidates: 1179.
- Wave1108 current focused accounting: `77/1179 = 6.53%`.

Representative anchors:

| Address | Fresh read-back evidence |
| --- | --- |
| `0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08` | Call xref `0x00437f5f`; frees `this+0x8` and copies `sourceString` into the owned round-value string slot. |
| `0x004453a0 CDiveBomberAI__dtor_base` | Scalar-deleting dtor caller; removes tracked entries at `+0x28/+0x24/+0x0c` and calls `CMonitor__Shutdown`. |
| `0x00445460 CDiveBomberGuide__dtor_base` | Scalar-deleting dtor caller; removes tracked entry `+0x2c` and calls `CMonitor__Shutdown`. |
| `0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3` | Door-wing state `+0x280` open-animation helper reached from engagement/open-tracking callers. |
| `0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2` | Door-wing state `+0x280` close-animation helper reached from engagement callers. |
| `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState` | DATA xref `0x005e1328`; resolves shoot/close/open-style animation names and updates state `+0x280`. |
| `0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange` | Close-range engagement helper with `+0x64/+0x68`, threshold `+0x70`, and movement vfunc `+0xf4`. |
| `0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange` | Mid-range engagement helper with attached target/weapon context, `+0x6c`, and movement vfunc `+0xf4`. |
| `0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange` | Long-range engagement helper calling `CUnitAI__EnterDoorWingOpenTrackingState` or close-animation paths. |
| `0x00446400 CUnitAI__EnterDoorWingOpenTrackingState` | Sets `+0x68`, randomizes threshold `+0x70`, and calls the open-animation helper. |
| `0x00447060 CDropshipAI__dtor_base` | Scalar-deleting dtor caller; removes tracked entries at `+0x28/+0x24/+0x0c` and calls `CMonitor__Shutdown`. |
| `0x00447100 CDropship__dtor_base` | DATA xref `0x005e1de0`; removes the unit from occupancy and calls `CAirUnit__dtor_base`. |
| `0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta` | DATA xref `0x005e1fb0`; validates cached anchor fields and writes state `+0x27c` to `2`. |
| `0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3` | DATA xref `0x005e1fb4`; resolves `wingfolded`, writes state `+0x27c`, and restores occupancy/shadow state. |
| `0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | DATA xref `0x005e1fb8`; resolves `wingunfolded`, writes state `+0x27c`, and removes occupancy. |
| `0x00447b60 CUnitAI__HasReachedCachedAnchorPoint` | Dropship AI caller; checks cached anchor flag `+0x290` against cached X/Y fields. |
| `0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint` | Dropship AI caller; writes `outAnchorPoint`, seeds cached anchor fields, and validates them. |
| `0x00447d50 CUnitAI__IsCachedAnchorPointValid` | Queries `CMapWho`, checks collision/height context, and scans an occupancy bitmask. |
| `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` | DATA xref `0x005e1ec4`; recognizes `dooropening`, `doorclosing`, `wingfolded`, and `wingunfolded`. |
| `0x00448110 CUnitAI__SetDoorWingState6` | Dropship AI caller; writes state `+0x27c` to `6`. |
| `0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset` | Dropship AI caller; writes state `+0x27c` to `7` and mirrors yaw/offset field `+0x2a4`. |

Read-back evidence:

- Fresh exports: `21` metadata rows, `21` tag rows, `25` xref rows, `2037` instruction rows, and `21` decompile rows.
- Export logs: `targets=21 found=21 missing=0`; `rows=21 missing=0`; `Wrote 25 rows`; `targets=21 missing=0`; `targets=21 dumped=21 missing=0 failed=0`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified`, `19` files, `175541127` bytes, `DiffCount=0`.
- Previous latest completed Ghidra review backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified`.

Probe token anchor: Wave1116; wave1116-door-wing-ai-current-risk-review; 77/1179 = 6.53%; 21 rows; current focused candidates: 1179; score-26 PhysicsRoundValue plus door-wing AI head; fresh read-only Ghidra export; no mutation; 0x00438050 CPhysicsRoundValue__SetOwnedValueStringAt08; 0x004453a0 CDiveBomberAI__dtor_base; 0x00445460 CDiveBomberGuide__dtor_base; 0x00445570 CUnitAI__PlayOpenAnimationIfState1Or3; 0x004455c0 CUnitAI__PlayCloseAnimationIfState0Or2; 0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState; 0x00445ad0 CUnitAI__UpdateDoorWingEngagement_CloseRange; 0x00445f40 CUnitAI__UpdateDoorWingEngagement_MidRange; 0x00446150 CUnitAI__UpdateDoorWingEngagement_LongRange; 0x00446400 CUnitAI__EnterDoorWingOpenTrackingState; 0x00447060 CDropshipAI__dtor_base; 0x00447100 CDropship__dtor_base; 0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta; 0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3; 0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5; 0x00447b60 CUnitAI__HasReachedCachedAnchorPoint; 0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint; 0x00447d50 CUnitAI__IsCachedAnchorPointValid; 0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState; 0x00448110 CUnitAI__SetDoorWingState6; 0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset; [maintainer-local-ghidra-backup-root]\BEA_20260605-011935_post_wave1116_door_wing_ai_current_risk_review_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-010428_post_wave1115_unitai_carver_motion_activation_current_risk_review_verified.

Boundary: this is static read-only Ghidra evidence only. Runtime AI behavior, runtime door-wing behavior, runtime dropship behavior, runtime PhysicsScript behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.

# Ghidra CUnitAI Door-Wing State Review Wave930 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `cunitai-doorwing-state-review-wave930`

Wave930 re-reviewed five Wave911 focused CUnitAI `+0x27c` door-wing state candidates, plus five adjacent context helpers and one comparison target. The review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00447a40 CUnitAI__SetDoorWingState2AndClampYawDelta` | `void __fastcall CUnitAI__SetDoorWingState2AndClampYawDelta(void * unitAI)` | DATA xref `0x005e1fb0`; decompile gates on `+0x290/+0x294`, calls `CUnitAI__IsCachedAnchorPointValid`, writes state field `+0x27c = 2`, and clamps yaw delta into `+0x2a0`. |
| `0x00447ac0 CUnitAI__PlayWingFoldedAnimationAndSetState3` | `void __fastcall CUnitAI__PlayWingFoldedAnimationAndSetState3(void * unitAI)` | DATA xref `0x005e1fb4`; decompile writes `+0x27c = 3`, clears `+0x290`, re-adds occupancy/shadow state, resolves `0x00628aa4` (`wingfolded`), and dispatches animation vfunc `+0xf0`. |
| `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` | `int __fastcall CUnitAI__AdvanceDoorWingAnimationState(void * unitAI)` | DATA xref `0x005e1ec4`; vtable export places this at `0x005e1e7c` slot `18`. Decompile recognizes `dooropening`, `doorclosing`, `doorclosed`, `wingfolded`, `wingunfolded`, `wingflat`, and `dooropen`, dispatches animation vfunc `+0xf0`, and writes state field `+0x27c`. |
| `0x00448110 CUnitAI__SetDoorWingState6` | `void __fastcall CUnitAI__SetDoorWingState6(void * unitAI)` | Call xref `0x004486dc`; two-instruction narrow writer for `+0x27c = 6`. |
| `0x00448120 CUnitAI__SetDoorWingState7AndMirrorYawOffset` | `void __fastcall CUnitAI__SetDoorWingState7AndMirrorYawOffset(void * unitAI)` | Call xref `0x00448737`; writes `+0x27c = 7` and mirrors yaw/offset field `+0x2a4` around the `0x005d8568` constant. |

Context helpers:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00447b10 CUnitAI__PlayWingUnfoldedAnimationAndSetState5` | `void __fastcall CUnitAI__PlayWingUnfoldedAnimationAndSetState5(void * unitAI)` | DATA xref `0x005e1fb8`; counterpart to the folded helper, resolves `0x00628ab0` (`wingunfolded`), dispatches vfunc `+0xf0`, writes `+0x27c = 5`, and removes the unit from the occupancy grid. |
| `0x00447b60 CUnitAI__HasReachedCachedAnchorPoint` | `int __fastcall CUnitAI__HasReachedCachedAnchorPoint(void * unitAI)` | Call xref `0x0044866d`; checks cached-anchor flag `+0x290` and compares current XY against cached `+0x280/+0x284`. |
| `0x00447bb0 CUnitAI__GetOrGenerateCachedAnchorPoint` | `void __thiscall CUnitAI__GetOrGenerateCachedAnchorPoint(void * this, void * outAnchorPoint)` | Call xref `0x00448690`; uses the `RET 0x4` out-anchor pointer, seeds/regenerates cached anchor fields `+0x280/+0x284/+0x290`, and calls `CUnitAI__IsCachedAnchorPointValid`. |
| `0x00447d50 CUnitAI__IsCachedAnchorPointValid` | `int __fastcall CUnitAI__IsCachedAnchorPointValid(void * unitAI)` | Call xrefs from `0x00447a57`, `0x00447c3d`, and `0x00447cf7`; validates anchors through CMapWho, static-shadow height, and occupancy checks. |
| `0x004480c0 CUnitAI__CanContinueDoorWingTransition` | `bool __fastcall CUnitAI__CanContinueDoorWingTransition(void * unitAi)` | Call xref `0x004486bf`; transition predicate context for `+0x294` and spawned-child/target fireability checks. |

Comparison target:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState` | `int __fastcall CUnitAI__AdvanceOpenCloseShootAnimationState(void * unitAI)` | DATA xref `0x005e1328`; vtable export places this at `0x005e11b0` slot `94`, separate from `0x00447fa0` at `0x005e1e7c` slot `18`. Decompile uses the Wave929 `+0x280` open/close/shoot state lane and strings `open`, `close`, `shoot`, and `fly`. |

Evidence:

- Primary exports: 5 metadata rows, 5 tag rows, 5 xref rows, 164 instruction rows, and 5 decompile rows.
- Context exports: 5 metadata rows, 5 tag rows, 7 xref rows, 355 instruction rows, and 5 decompile rows.
- Comparison export: 1 metadata row, 1 tag row, 1 xref row, 73 instruction rows, and 1 decompile row for `0x00445610`.
- Vtable export: 256 rows across `0x005e11b0` and `0x005e1e7c`, including `0x00445610` at `0x005e11b0` slot `94`, `0x00447fa0` at `0x005e1e7c` slot `18`, `0x00447a40` at slot `77`, `0x00447ac0` at slot `78`, and `0x00447b10` at slot `79`.
- String dumps verified `0x00628a98=dooropening`, `0x00628a8c=doorclosing`, `0x00628a80=doorclosed`, `0x00628aa4=wingfolded`, `0x00628ab0=wingunfolded`, `0x00628a74=wingflat`, `0x00628ac0=dooropen`, plus comparison strings `open`, `close`, `shoot`, and `fly`.
- Wave911 focused re-audit progress after Wave930: `116/1408 = 8.24%`; context helpers are not counted against that progress denominator.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-233937_post_wave930_cunitai_doorwing_state_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, string literals, and decompiles for the five primary `+0x27c` door-wing state rows remain internally consistent with prior bounded claims.
- The cached-anchor helpers are adjacent context for the state lane, not counted as Wave930 primaries.
- `0x00447fa0 CUnitAI__AdvanceDoorWingAnimationState` has primary-tier Wave930 evidence and remains separate from the Wave929 `0x00445610 CUnitAI__AdvanceOpenCloseShootAnimationState` comparison row.
- The observed `+0x280` offset is address-qualified: Wave929 comparison uses it as open/close/shoot state in `0x00445610`, while Wave930 context rows use `+0x280/+0x284` as cached-anchor coordinates. Wave930 does not turn that into a final CUnitAI layout claim.

What remains unproven:

- Runtime door-wing behavior.
- Runtime targeting or movement outcomes.
- Exact `CUnitAI` field names/layout beyond observed address-qualified offsets.
- Exact source-body identity or source method names.
- A unified door-wing animation/state FSM spanning `0x00445610` and `0x00447fa0`.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
